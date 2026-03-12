"""
知识库
"""
import os
import hashlib

from app.core.config import settings as config
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from datetime import datetime


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


class KnowledgeBase:
    """
    知识库
    """
    def __init__(self):
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

    def upload(self, data, file_name):
        """
        上传文件到知识库
        :param data:
        :param file_name:
        :return:
        """
        # 去重
        md5_hex = get_md5(data)
        if check_md5(md5_hex):
            return "【跳过】知识库已存在该文件"
        # 分割
        if len(data) > config.MAX_SPLIT_CHARACTERS:
            knowledge_chunks: list[str] = self.splitter.split_text(data)
        else:
            knowledge_chunks = [data]
        # 添加到知识库
        self.chroma.add_texts(
            texts=knowledge_chunks,
            metadatas=[{"source": file_name, "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]
        )
        # 保存MD5
        save_md5(md5_hex)

        return "【成功】文件存入知识库"


if __name__ == '__main__':
    kb = KnowledgeBase()
    res = kb.upload("test", "test.txt")
    print(res)
    # r1 = get_md5('123456')
    # r2 = get_md5('123465')
    # r3 = get_md5('123456')
    # print(r1, r2, r3)
    # save_md5(r1)
    # print(check_md5("e10adc3949ba59abbe56e057f20f883e"))
