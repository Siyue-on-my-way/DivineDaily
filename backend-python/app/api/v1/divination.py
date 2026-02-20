"""占卜相关路由 - 增强版"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.divination import DivinationSession
from app.schemas.divination import CreateDivinationRequest, DivinationResult
from app.services.enhanced_divination_service import EnhancedDivinationService
from app.services.llm_service import create_llm_service
from app.repositories.llm_repository import LLMRepository
from app.repositories.divination_repository import DivinationRepository
from datetime import datetime
from typing import Optional

router = APIRouter()


@router.post("/start", response_model=DivinationResult)
async def start_divination(
    request: CreateDivinationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """开始占卜（使用增强服务，集成 LLM 智能分析）"""
    # 确保 user_id 与当前登录用户一致
    request.user_id = str(current_user.id)
    
    try:
        # 获取默认 LLM 配置
        llm_repo = LLMRepository(db)
        llm_config = await llm_repo.get_default()
        
        llm_service = None
        if llm_config and llm_config.is_enabled:
            try:
                llm_service = create_llm_service(llm_config)
                print(f"[INFO] 使用 LLM: {llm_config.name}")
            except Exception as e:
                print(f"[WARN] 创建 LLM 服务失败: {e}")
                # 降级：不使用 LLM
        else:
            print(f"[WARN] 未配置可用的 LLM，将使用基础占卜服务")
        
        # 使用增强占卜服务
        service = EnhancedDivinationService(db, llm_service)
        result = await service.start_divination_with_enhancement(request)
        await db.commit()
        
        # 关闭 LLM 连接
        if llm_service and hasattr(llm_service, 'close'):
            await llm_service.close()
        
        return result
    except Exception as e:
        await db.rollback()
        print(f"[ERROR] 占卜失败: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"占卜失败: {str(e)}")


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
    - status: 状态（pending/completed/failed）
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
                # 设置为当天的23:59:59
                end_dt = end_dt.replace(hour=23, minute=59, second=59)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format, use YYYY-MM-DD")
        
        # 获取历史记录
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
            order_direction=order_direction
        )
        
        # 获取总数
        total_count = await repo.count_user_sessions_with_filters(
            user_id=str(current_user.id),
            event_type=event_type,
            version=version,
            status=status,
            start_date=start_dt,
            end_date=end_dt
        )
        
        return {
            "sessions": sessions,
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total_count
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
    """
    获取占卜历史记录总数
    
    支持过滤条件，与 /history 接口的过滤参数一致
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
        
        # 获取总数
        count = await repo.count_user_sessions_with_filters(
            user_id=str(current_user.id),
            event_type=event_type,
            version=version,
            status=status,
            start_date=start_dt,
            end_date=end_dt
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
    """
    获取用户占卜统计数据（增强版）
    
    返回：
    - total_count: 总占卜次数
    - by_type: 按事件类型统计
    - by_version: 按版本统计
    - by_status: 按状态统计
    """
    try:
        repo = DivinationRepository(db)
        stats = await repo.get_user_stats(str(current_user.id))
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计失败: {str(e)}")


# 通配路由必须放在最后，否则会拦截所有请求
@router.get("/{session_id}", response_model=DivinationResult)
async def get_divination_result(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取占卜结果"""
    llm_repo = LLMRepository(db)
    llm_config = await llm_repo.get_default()
    
    llm_service = None
    if llm_config and llm_config.is_enabled:
        try:
            llm_service = create_llm_service(llm_config)
        except:
            pass
    
    service = EnhancedDivinationService(db, llm_service)
    try:
        result = await service.get_result(session_id)
        
        if llm_service and hasattr(llm_service, 'close'):
            await llm_service.close()
        
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"未找到占卜结果: {str(e)}")
