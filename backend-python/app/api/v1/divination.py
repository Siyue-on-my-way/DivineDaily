"""占卜相关路由"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.divination import CreateDivinationRequest, DivinationResult
from app.services.enhanced_divination_service import EnhancedDivinationService
from app.services.llm_service import create_llm_service
from app.repositories.llm_repository import LLMRepository

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
            except Exception as e:
                print(f"创建 LLM 服务失败: {e}")
                # 降级：不使用 LLM
        
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
        raise HTTPException(status_code=500, detail=f"占卜失败: {str(e)}")


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


@router.get("/")
async def list_divination_history(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取占卜历史"""
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
        history = await service.list_history(str(current_user.id), limit, offset)
        
        if llm_service and hasattr(llm_service, 'close'):
            await llm_service.close()
        
        return {"data": history, "total": len(history)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取历史失败: {str(e)}")
