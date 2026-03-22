import os
import json
from app.core.config import settings as config
from typing import List, Dict, Optional


def load_records() -> List[Dict]:

    if not os.path.exists(config.KNOWLEDGE_RECORD_PATH):
        # 初始化空文件
        with open(config.KNOWLEDGE_RECORD_PATH, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return []
    
    try:
        with open(config.KNOWLEDGE_RECORD_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        # 文件损坏时重置
        with open(config.KNOWLEDGE_RECORD_PATH, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return []

def append_records(records: List[Dict]) -> None:
    """
    追加知识库记录到文件
    """
    # 先加载现有记录
    existing_records = load_records()
    # 合并新记录
    existing_records.extend(records)
    # 覆盖写入合并后的记录（保证JSON格式正确）
    write_records(existing_records)

def write_records(records: List[Dict]) -> None:
    """
    保存知识库记录到文件（覆盖写入）
    """
    with open(config.KNOWLEDGE_RECORD_PATH, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

def get_record(record_id: str) -> Optional[Dict]:
    """
    根据唯一ID查询知识库记录
    """
    records = load_records()
    for record in records:
        if record.get('id') == record_id:
            return record
    return None

def update_record(record_id: str, new_record: Dict) -> bool:
    """
    根据唯一ID更新知识库记录（先删除旧的，再覆盖新的）
    """
    records = load_records()
    updated = False
    for idx, record in enumerate(records):
        if record.get('id') == record_id:
            records[idx] = new_record
            updated = True
            break
    if updated:
        write_records(records)
    return updated

def remove_record(record_id: str) -> bool:
    """
    根据唯一ID删除知识库记录（先删除旧的，再覆盖新的）
    """
    records = load_records()
    new_records = [record for record in records if record.get('id') != record_id]
    if len(new_records) < len(records):
        write_records(new_records)
        return True
    return False
