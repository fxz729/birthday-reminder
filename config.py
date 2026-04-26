from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    """应用配置"""

    # 数据库
    database_url: str = "sqlite:///./data/birthday.db"

    # 邮件配置
    mail_username: str = ""
    mail_password: str = ""
    mail_from: str = ""
    mail_server: str = "smtp.qq.com"
    mail_port: int = 587
    mail_starttls: bool = True
    mail_ssl_tls: bool = False
    mail_use_credentials: bool = True
    mail_validate_certs: bool = True

    # ServerChan 配置
    serverchan_sckey: str = ""

    # JWT 配置
    secret_key: str = "change-this-to-a-random-secret-key"
    jwt_algorithm: str = "HS256"
    access_token_expire_hours: int = 24

    # 应用
    app_name: str = "生日定时提醒"
    debug: bool = False
    base_url: str = "http://localhost:8000"
    cors_origins: List[str] = ["http://localhost:8000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
