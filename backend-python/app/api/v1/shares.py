"""分享相关路由"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.divination import DivinationSession, DivinationResult
from app.models.share import DivinationShare
from app.repositories.share_repository import ShareRepository
from app.schemas.share import (
    ShareCreateRequest,
    ShareResponse,
    ShareContentResponse,
    ShareStatsResponse
)
from app.core.config import settings
from app.core.logger import get_logger

router = APIRouter()
logger = get_logger("share_api")


@router.post("/{session_id}/share", response_model=ShareResponse)
async def create_share(
    session_id: str,
    request: ShareCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建分享链接"""
    
    # 验证会话是否存在且属于当前用户
    result = await db.execute(
        select(DivinationSession).where(
            DivinationSession.id == session_id,
            DivinationSession.user_id == str(current_user.id)
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="占卜会话不存在"
        )
    
    # 检查是否已经创建过分享
    share_repo = ShareRepository(db)
    existing_shares = await share_repo.get_by_session_id(session_id)
    
    # 限制分享次数（可选）
    max_shares = 10
    if len(existing_shares) >= max_shares:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"每个占卜最多只能创建 {max_shares} 个分享链接"
        )
    
    # 创建分享记录
    share_url_base = getattr(settings, 'FRONTEND_URL', 'http://localhost:40080')
    
    share = await share_repo.create_share(
        session_id=session_id,
        share_url="",  # 先创建，后面更新
        expires_days=request.expires_days,
        is_public=request.is_public
    )
    
    # 更新完整的分享 URL
    share.share_url = f"{share_url_base}/share/{share.share_token}"
    await db.commit()
    
    logger.info("创建分享成功", extra={
        "session_id": session_id,
        "share_token": share.share_token,
        "user_id": str(current_user.id)
    })
    
    return ShareResponse(
        share_token=share.share_token,
        share_url=share.share_url,
        created_at=share.created_at,
        expires_at=share.expires_at
    )


@router.get("/{share_token}", response_model=ShareContentResponse)
async def get_share_content(
    share_token: str,
    db: AsyncSession = Depends(get_db)
):
    """获取分享内容（无需登录）"""
    
    # 获取分享记录
    share_repo = ShareRepository(db)
    share = await share_repo.get_by_token(share_token)
    
    if not share:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分享不存在"
        )
    
    # 检查是否过期
    if share.is_expired():
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="分享已过期"
        )
    
    # 检查是否公开
    if not share.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="分享已设为私密"
        )
    
    # 获取占卜会话
    session_result = await db.execute(
        select(DivinationSession).where(DivinationSession.id == share.session_id)
    )
    session = session_result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="占卜会话不存在"
        )
    
    # 获取占卜结果
    result_query = await db.execute(
        select(DivinationResult).where(DivinationResult.session_id == share.session_id)
    )
    divination_result = result_query.scalar_one_or_none()
    
    if not divination_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="占卜结果不存在"
        )
    
    # 增加浏览次数
    await share_repo.increment_view_count(share_token)
    await db.commit()
    
    # 构建响应
    result_data = {
        "title": divination_result.title,
        "outcome": divination_result.outcome,
        "summary": divination_result.summary,
        "detail": divination_result.detail,
        "hexagram_info": divination_result.hexagram_info,
        "cards": divination_result.cards,
        "daily_fortune": divination_result.daily_fortune
    }
    
    metadata = {
        "created_at": share.created_at.isoformat(),
        "view_count": share.view_count,
        "is_expired": share.is_expired()
    }
    
    logger.debug("获取分享内容", extra={
        "share_token": share_token,
        "view_count": share.view_count
    })
    
    return ShareContentResponse(
        share_token=share_token,
        question=session.question,
        result=result_data,
        metadata=metadata
    )


@router.post("/{share_token}/view")
async def record_view(
    share_token: str,
    db: AsyncSession = Depends(get_db)
):
    """记录浏览（可选的独立端点）"""
    
    share_repo = ShareRepository(db)
    success = await share_repo.increment_view_count(share_token)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分享不存在"
        )
    
    await db.commit()
    
    return {"message": "浏览记录成功"}


@router.delete("/{share_token}")
async def delete_share(
    share_token: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除分享（仅所有者）"""
    
    share_repo = ShareRepository(db)
    share = await share_repo.get_by_token(share_token)
    
    if not share:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分享不存在"
        )
    
    # 验证所有权
    session_result = await db.execute(
        select(DivinationSession).where(DivinationSession.id == share.session_id)
    )
    session = session_result.scalar_one_or_none()
    
    if not session or session.user_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此分享"
        )
    
    await share_repo.delete_share(share_token)
    await db.commit()
    
    logger.info("删除分享", extra={
        "share_token": share_token,
        "user_id": str(current_user.id)
    })
    
    return {"message": "删除成功"}


@router.get("/session/{session_id}/stats", response_model=ShareStatsResponse)
async def get_share_stats(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取会话的分享统计"""
    
    # 验证所有权
    result = await db.execute(
        select(DivinationSession).where(
            DivinationSession.id == session_id,
            DivinationSession.user_id == str(current_user.id)
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="占卜会话不存在"
        )
    
    # 获取统计数据
    share_repo = ShareRepository(db)
    stats = await share_repo.get_stats_by_session(session_id)
    
    # 获取分享列表
    shares = await share_repo.get_by_session_id(session_id)
    shares_data = [
        {
            "share_token": s.share_token,
            "share_url": s.share_url,
            "view_count": s.view_count,
            "created_at": s.created_at.isoformat(),
            "expires_at": s.expires_at.isoformat() if s.expires_at else None,
            "is_expired": s.is_expired()
        }
        for s in shares
    ]
    
    return ShareStatsResponse(
        total_shares=stats["total_shares"],
        total_views=stats["total_views"],
        shares=shares_data
    )
