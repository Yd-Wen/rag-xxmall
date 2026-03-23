import os
import hashlib
from app.core.config import settings as config
from typing import List


def check_md5(md5_str: str) -> bool:
    """
    检查MD5字符串是否已经处理过
    :param md5_str:
    :return:
    """
    if not os.path.exists(config.MD5_PATH):
        # 文件不存在，创建父目录和空文件
        os.makedirs(os.path.dirname(config.MD5_PATH), exist_ok=True)
        open(config.MD5_PATH, 'w', encoding='utf-8').close()
        return False
    else:
        for line in open(config.MD5_PATH, 'r', encoding='utf-8').readlines():
            line = line.strip()  # 去掉换行符
            if line == md5_str:
                # 已经处理过
                return True
        return False


def append_md5(md5_str_list: List[str]) -> None:
    """
    写入MD5字符串（追加模式）
    :param md5_str_list:
    :return:
    """
    # 追加模式
    with open(config.MD5_PATH, 'a', encoding='utf-8') as f:
        for md5_str in md5_str_list:
            f.write(md5_str + '\n')

def write_md5(md5_str_list: List[str]) -> None:
    """
    写入MD5字符串（覆盖模式）
    :param md5_str_list:
    :return:
    """
    with open(config.MD5_PATH, 'w', encoding='utf-8') as f:
        for md5_str in md5_str_list:
            f.write(md5_str + '\n')

def update_md5(old_md5: str, new_md5: str) -> None:
    """
    更新MD5字符串（先删除旧的，再覆盖新的）
    :param old_md5:
    :param new_md5:
    :return:
    """
    if not os.path.exists(config.MD5_PATH):
        return
    # 读取所有MD5记录
    with open(config.MD5_PATH, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines()]
    # 过滤掉要删除的MD5字符串
    new_lines = [line if line.strip() != old_md5 and line.strip() else new_md5 for line in lines]
    # 将过滤后的MD5记录写回文件
    write_md5(new_lines)

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

def remove_md5(md5_str: str) -> None:
    """
    从MD5记录文件中删除指定的MD5字符串（先删除旧的，再覆盖新的）
    :param md5_str:
    :return:
    """
    if not os.path.exists(config.MD5_PATH):
        return
    # 读取所有MD5记录
    with open(config.MD5_PATH, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines()]
    # 过滤掉要删除的MD5字符串
    new_lines = [line for line in lines if line.strip() != md5_str and line.strip()]
    # 将过滤后的MD5记录写回文件
    write_md5(new_lines)
