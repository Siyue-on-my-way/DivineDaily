"""带缓存的占卜服务"""

from typing import Optional, List
from app.core.cache import get_cache_manager, RedisCache
from app.core.config import settings
from app.models.divination import DivinationSession
from app.repositories.divination_repository import DivinationRepository


class CachedDivinationService:
    """带缓存的占卜服务"""
    
    def __init__(self, repository: DivinationRepository, cache_manager=None):
        """
        初始化服务
        
        Args:
            repository: 占卜Repository
            cache_manager: 缓存管理器（可选）
        """
        self.repository = repository
        self.cache_manager = cache_manager
        self.cache_enabled = settings.REDIS_ENABLED
    
    async def get_session_cached(self, session_id: str) -> Optional[DivinationSession]:
        """
        获取占卜会话（带缓存）
        
        Args:
            session_id: 会话ID
        
        Returns:
            DivinationSession: 占卜会话
        """
        if not self.cache_enabled or not self.cache_manager:
            return await self.repository.get_session(session_id)
        
        # 生成缓存键
        cache_key = RedisCache.generate_key("session", session_id, prefix="divination")
        
        # 使用缓存
        return await self.cache_manager.get_or_set(
            key=cache_key,
            fetch_func=lambda: self.repository.get_session(session_id),
            expire=settings.CACHE_TTL_DEFAULT
        )
    
    async def get_user_sessions_cached(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[DivinationSession]:
        """
        获取用户会话列表（带缓存）
        
        Args:
            user_id: 用户ID
            limit: 每页数量
            offset: 偏移量
        
        Returns:
            List[DivinationSession]: 会话列表
        """
        if not self.cache_enabled or not self.cache_manager:
            return await self.repository.get_user_sessions(user_id, limit, offset)
        
        # 生成缓存键
        cache_key = RedisCache.generate_key(
            "user_sessions", user_id, limit, offset,
            prefix="divination"
        )
        
        # 使用缓存（短期缓存，因为列表可能经常变化）
        return await self.cache_manager.get_or_set(
            key=cache_key,
            fetch_func=lambda: self.repository.get_user_sessions(user_id, limit, offset),
            expire=settings.CACHE_TTL_SHORT
        )
    
    async def get_user_stats_cached(self, user_id: str) -> dict:
        """
        获取用户统计信息（带缓存）
        
        Args:
            user_id: 用户ID
        
        Returns:
            dict: 统计信息
        """
        if not self.cache_enabled or not self.cache_manager:
            return await self.repository.get_user_stats(user_id)
        
        # 生成缓存键
        cache_key = RedisCache.generate_key("user_stats", user_id, prefix="divination")
        
        # 使用缓存（中期缓存）
        return await self.cache_manager.get_or_set(
            key=cache_key,
            fetch_func=lambda: self.repository.get_user_stats(user_id),
            expire=settings.CACHE_TTL_DEFAULT
        )
    
    async def invalidate_user_cache(self, user_id: str):
        """
        使用户相关的所有缓存失效
        
        Args:
            user_id: 用户ID
        """
        if not self.cache_enabled or not self.cache_manager:
            return
        
        # 使用模式匹配删除所有相关缓存
        pattern = f"divination:*{user_id}*"
        await self.cache_manager.invalidate_pattern(pattern)
    
    async def invalidate_session_cache(self, session_id: str):
        """
        使会话缓存失效
        
        Args:
            session_id: 会话ID
        """
        if not self.cache_enabled or not self.cache_manager:
            return
        
        cache_key = RedisCache.generate_key("session", session_id, prefix="divination")
        await self.cache_manager.invalidate(cache_key)


class CacheStrategy:
    """缓存策略"""
    
    # 缓存键前缀
    PREFIX_DIVINATION = "divination"
    PREFIX_USER = "user"
    PREFIX_CONFIG = "config"
    PREFIX_LLM = "llm"
    
    # 缓存过期时间（秒）
    TTL_SESSION = 3600  # 会话缓存：1小时
    TTL_USER_LIST = 300  # 用户列表：5分钟
    TTL_USER_STATS = 3600  # 用户统计：1小时
    TTL_CONFIG = 86400  # 配置缓存：24小时
    TTL_LLM_RESPONSE = 7200  # LLM响应：2小时
    
    @staticmethod
    def get_session_key(session_id: str) -> str:
        """获取会话缓存键"""
        return RedisCache.generate_key(
            "session", session_id,
            prefix=CacheStrategy.PREFIX_DIVINATION
        )
    
    @staticmethod
    def get_user_sessions_key(user_id: str, limit: int, offset: int) -> str:
        """获取用户会话列表缓存键"""
        return RedisCache.generate_key(
            "user_sessions", user_id, limit, offset,
            prefix=CacheStrategy.PREFIX_DIVINATION
        )
    
    @staticmethod
    def get_user_stats_key(user_id: str) -> str:
        """获取用户统计缓存键"""
        return RedisCache.generate_key(
            "user_stats", user_id,
            prefix=CacheStrategy.PREFIX_DIVINATION
        )
    
    @staticmethod
    def get_config_key(config_type: str) -> str:
        """获取配置缓存键"""
        return RedisCache.generate_key(
            config_type,
            prefix=CacheStrategy.PREFIX_CONFIG
        )
    
    @staticmethod
    def get_llm_response_key(prompt: str, model: str) -> str:
        """获取LLM响应缓存键"""
        return RedisCache.generate_key(
            "response", prompt, model,
            prefix=CacheStrategy.PREFIX_LLM
        )

