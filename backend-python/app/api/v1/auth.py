"""认证相关路由"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse, RefreshTokenRequest
from app.services.auth_service import AuthService
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """用户注册"""
    auth_service = AuthService(db)
    user, access_token, refresh_token = await auth_service.register(user_data)
    
    return TokenResponse(
        token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.from_orm(user)
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """用户登录"""
    auth_service = AuthService(db)
    user, access_token, refresh_token = await auth_service.login(login_data)
    
    return TokenResponse(
        token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.from_orm(user)
    )


@router.post("/refresh", response_model=dict)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """刷新令牌"""
    auth_service = AuthService(db)
    access_token, new_refresh_token = await auth_service.refresh_token(refresh_data.refresh_token)
    
    return {
        "token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    """获取当前用户信息"""
    return UserResponse.from_orm(current_user)


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
):
    """用户登出"""
    # TODO: 实现令牌黑名单
    return {"message": "登出成功"}
