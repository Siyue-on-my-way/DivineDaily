"""Redis缓存服务"""

import json
import hashlib
from typing import Optional, Any
from datetime import timedelta
import redis.asyncio as redis


class RedisCache:
    """Redis缓存服务"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        """
        初始化Redis连接
        
        Args:
            redis_url: Redis连接URL
        """
        self.redis_url = redis_url
        self.client: Optional[redis.Redis] = None
    
    async def connect(self):
        """连接到Redis"""
        if not self.client:
            self.client = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
    
    async def disconnect(self):
        """断开Redis连接"""
        if self.client:
            await self.client.close()
            self.client = None
    
    async def get(self, key: str) -> Optional[Any]:
        """
        获取缓存
        
        Args:
            key: 缓存键
        
        Returns:
            缓存值，如果不存在返回None
        """
        if not self.client:
            await self.connect()
        
        try:
            value = await self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"[Redis] 获取缓存失败: {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None
    ) -> bool:
        """
        设置缓存
        
        Args:
            key: 缓存键
            value: 缓存值
            expire: 过期时间（秒），None表示永不过期
        
        Returns:
            是否设置成功
        """
        if not self.client:
            await self.connect()
        
        try:
            json_value = json.dumps(value, ensure_ascii=False)
            if expire:
                await self.client.setex(key, expire, json_value)
            else:
                await self.client.set(key, json_value)
            return True
        except Exception as e:
            print(f"[Redis] 设置缓存失败: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """
        删除缓存
        
        Args:
            key: 缓存键
        
        Returns:
            是否删除成功
        """
        if not self.client:
            await self.connect()
        
        try:
            await self.client.delete(key)
            return True
        except Exception as e:
            print(f"[Redis] 删除缓存失败: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """
        检查缓存是否存在
        
        Args:
            key: 缓存键
        
        Returns:
            是否存在
        """
        if not self.client:
            await self.connect()
        
        try:
            return await self.client.exists(key) > 0
        except Exception as e:
            print(f"[Redis] 检查缓存失败: {e}")
            return False
    
    async def expire(self, key: str, seconds: int) -> bool:
        """
        设置缓存过期时间
        
        Args:
            key: 缓存键
            seconds: 过期时间（秒）
        
        Returns:
            是否设置成功
        """
        if not self.client:
            await self.connect()
        
        try:
            await self.client.expire(key, seconds)
            return True
        except Exception as e:
            print(f"[Redis] 设置过期时间失败: {e}")
            return False
    
    async def ttl(self, key: str) -> int:
        """
        获取缓存剩余时间
        
        Args:
            key: 缓存键
        
        Returns:
            剩余时间（秒），-1表示永不过期，-2表示不存在
        """
        if not self.client:
            await self.connect()
        
        try:
            return await self.client.ttl(key)
        except Exception as e:
            print(f"[Redis] 获取TTL失败: {e}")
            return -2
    
    async def clear_pattern(self, pattern: str) -> int:
        """
        清除匹配模式的所有缓存
        
        Args:
            pattern: 匹配模式（如 "user:*"）
        
        Returns:
            删除的键数量
        """
        if not self.client:
            await self.connect()
        
        try:
            keys = []
            async for key in self.client.scan_iter(match=pattern):
                keys.append(key)
            
            if keys:
                await self.client.delete(*keys)
            
            return len(keys)
        except Exception as e:
            print(f"[Redis] 清除缓存失败: {e}")
            return 0
    
    @staticmethod
    def generate_key(*args, prefix: str = "") -> str:
        """
        生成缓存键
        
        Args:
            *args: 用于生成键的参数
            prefix: 键前缀
        
        Returns:
            缓存键
        """
        # 将参数转换为字符串并拼接
        key_parts = [str(arg) for arg in args]
        key_string = ":".join(key_parts)
        
        # 如果键太长，使用MD5哈希
        if len(key_string) > 100:
            key_hash = hashlib.md5(key_string.encode()).hexdigest()
            key_string = key_hash
        
        # 添加前缀
        if prefix:
            return f"{prefix}:{key_string}"
        return key_string


class CacheManager:
    """缓存管理器 - 统一的缓存接口"""
    
    def __init__(self, redis_cache: RedisCache):
        """
        初始化缓存管理器
        
        Args:
            redis_cache: Redis缓存实例
        """
        self.redis = redis_cache
    
    async def get_or_set(
        self,
        key: str,
        fetch_func,
        expire: int = 3600
    ) -> Any:
        """
        获取缓存，如果不存在则调用函数获取并缓存
        
        Args:
            key: 缓存键
            fetch_func: 获取数据的函数（可以是async函数）
            expire: 过期时间（秒）
        
        Returns:
            缓存值或函数返回值
        """
        # 尝试从缓存获取
        cached_value = await self.redis.get(key)
        if cached_value is not None:
            print(f"[Cache] 命中缓存: {key}")
            return cached_value
        
        # 缓存未命中，调用函数获取数据
        print(f"[Cache] 未命中缓存: {key}")
        
        # 判断是否为async函数
        import asyncio
        if asyncio.iscoroutinefunction(fetch_func):
            value = await fetch_func()
        else:
            value = fetch_func()
        
        # 缓存数据
        await self.redis.set(key, value, expire)
        
        return value
    
    async def invalidate(self, key: str):
        """
        使缓存失效
        
        Args:
            key: 缓存键
        """
        await self.redis.delete(key)
        print(f"[Cache] 缓存失效: {key}")
    
    async def invalidate_pattern(self, pattern: str):
        """
        使匹配模式的所有缓存失效
        
        Args:
            pattern: 匹配模式
        """
        count = await self.redis.clear_pattern(pattern)
        print(f"[Cache] 批量缓存失效: {pattern}, 删除{count}个键")


# 全局缓存实例
_redis_cache: Optional[RedisCache] = None
_cache_manager: Optional[CacheManager] = None


async def get_redis_cache() -> RedisCache:
    """获取Redis缓存实例"""
    global _redis_cache
    if _redis_cache is None:
        from app.core.config import settings
        redis_url = getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0')
        _redis_cache = RedisCache(redis_url)
        await _redis_cache.connect()
    return _redis_cache


async def get_cache_manager() -> CacheManager:
    """获取缓存管理器实例"""
    global _cache_manager
    if _cache_manager is None:
        redis_cache = await get_redis_cache()
        _cache_manager = CacheManager(redis_cache)
    return _cache_manager


async def close_redis():
    """关闭Redis连接"""
    global _redis_cache, _cache_manager
    if _redis_cache:
        await _redis_cache.disconnect()
        _redis_cache = None
        _cache_manager = None

