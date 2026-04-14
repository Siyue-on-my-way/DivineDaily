"""用户管理 API 路由"""

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.user import User, UserRole
from app.services.user_management_service import UserManagementService
from app.repositories.audit_log_repository import AuditLogRepository
from app.schemas.user_management import (
    UserCreateAdmin, UserUpdateAdmin, UserResponse, UserListResponse,
    UserDetailResponse, ResetPasswordRequest, ChangeRoleRequest,
    ChangeStatusRequest, BatchStatusRequest, BatchDeleteRequest,
    UserStatsResponse, AuditLogListResponse, LoginHistoryListResponse,
    UserDivinationListResponse
)
from app.core.exceptions import PermissionDeniedError

router = APIRouter()


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """要求管理员权限"""
    if current_user.role != UserRole.ADMIN:
        raise PermissionDeniedError(detail="需要管理员权限")
    return current_user


def get_client_ip(request: Request) -> str:
    """获取客户端 IP 地址"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


# ==================== 用户列表 ====================

@router.get("/users", response_model=UserListResponse, tags=["用户管理"])
async def get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    role: Optional[str] = None,
    status: Optional[int] = None,
    order_by: str = Query("created_at"),
    order_direction: str = Query("desc"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取用户列表（分页、搜索、筛选）"""
    service = UserManagementService(db)
    users, total = await service.list_users(
        page=page,
        page_size=page_size,
        search=search,
        role=role,
        status=status,
        order_by=order_by,
        order_direction=order_direction,
        start_date=start_date,
        end_date=end_date
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return UserListResponse(
        users=[UserResponse.from_orm(user) for user in users],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.post("/users", response_model=UserResponse, tags=["用户管理"])
async def create_user(
    user_data: UserCreateAdmin,
    request: Request,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """创建用户"""
    service = UserManagementService(db)
    ip_address = get_client_ip(request)
    user = await service.create_user(user_data, admin, ip_address)
    return UserResponse.from_orm(user)


# ==================== 统计数据 ====================
# 注意: 所有固定路径的路由必须放在 /users/{user_id} 之前

@router.get("/users/stats", response_model=UserStatsResponse, tags=["用户管理"])
async def get_user_stats(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取用户统计数据"""
    service = UserManagementService(db)
    return await service.get_user_stats()


# ==================== 批量操作 ====================

@router.delete("/users/batch", tags=["用户管理"])
async def batch_delete_users(
    request_data: BatchDeleteRequest,
    request: Request,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """批量删除用户"""
    service = UserManagementService(db)
    ip_address = get_client_ip(request)
    result = await service.batch_delete_users(request_data.user_ids, admin, ip_address)
    return {
        "message": "批量删除成功",
        "deleted_count": result["deleted_count"],
        "skipped_count": result["skipped_count"]
    }


@router.put("/users/batch/status", tags=["用户管理"])
async def batch_change_status(
    request_data: BatchStatusRequest,
    request: Request,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """批量修改用户状态"""
    service = UserManagementService(db)
    ip_address = get_client_ip(request)
    result = await service.batch_change_status(request_data, admin, ip_address)
    return {
        "message": "批量修改成功",
        "updated_count": result["updated_count"],
        "skipped_count": result["skipped_count"]
    }


# ==================== 用户详情与操作 ====================
# 注意: 带 {user_id} 参数的路由放在最后

@router.get("/users/{user_id}", response_model=UserDetailResponse, tags=["用户管理"])
async def get_user_detail(
    user_id: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取用户详情"""
    service = UserManagementService(db)
    return await service.get_user_detail(user_id)


@router.put("/users/{user_id}", response_model=UserResponse, tags=["用户管理"])
async def update_user(
    user_id: int,
    user_data: UserUpdateAdmin,
    request: Request,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """更新用户"""
    service = UserManagementService(db)
    ip_address = get_client_ip(request)
    user = await service.update_user(user_id, user_data, admin, ip_address)
    return UserResponse.from_orm(user)


@router.delete("/users/{user_id}", tags=["用户管理"])
async def delete_user(
    user_id: int,
    request: Request,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """删除用户"""
    service = UserManagementService(db)
    ip_address = get_client_ip(request)
    await service.delete_user(user_id, admin, ip_address)
    return {"message": "删除成功"}


@router.post("/users/{user_id}/reset-password", tags=["用户管理"])
async def reset_password(
    user_id: int,
    request_data: ResetPasswordRequest,
    request: Request,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """重置用户密码"""
    service = UserManagementService(db)
    ip_address = get_client_ip(request)
    result = await service.reset_password(user_id, request_data, admin, ip_address)
    return result


@router.put("/users/{user_id}/role", response_model=UserResponse, tags=["用户管理"])
async def change_role(
    user_id: int,
    request_data: ChangeRoleRequest,
    request: Request,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """修改用户角色"""
    service = UserManagementService(db)
    ip_address = get_client_ip(request)
    user = await service.change_role(user_id, request_data, admin, ip_address)
    return UserResponse.from_orm(user)


@router.put("/users/{user_id}/status", response_model=UserResponse, tags=["用户管理"])
async def change_status(
    user_id: int,
    request_data: ChangeStatusRequest,
    request: Request,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """修改用户状态"""
    service = UserManagementService(db)
    ip_address = get_client_ip(request)
    user = await service.change_status(user_id, request_data, admin, ip_address)
    return UserResponse.from_orm(user)


@router.get("/users/{user_id}/divinations", response_model=UserDivinationListResponse, tags=["用户管理"])
async def get_user_divinations(
    user_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    filter_type: Optional[str] = Query(None, description="筛选类型：all/iching/tarot/fortune"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取用户占卜历史（支持筛选和搜索）"""
    from app.models.divination import DivinationSession
    from sqlalchemy import select, func, desc, or_
    
    # 构建基础查询
    query = select(DivinationSession).where(
        DivinationSession.user_id == str(user_id)
    )
    
    # 应用筛选
    if filter_type and filter_type != 'all':
        if filter_type == 'iching':
            query = query.where(DivinationSession.version == 'CN')
        elif filter_type == 'tarot':
            query = query.where(DivinationSession.version == 'TAROT')
        elif filter_type == 'fortune':
            # 运势类型可能有多种表示方式
            query = query.where(
                or_(
                    DivinationSession.version == 'FORTUNE',
                    DivinationSession.version.like('%fortune%'),
                    DivinationSession.event_type == 'daily_fortune'
                )
            )
    
    # 应用搜索
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                DivinationSession.question.like(search_pattern),
                DivinationSession.result_summary.like(search_pattern)
            )
        )
    
    # 排序
    query = query.order_by(desc(DivinationSession.created_at))
    
    # 获取总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # 分页查询
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    divinations = result.scalars().all()
    
    from app.schemas.user_management import UserDivinationResponse
    return UserDivinationListResponse(
        divinations=[UserDivinationResponse.from_orm(d) for d in divinations],
        total=total
    )


@router.get("/users/{user_id}/divinations/{session_id}", tags=["用户管理"])
async def get_user_divination_detail(
    user_id: int,
    session_id: str,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """获取用户单条占卜详情（含 result_detail/result_data）"""
    from sqlalchemy import select
    from app.models.divination import DivinationSession

    result = await db.execute(
        select(DivinationSession).where(
            DivinationSession.id == session_id,
            DivinationSession.user_id == str(user_id),
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="占卜记录不存在")

    return {
        "id": session.id,
        "user_id": session.user_id,
        "version": session.version,
        "question": session.question,
        "event_type": session.event_type,
        "status": session.status,
        "result_summary": session.result_summary,
        "result_detail": session.result_detail,
        "result_data": session.result_data,
        "created_at": session.created_at,
        "updated_at": session.updated_at,
    }


@router.get("/users/{user_id}/login-history", response_model=LoginHistoryListResponse, tags=["用户管理"])
async def get_user_login_history(
    user_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取用户登录历史"""
    from app.models.user import UserSession
    from sqlalchemy import select, func, desc
    
    # 查询登录历史
    query = select(UserSession).where(
        UserSession.user_id == user_id
    ).order_by(desc(UserSession.created_at))
    
    # 获取总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # 分页查询
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    sessions = result.scalars().all()
    
    from app.schemas.user_management import LoginHistoryResponse
    return LoginHistoryListResponse(
        history=[LoginHistoryResponse.from_orm(s) for s in sessions],
        total=total
    )


# ==================== 操作日志 ====================

@router.get("/audit-logs", response_model=AuditLogListResponse, tags=["用户管理"])
async def get_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    operator_id: Optional[int] = None,
    target_user_id: Optional[int] = None,
    action: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取操作日志"""
    audit_repo = AuditLogRepository(db)
    logs, total = await audit_repo.list_logs(
        page=page,
        page_size=page_size,
        operator_id=operator_id,
        target_user_id=target_user_id,
        action=action,
        start_date=start_date,
        end_date=end_date
    )
    
    from app.schemas.user_management import AuditLogResponse
    return AuditLogListResponse(
        logs=[AuditLogResponse.from_orm(log) for log in logs],
        total=total,
        page=page,
        page_size=page_size
    )
