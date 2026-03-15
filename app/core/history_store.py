import os
import json
from datetime import datetime
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import message_to_dict, messages_from_dict, BaseMessage
from app.core.config import settings as config
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage


def get_history(session_id, req_time=None, res_time=None):
    return FileChatMessageHistory(session_id, req_time, res_time, config.HISTORY_PATH)


class FileChatMessageHistory(BaseChatMessageHistory):
    def __init__(self, session_id: str, req_time: str, res_time: str, storage_path: str):
        self.session_id = session_id      # 会话ID
        self.req_time = req_time          # 请求时间戳
        self.res_time = res_time          # 响应时间戳
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
        if isinstance(message, HumanMessage):
            # 用户消息 → 请求时间戳
            message.additional_kwargs["timestamp"] = self.req_time
        else:
            # 其他消息类型（如SystemMessage）→ 默认用当前时间
            message.additional_kwargs["timestamp"] = datetime.now().isoformat()
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

    def update_response_timestamp(self) -> None:
        """更新最后一条AIMessage的响应时间戳"""
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                message_data = json.load(f)
            # 引用最后一条消息并更新响应时间戳
            last_msg = message_data[-1] if message_data else None
            if last_msg and last_msg.get("type") == "ai":
                last_msg.get("additional_kwargs", {}).setdefault("timestamp", self.res_time)
                # 写回文件
                with open(self.file_path, "w", encoding="utf-8") as f:
                    json.dump(message_data, f, ensure_ascii=False, indent=2)

        except FileNotFoundError:
            # 无历史文件时跳过
            pass
        except IndexError:
            # 极端情况：消息列表为空
            pass
