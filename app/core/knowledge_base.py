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
from app.core.config import settings as config
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from datetime import datetime
from app.api.v1.knowledge.schema import KnowledgeRequest
from typing import List, Dict
from app.common.md5 import get_md5, check_md5, append_md5, update_md5, remove_md5
from app.common.record import load_records, append_records, get_record, update_record, remove_record


ALLOWED_CATEGORIES = [{
    "name": "文件",
    "value": "file",
    "description": "文件知识库，id为文件标题，url为云存储路径"
}, {
    "name": "商品",
    "value": "goods",
    "description": "商品知识库，id为商品ID，url为商品图片链接列表"
}, {
    "name": "推荐",
    "value": "recommend",
    "description": "推荐知识库，id为推荐ID，url为推荐图片链接列表"
}]  # 允许的知识库类型

class KnowledgeBase:
    """
    知识库核心类 - 支持file/goods/recommend三种类型
    """
    def __init__(self):
        self.ALLOWED_CATEGORIES = [category["value"] for category in ALLOWED_CATEGORIES]  # 允许的知识库类型列表
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
        if category not in self.ALLOWED_CATEGORIES:
            raise ValueError(f"非法的知识库类型：{category}，仅支持{self.ALLOWED_CATEGORIES}")

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
                "url": url if url else [""],
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
        if get_record(request.id):
            return "【跳过】知识库已同步"
        # 获取 MD5
        md5_str = get_md5(request.content)
        if check_md5(md5_str):
            return "【跳过】存在相同知识"
        # 分割文本
        knowledge_chunks = self._split_text(request.content)
        # 创建 metadata
        metadatas = self._create_metadatas(request.id, request.category, request.url, len(knowledge_chunks))
        # 保存到知识库
        chroma_ids = self.chroma.add_texts(texts=knowledge_chunks, metadatas=metadatas)
        # 保存 MD5
        append_md5([md5_str])
        # 保存记录
        time = datetime.now().isoformat()
        append_records([{
            "id": request.id,
            "category": request.category,
            "url": request.url,
            "md5": md5_str,
            "chroma_ids": chroma_ids,
            "create_time": time,
            "update_time": time
        }])

        return "【成功】同步到知识库"

    def update(self, request: KnowledgeRequest) -> str:
        """
        更新知识库
        """
        # 校验
        self._validate_type(request.category)
        # 获取现有记录
        existing_record = get_record(request.id)
        if not existing_record:
            if request.category != 'file':
                return self.upload(request)  # 对于非文件类型，如果记录不存在则直接上传
            return "【跳过】知识库不存在"
        # 获取新MD5
        md5_str = get_md5(request.content)
        if check_md5(md5_str):
            return "【跳过】存在相同知识"
        
        # 删除旧向量
        self.chroma.delete(ids=existing_record["chroma_ids"])
        # 创建新向量
        chunks = self._split_text(request.content)
        metadatas = self._create_metadatas(request.id, existing_record['category'], request.url, len(chunks))
        new_chroma_ids = self.chroma.add_texts(texts=chunks, metadatas=metadatas)
        # 更新MD5
        update_md5(existing_record['md5'], md5_str)
        # 更新记录
        updated_record = existing_record.copy()
        updated_record["url"] = request.url if request.url else existing_record["url"]
        updated_record["md5"] = md5_str
        updated_record["chroma_ids"] = new_chroma_ids
        updated_record["update_time"] = datetime.now().isoformat()
        # 保存更新后的记录
        update_record(existing_record['id'], updated_record)
        return "【成功】知识库已更新"

    def query(self, category: str = 'file', offset: int = 0, limit: int = 10) -> Dict[str,List[Dict]]:
        """
        获取所有知识库（按分类分组）
        :param category: 可选，指定分类获取对应知识库内容，不指定则返回所有内容
        :param offset: 分页偏移量
        :param limit: 分页大小
        :return: 分组结果，示例：
        {
            "file": [{"id": "标题1", "url": ["url1"], "create_time": "xxx"}, ...],
            "goods": [{"id": "goods001", "url": ["img1"], "create_time": "xxx"}, ...],
            "recommend": [...]
        }
        """
        # 1. 加载所有记录并筛选指定分类的记录
        records = load_records()
        target_records = []
        for record in records:
            # 只保留指定分类的记录
            if record['category'] == category:
                simplified_record = {
                    "id": record['id'],
                    "url": record['url'],
                    "create_time": record['create_time'],
                    "update_time": record['update_time']
                }
                target_records.append(simplified_record)
        
        # 计算总数 / 分页处理
        total = len(target_records)  # 该分类的总记录数（不受分页影响）
        paginated_data = target_records[offset:offset + limit]  # 分页切片
        
        return {
            "knowledge": paginated_data,
            "total": total
        }

    def remove(self, record_id: str) -> str:
        """
        删除知识库
        :param record_id: 唯一ID（file=标题，goods/recommend=ID）
        :return: 操作结果
        """
        existing_record = get_record(record_id)
        if not existing_record:
            return "【跳过】知识库不存在"
        
        # 删除向量
        self.chroma.delete(ids=existing_record["chroma_ids"])
        # 删除 MD5
        remove_md5(existing_record['md5'])
        # 删除记录
        remove_record(record_id)
        return "【成功】知识库已删除"
