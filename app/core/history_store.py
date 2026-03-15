import os
import json
from datetime import datetime
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import message_to_dict, messages_from_dict, BaseMessage
from app.core.config import settings as config


def get_history(session_id, timestamp):
    return FileChatMessageHistory(session_id, timestamp, config.HISTORY_PATH)


class FileChatMessageHistory(BaseChatMessageHistory):
    def __init__(self, session_id: str, timestamp: str, storage_path: str):
        self.session_id = session_id      # 会话ID
        self.timestamp = timestamp        # 时间戳
        self.storage_path = storage_path  # 不同ID的会话历史的存储路径
        # 会话历史文件路径
        self.file_path = os.path.join(self.storage_path, self.session_id + ".json")
        # 确保文件夹存在
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

    def add_message(self, message: BaseMessage) -> None:
        """参数为单个BaseMessage，而非Sequence"""
        # 读取已有消息
        all_messages = self.messages  # 直接使用@property装饰的messages属性
        # 追加时间戳: 将时间戳存入 additional_kwargs（原生属性）
        message.additional_kwargs["timestamp"] = self.timestamp 
        # 追加单个消息
        all_messages.append(message)
        # 转换为字典列表并写入文件
        message_dicts = [message_to_dict(msg) for msg in all_messages]
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(message_dicts, f, ensure_ascii=False, indent=2)  # 加ensure_ascii=False避免中文乱码

    @property  # property装饰器将messages方法转变成成员属性
    def messages(self) -> list[BaseMessage]:
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                message_data = json.load(f)
                return messages_from_dict(message_data)
        except FileNotFoundError:
            return []

    def clear(self) -> None:
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump([], f)
