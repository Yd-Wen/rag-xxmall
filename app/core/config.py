# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Dict
import os
from pathlib import Path


# 定义配置模型（对应你所有的配置项）
class Settings(BaseSettings):
    # -------------------------- 服务配置 --------------------------
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    # -------------------------- 路径配置 --------------------------
    # MD5_PATH: str = "../../data/knowledge_base/md5.text"
    # PERSIST_DIRECTORY: str = "../../data/chroma_db"
    # HISTORY_PATH: str = "../../data/chat_history"

    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    MD5_PATH: str = str(BASE_DIR / "data" / "knowledge_base" / "md5.text")
    KNOWLEDGE_RECORD_PATH: str = str(BASE_DIR / "data" / "knowledge_base" / "records.json")
    PERSIST_DIRECTORY: str = str(BASE_DIR / "data" / "chroma_db")
    HISTORY_PATH: str = str(BASE_DIR / "data" / "chat_history")
    SYSTEM_PROMPT_PATH: str = str(BASE_DIR / "data" / "prompt" / "system_prompt.txt")

    # -------------------------- API密钥配置 --------------------------
    DASHSCOPE_API_KEY: str  # 必传项（无默认值，强制从环境变量/配置文件读取）

    # -------------------------- Chroma配置 --------------------------
    COLLECTION_NAME: str = "rag"

    # -------------------------- 文本拆分配置 --------------------------
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    SEPARATORS: List[str] = ["\n\n", "\n", " ", "", "?", "!", ".", "？", "！", "。"]
    MAX_SPLIT_CHARACTERS: int = 1000

    # -------------------------- 检索配置 --------------------------
    SIMILARITY_SEARCH_K: int = 3

    # -------------------------- 模型配置 --------------------------
    EMBEDDING_MODEL_NAME: str = "text-embedding-v4"
    CHAT_MODEL_NAME: str = "qwen3-max"

    # # -------------------------- 会话配置 --------------------------
    # SESSION_CONFIG: Dict[str, Dict[str, str]] = {
    #     "configurable": {"session_id": "user_001"}
    # }

    # 配置文件读取规则：优先读取环境变量，其次读取指定的.env文件
    model_config = SettingsConfigDict(
        env_file=f"app/core/settings/.env.{os.getenv('ENVIRONMENT', 'dev')}",  # 按环境读取配置文件
        env_file_encoding="utf-8",
        case_sensitive=False,  # 环境变量不区分大小写（如DASHSCOPE_API_KEY和dashscope_api_key都可）
        extra="ignore"  # 忽略配置文件中未定义的字段
    )


# 创建全局配置实例
settings = Settings()
