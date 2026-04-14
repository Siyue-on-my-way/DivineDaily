"""占卜相关路由 - 异步任务模式"""

import json
from datetime import datetime, timezone
from typing import Optional, Any

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db, async_session_maker
from app.dependencies import get_current_user
from app.models.user import User
from app.models.divination import DivinationSession
from app.schemas.divination import CreateDivinationRequest, DivinationResult, DivinationTaskAccepted
from app.services.enhanced_divination_service import EnhancedDivinationService
from app.services.llm_service import create_llm_service
from app.repositories.llm_repository import LLMRepository
from app.repositories.divination_repository import DivinationRepository
from app.core.exceptions import BadRequestError, NotFoundError
from app.core.logger import get_logger

router = APIRouter()
logger = get_logger("api")


def _sanitize_result_for_json(value: Any) -> Any:
    """兜底 JSON 安全转换，避免不可序列化对象导致任务失败"""
    encoded = jsonable_encoder(value)
    try:
        # 二次保障：确认可被标准 JSON 序列化
        json.dumps(encoded)
        return encoded
    except TypeError:
        if isinstance(encoded, dict):
            sanitized: dict[str, Any] = {}
            for k, v in encoded.items():
                try:
                    json.dumps(v)
                    sanitized[k] = v
                except TypeError:
                    sanitized[k] = str(v)
            sanitized.setdefault("serialization_warning", "部分字段不可序列化，已降级为字符串")
            return sanitized
        return str(encoded)


def _normalize_outcome_label(raw: Optional[str]) -> Optional[str]:
    """将细粒度吉凶标签归一化为 吉/平/凶"""
    if not raw:
        return None

    text = str(raw).strip()
    if not text:
        return None

    positive_keywords = ["大吉", "中吉", "小吉", "末吉", "吉"]
    neutral_keywords = ["中平", "平", "尚可", "一般", "普通"]
    negative_keywords = ["大凶", "中凶", "小凶", "不利", "凶"]

    if any(k in text for k in positive_keywords):
        return "吉"
    if any(k in text for k in negative_keywords):
        return "凶"
    if any(k in text for k in neutral_keywords):
        return "平"

    return None


def _extract_session_outcome(session: DivinationSession) -> tuple[Optional[str], Optional[str]]:
    """为历史列表提取 outcome。

    Returns:
        (normalized_outcome, raw_outcome_label)
    """
    raw_outcome: Optional[str] = None

    # 1) 优先从结构化结果中读取顶层 outcome
    if isinstance(session.result_data, dict):
        outcome = session.result_data.get("outcome")
        if outcome:
            raw_outcome = str(outcome)

        # 2) 其次从 hexagram_info.outcome 读取
        if not raw_outcome:
            hexagram_info = session.result_data.get("hexagram_info")
            if isinstance(hexagram_info, dict):
                hex_outcome = hexagram_info.get("outcome")
                if hex_outcome:
                    raw_outcome = str(hex_outcome)

    # 3) 最后从摘要文本做弱推断（兼容历史旧数据）
    if not raw_outcome:
        summary = session.result_summary or ""
        if summary:
            raw_outcome = summary

    normalized = _normalize_outcome_label(raw_outcome)
    return normalized, raw_outcome


def _serialize_history_session(session: DivinationSession) -> dict[str, Any]:
    """历史列表序列化，补充前端所需字段"""
    payload = jsonable_encoder(session)
    normalized_outcome, raw_outcome = _extract_session_outcome(session)
    payload["outcome"] = normalized_outcome
    payload["outcome_label"] = raw_outcome
    return payload


async def _run_divination_task(session_id: str, request: CreateDivinationRequest):
    """后台执行占卜任务并回写 session 结果"""
    async with async_session_maker() as task_db:
        llm_service = None
        try:
            llm_repo = LLMRepository(task_db)
            llm_config = await llm_repo.get_default()

            if llm_config and llm_config.is_enabled:
                try:
                    llm_service = create_llm_service(llm_config)
                    logger.info("后台任务使用 LLM", extra={"session_id": session_id, "llm_name": llm_config.name})
                except Exception:
                    logger.warning("后台任务创建 LLM 服务失败", exc_info=True, extra={"session_id": session_id})
            else:
                logger.warning("后台任务未配置可用的 LLM，将使用基础占卜服务", extra={"session_id": session_id})

            service = EnhancedDivinationService(task_db, llm_service)
            result = await service.start_divination_with_enhancement(request)
            serializable_result = _sanitize_result_for_json(result)

            # 回写到预创建 session（避免内部新建 session_id 与外部不一致）
            session = await task_db.get(DivinationSession, session_id)
            if session:
                session.status = "completed"
                session.result_summary = serializable_result.get("summary")
                session.result_detail = serializable_result.get("detail")
                session.result_data = serializable_result
                await task_db.commit()

                summary_text = session.result_summary or ""
                detail_text = session.result_detail or ""
                logger.info(
                    "后台占卜任务完成",
                    extra={
                        "session_id": session_id,
                        "processing_type": serializable_result.get("processing_type"),
                        "fallback_used": bool(serializable_result.get("fallback_used", False)),
                        "degrade_reason": serializable_result.get("degrade_reason"),
                        "quality_level": (serializable_result.get("quality") or {}).get("level")
                        if isinstance(serializable_result.get("quality"), dict) else None,
                        "quality_score": (serializable_result.get("quality") or {}).get("score")
                        if isinstance(serializable_result.get("quality"), dict) else None,
                        "summary_len": len(summary_text),
                        "detail_len": len(detail_text),
                        "status": session.status,
                    },
                )
            else:
                await task_db.rollback()
                logger.error("后台占卜任务回写失败：session 不存在", extra={"session_id": session_id})

        except Exception as e:
            await task_db.rollback()
            logger.error("后台占卜任务失败", exc_info=True, extra={"session_id": session_id, "error": str(e)})

            # 标记为 failed，便于前端轮询结束
            try:
                failed_session = await task_db.get(DivinationSession, session_id)
                if failed_session:
                    failed_session.status = "failed"
                    failed_session.result_summary = "占卜处理失败，请稍后重试"
                    failed_session.result_detail = str(e)
                    failed_session.result_data = {
                        "error_code": "DIVINATION_TASK_FAILED",
                        "error_message": str(e),
                        "retryable": True,
                    }
                    await task_db.commit()
            except Exception:
                await task_db.rollback()
                logger.error("后台占卜任务失败状态回写失败", exc_info=True, extra={"session_id": session_id})
        finally:
            if llm_service and hasattr(llm_service, "close"):
                await llm_service.close()


@router.post("/start", response_model=DivinationTaskAccepted)
async def start_divination(
    request: CreateDivinationRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    开始占卜（异步任务模式）

    提交请求后立即返回 session_id 和 processing 状态，
    占卜与 LLM 增强在后台执行。
    """
    request.user_id = str(current_user.id)

    try:
        session_id = request.context.get("session_id") if request.context else None
        if not session_id:
            import uuid
            session_id = str(uuid.uuid4())

        # 预创建 session，立即返回，避免网关超时
        session = DivinationSession(
            id=session_id,
            user_id=request.user_id,
            version=request.version,
            question=request.question,
            event_type=request.event_type or "general",
            orientation=request.orientation,
            spread=request.spread,
            intent=request.intent,
            status="processing",
        )
        db.add(session)
        await db.flush()

        # 将 session_id 注入 context，后台任务可对齐写回
        merged_context = request.context or {}
        merged_context["session_id"] = session_id
        request.context = merged_context

        background_tasks.add_task(_run_divination_task, session_id, request)

        return DivinationTaskAccepted(
            accepted=True,
            session_id=session_id,
            status="processing",
            status_url=f"/api/v1/divinations/{session_id}",
            message="占卜任务已受理，正在处理中",
            created_at=datetime.now(timezone.utc),
        )
    except Exception as e:
        await db.rollback()
        logger.error("创建占卜任务失败", exc_info=True)
        raise HTTPException(status_code=500, detail=f"创建占卜任务失败: {str(e)}")


@router.get("/history")
async def list_divination_history(
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    event_type: Optional[str] = Query(None, description="事件类型过滤"),
    version: Optional[str] = Query(None, description="版本过滤"),
    status: Optional[str] = Query(None, description="状态过滤"),
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    order_by: str = Query("created_at", description="排序字段"),
    order_direction: str = Query("desc", description="排序方向 (asc/desc)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取占卜历史（增强版）

    支持过滤和排序：
    - event_type: 事件类型（decision/career/relationship/fortune/knowledge）
    - version: 版本（CN/Global/TAROT）
    - status: 状态（processing/completed/failed）
    - start_date: 开始日期（YYYY-MM-DD）
    - end_date: 结束日期（YYYY-MM-DD）
    - order_by: 排序字段（created_at/updated_at）
    - order_direction: 排序方向（asc/desc）
    """
    try:
        repo = DivinationRepository(db)

        # 解析日期
        start_dt = None
        end_dt = None
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format, use YYYY-MM-DD")

        if end_date:
            try:
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                end_dt = end_dt.replace(hour=23, minute=59, second=59)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format, use YYYY-MM-DD")

        sessions = await repo.get_user_sessions_with_filters(
            user_id=str(current_user.id),
            limit=limit,
            offset=offset,
            event_type=event_type,
            version=version,
            status=status,
            start_date=start_dt,
            end_date=end_dt,
            order_by=order_by,
            order_direction=order_direction,
        )

        total_count = await repo.count_user_sessions_with_filters(
            user_id=str(current_user.id),
            event_type=event_type,
            version=version,
            status=status,
            start_date=start_dt,
            end_date=end_dt,
        )

        return {
            "sessions": [_serialize_history_session(session) for session in sessions],
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total_count,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取历史失败: {str(e)}")


@router.get("/history/count")
async def get_history_count(
    event_type: Optional[str] = Query(None, description="事件类型过滤"),
    version: Optional[str] = Query(None, description="版本过滤"),
    status: Optional[str] = Query(None, description="状态过滤"),
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取占卜历史记录总数"""
    try:
        repo = DivinationRepository(db)

        start_dt = None
        end_dt = None
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format, use YYYY-MM-DD")

        if end_date:
            try:
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                end_dt = end_dt.replace(hour=23, minute=59, second=59)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format, use YYYY-MM-DD")

        count = await repo.count_user_sessions_with_filters(
            user_id=str(current_user.id),
            event_type=event_type,
            version=version,
            status=status,
            start_date=start_dt,
            end_date=end_dt,
        )

        return {"count": count}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计失败: {str(e)}")


@router.get("/stats")
async def get_divination_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取用户占卜统计数据（增强版）"""
    try:
        repo = DivinationRepository(db)
        stats = await repo.get_user_stats(str(current_user.id))
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计失败: {str(e)}")


@router.post("/{session_id}/save")
async def save_divination_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    兼容客户端“保存占卜”动作。

    目前占卜会话在 `/divinations/start` 时就会落库，因此这里只做归属校验并返回成功。
    """
    repo = DivinationRepository(db)
    session = await repo.get_session(session_id)
    if not session:
        raise NotFoundError("占卜会话不存在")

    if str(session.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="无权保存该会话")

    return {"ok": True, "message": "已保存"}


@router.get("/{session_id}", response_model=DivinationResult)
async def get_divination_result(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取占卜结果（兼容 processing/completed/failed）"""
    llm_repo = LLMRepository(db)
    llm_config = await llm_repo.get_default()

    llm_service = None
    if llm_config and llm_config.is_enabled:
        try:
            llm_service = create_llm_service(llm_config)
        except Exception:
            pass

    service = EnhancedDivinationService(db, llm_service)
    try:
        result = await service.get_result(session_id)

        if llm_service and hasattr(llm_service, "close"):
            await llm_service.close()

        return result
    except NotFoundError:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取占卜结果失败: {str(e)}")
