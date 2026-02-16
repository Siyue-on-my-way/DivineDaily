"""应用配置管理"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用配置
    APP_NAME: str = "DivineDaily"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8080
    
    # 数据库配置
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "divinedaily"
    DB_PASSWORD: str = "your_password"
    DB_NAME: str = "divinedaily"
    
    # JWT 配置
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 24
    JWT_REFRESH_EXPIRE_HOURS: int = 168
    
    # 管理员账号
    ADMIN_USERNAME: str = "admin"
    ADMIN_EMAIL: str = "admin@163.com"
    ADMIN_PASSWORD: str = "594120"
    
    # LLM 配置
    DEFAULT_LLM_PROVIDER: str = "openai"
    DEFAULT_LLM_API_KEY: Optional[str] = None
    DEFAULT_LLM_BASE_URL: str = "https://api.openai.com/v1"
    DEFAULT_LLM_MODEL: str = "gpt-3.5-turbo"
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    
    @property
    def database_url(self) -> str:
        """获取数据库连接 URL"""
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def sync_database_url(self) -> str:
        """获取同步数据库连接 URL（用于 Alembic）"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 全局配置实例
settings = Settings()
