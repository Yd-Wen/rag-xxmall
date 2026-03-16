"""
    知识库核心模块
    知识库记录存储规范：
    {
        "id": "文件标题/商品ID/推荐ID（唯一标识）",
        "category": "file/goods/recommend",
        "url": ["云存储路径列表"],
        "md5": "内容MD5",
        "chroma_ids": ["向量ID列表"],
        "create_time": "创建时间",
        "update_time": "更新时间"
    }
"""
import os
import hashlib
import json
from app.core.config import settings as config
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from datetime import datetime
from app.api.v1.knowledge.schema import KnowledgeRequest
from typing import List, Dict, Optional


def check_md5(md5_str) -> bool:
    """
    检查MD5字符串是否已经处理过
    :param md5_str:
    :return:
    """
    if not os.path.exists(config.MD5_PATH):
        # 文件不存在
        open(config.MD5_PATH, 'w', encoding='utf-8').close()
        return False
    else:
        for line in open(config.MD5_PATH, 'r', encoding='utf-8').readlines():
            line = line.strip()  # 去掉换行符
            if line == md5_str:
                # 已经处理过
                return True
        return False


def save_md5(md5_str) -> None:
    """
    保存MD5字符串，记录到文件保存
    :param md5_str:
    :return:
    """
    # 追加模式
    with open(config.MD5_PATH, 'a', encoding='utf-8') as f:
        f.write(md5_str + '\n')


def get_md5(file_str, encoding='utf-8') -> str:
    """
    文件内容转换成MD5值
    :param file_str:
    :param encoding:
    :return:
    """
    str_bytes = file_str.encode(encoding)    # 字符串转字节流
    md5 = hashlib.md5()                 # 创建MD5对象
    md5.update(str_bytes)               # 更新MD5对象
    md5_hex = md5.hexdigest()           # 获取MD5的十六进制字符串
    return md5_hex

def remove_md5(md5_str) -> None:
    """
    从MD5记录文件中删除指定的MD5字符串
    :param md5_str:
    :return:
    """
    if not os.path.exists(config.MD5_PATH):
        return
    # 读取所有MD5记录
    with open(config.MD5_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    # 过滤掉要删除的MD5字符串
    new_lines = [line for line in lines if line.strip() != md5_str]
    # 将过滤后的MD5记录写回文件
    with open(config.MD5_PATH, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

def _load_records() -> List[Dict]:

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

def _save_records(new_records: List[Dict]) -> None:
    """
    保存知识库记录到文件
    """
    records = _load_records()
    records.extend(new_records)
    with open(config.KNOWLEDGE_RECORD_PATH, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

def _get_record(record_id: str) -> Optional[Dict]:
    """
    根据唯一ID查询知识库记录
    """
    records = _load_records()
    for record in records:
        if record.get('id') == record_id:
            return record
    return None

def _remove_record(record_id: str) -> bool:
    """
    根据唯一ID删除知识库记录
    """
    records = _load_records()
    new_records = [record for record in records if record.get('id') != record_id]
    if len(new_records) < len(records):
        _save_records(new_records)
        return True
    return False

class KnowledgeBase:
    """
    知识库核心类 - 支持file/goods/recommend三种类型
    """
    def __init__(self):
        self.ALLOWED_TYPES = ['file', 'goods', 'recommend']  # 允许的知识库类型
        os.makedirs(config.PERSIST_DIRECTORY, exist_ok=True)  # 创建数据库目录, 如果已存在则不创建
        # Chroma 数据库实例
        self.chroma = Chroma(
            collection_name=config.COLLECTION_NAME,
            embedding_function=DashScopeEmbeddings(dashscope_api_key=config.DASHSCOPE_API_KEY,
                                                   model=config.EMBEDDING_MODEL_NAME),
            persist_directory=config.PERSIST_DIRECTORY
        )
        # 文本分割器实例
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP,
            separators=config.SEPARATORS,
            length_function=len
        )

    def _validate_type(self, category: str) -> None:
        """
        验证知识库类型是否合法
        """
        if category not in self.ALLOWED_TYPES:
            raise ValueError(f"非法的知识库类型：{category}，仅支持{self.ALLOWED_TYPES}")

    def _split_text(self, content: str) -> List[str]:
        """
        文本分割（处理长文本）
        """
        if len(content) > config.MAX_SPLIT_CHARACTERS:
            return self.splitter.split_text(content)
        return [content]

    def _create_metadatas(self, record_id: str, category: str, url: List[str], length: int=1) -> List[Dict]:
        """
        为每个文本块创建metadata
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        metadatas = []
        for idx in range(length):
            metadatas.append({
                "id": record_id,
                "category": category,
                "url": url,
                "chunk_index": idx,
                "create_time": current_time,
                "update_time": current_time
            })
        return metadatas

    def upload(self, request: KnowledgeRequest) -> str:
        """
        上传知识库
        :param request: 知识库上传请求
        :return: 响应消息
        """
        # 校验
        self._validate_type(request.category)
        if _get_record(request.id):
            return "【跳过】知识库已存在"
        # 分割文本
        knowledge_chunks = self._split_text(request.content)
        # 创建 metadata
        metadatas = self._create_metadatas(request.id, request.category, request.url, len(knowledge_chunks))
        # 保存到知识库
        chroma_ids = self.chroma.add_texts(texts=knowledge_chunks, metadatas=metadatas)
        # 保存 MD5
        save_md5(get_md5(request.content))
        # 保存记录
        _save_records([{
            "id": request.id,
            "category": request.category,
            "url": request.url,
            "md5": get_md5(request.content),
            "chroma_ids": chroma_ids,
            "create_time": datetime.now().isoformat(),
            "update_time": datetime.now().isoformat()
        }])

        return "【成功】添加到知识库"

    def update(self, request: KnowledgeRequest) -> str:
        """
        更新知识库
        """
        # 校验
        self._validate_type(request.category)
        # 获取现有记录
        existing_record = _get_record(request.id)
        if not existing_record:
            return "【跳过】知识库不存在"
        
        new_md5 = existing_record['md5']
        new_chroma_ids = existing_record['chroma_ids']
        # 更新向量存储
        if request.content is not None and request.content.strip():
            new_md5 = get_md5(request.content)
            # 内容变更才更新向量
            if new_md5 != existing_record['md5']:
                need_update_vector = True
                # 删除旧向量
                self.chroma.delete(ids=existing_record["chroma_ids"])
                # 创建新向量
                chunks = self._split_text(request.content)
                metadatas = self._create_metadatas(request.id, existing_record['category'], request.url, len(chunks))
                new_chroma_ids = self.chroma.add_texts(texts=chunks, metadatas=metadatas)

        # 更新记录
        updated_record = existing_record.copy()
        if request.url is not None:
            updated_record["url"] = request.url
        updated_record["md5"] = new_md5
        updated_record["chroma_ids"] = new_chroma_ids
        updated_record["update_time"] = datetime.now().isoformat()
        # 保存更新后的记录
        _save_records([updated_record])
        return "【成功】更新知识库"

    def get(self, category: str = None) -> Dict[str,List[Dict]]:
        """
        获取所有知识库（按分类分组）
        :return: 分组结果，示例：
        {
            "file": [{"id": "标题1", "url": ["url1"], "create_time": "xxx"}, ...],
            "goods": [{"id": "goods001", "url": ["img1"], "create_time": "xxx"}, ...],
            "recommend": [...]
        }
        """
        records = _load_records()
        result = {k: [] for k in self.ALLOWED_CATEGORIES}

        for record in records:
            category = record['category']
            # 仅返回核心信息，避免数据过大
            simplified_record = {
                "id": record['id'],
                "url": record['url'],
                "create_time": record['create_time'],
                "update_time": record['update_time']
            }
            result[category].append(simplified_record)
        
        if category and category in self.ALLOWED_CATEGORIES:
            return {category: result[category]}

        return result

    def remove(self, record_id: str) -> str:
        """
        删除知识库
        :param record_id: 唯一ID（file=标题，goods/recommend=ID）
        :return: 操作结果
        """
        existing_record = _get_record(record_id)
        if not existing_record:
            return "【跳过】知识库不存在"
        
        # 删除向量
        self.chroma.delete(ids=existing_record["chroma_ids"])
        # 删除 MD5
        remove_md5(existing_record['md5'])
        # 删除记录
        _remove_record(record_id)
        return "【成功】删除知识库"
