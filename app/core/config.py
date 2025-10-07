# Noupe-local/app/core/config.py

from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    """
    应用配置 (v2.0 - 哲学修正版)
    - 彻底解耦硬编码，所有 ID 均从环境变量加载，实现真正的通用性。
    """
    # --- 应用元数据 ---
    APP_NAME: str = "Noupe-2api"
    APP_VERSION: str = "2.0.0"
    DESCRIPTION: str = "一个将任何 Noupe/Jotform 聊天机器人转换为兼容 OpenAI 格式 API 的高性能通用代理。"

    # --- 认证与安全 ---
    API_MASTER_KEY: Optional[str] = None

    # --- Noupe API 核心凭证 (全部从 .env 加载) ---
    NOUPE_COOKIE: str
    AGENT_ID: str
    CHAT_ID: str

    # --- 模型列表配置 ---
    SUPPORTED_MODELS: List[str] = [
        "noupe-chat-model",
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        extra = "ignore"

settings = Settings()
