"""配置管理"""

import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用信息
    APP_NAME: str = "DivineDaily"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 数据库配置
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_USER: str = os.getenv("DB_USER", "divinedaily")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "divinedaily123")
    DB_NAME: str = os.getenv("DB_NAME", "divinedaily")
    
    # JWT 配置
    JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-secret-key-please-change-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    
    # CORS 配置
    CORS_ORIGINS: List[str] = ["*"]
    
    @property
    def DATABASE_URL(self) -> str:
        """数据库连接 URL"""
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
