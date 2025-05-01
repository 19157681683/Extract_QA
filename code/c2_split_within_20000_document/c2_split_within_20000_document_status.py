# -*- coding: utf-8 -*-
"""
@author: 李林名
Created on 2025/3/25 12:21
"""

import os
import re
import logging
from collections import defaultdict

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def extract_prefix_and_number(filename):
    """
    提取文件名前缀和序号。

    主要实现方式：
        使用正则表达式匹配文件名，提取前缀和序号部分。
        如果文件名不含序号，则返回文件名（去除 .md 后缀）和 None。

    Args:
        filename (str): 文件名，例如 "暑假值班-0.md" 或 "2023年营收.md"

    Returns:
        tuple: (前缀, 序号)，如果无序号则返回 (文件名, None)
    """
    # 匹配 {前缀}-{序号}.md 模式
    match = re.match(r"^(.*?)-(\d+)\.md$", filename)
    if match:
        return match.group(1), int(match.group(2))
    # 无序号的情况
    if filename.endswith('.md'):
        return filename[:-3], None
    return filename, None


def classify_file(filename):
    """
    根据文件名分类文件为小文件、中文件或大文件。

    主要实现方式：
        根据文件名序号判断文件类型，无序号为小文件，序号 < 10 为中文件，序号 >= 10 为大文件。

    Args:
        filename (str): 文件名

    Returns:
        str: 文件类型 ('small', 'medium', 'large')
    """
    prefix, number = extract_prefix_and_number(filename)
    if number is None:
        return 'small'
    elif number < 10:
        return 'medium'
    else:
        return 'large'


def count_files_in_directory(directory_path):
    """
    统计文件夹中的文件数量及分类。

    主要实现方式：
        遍历文件夹，统计总文件数、单一文件数（去重前缀），并按小文件、中文件、大文件分类。

    Args:
        directory_path (str): 文件夹路径

    Returns:
        dict: 包含统计结果的字典，包括总文件数、单一文件数及各类文件数量
    """
    if not os.path.isdir(directory_path):
        logging.error(f"路径 {directory_path} 不是有效的文件夹")
        return None

    total_files = 0
    unique_files = set()  # 单一文件去重
    file_counts = {'small': 0, 'medium': defaultdict(int), 'large': defaultdict(int)}  # 按类型统计

    # 遍历文件夹
    for root, _, files in os.walk(directory_path):
        for filename in files:
            if not filename.endswith('.md'):
                continue
            total_files += 1
            prefix, number = extract_prefix_and_number(filename)
            unique_files.add(prefix)  # 单一文件只记录前缀

            # 分类统计
            file_type = classify_file(filename)
            if file_type == 'small':
                file_counts['small'] += 1
            elif file_type == 'medium':
                file_counts['medium'][prefix] += 1
            elif file_type == 'large':
                file_counts['large'][prefix] += 1

    # 计算中文件和大文件的单一数量
    medium_count = len(file_counts['medium'])
    large_count = len(file_counts['large'])

    # 汇总结果
    result = {
        'total_files': total_files,
        'unique_files': len(unique_files),
        'small_files': file_counts['small'],
        'medium_files': medium_count,
        'large_files': large_count
    }
    return result


def find_max_text_length(directory_path):
    """
    查找文件夹中 Markdown 文件的最大文本块长度及对应文件名。

    主要实现方式：
        遍历文件夹中的 Markdown 文件，读取每个文件内容，计算字符数，记录最大长度和对应的文件名。
        如果文件夹无效或无 Markdown 文件，返回 None。

    Args:
        directory_path (str): 文件夹路径

    Returns:
        tuple: (最大文本块长度, 对应文件名)，如果无有效文件则返回 (None, None)
    """
    if not os.path.isdir(directory_path):
        logging.error(f"路径 {directory_path} 不是有效的文件夹")
        return None, None

    max_length = 0
    max_length_file = None

    # 遍历文件夹
    for root, _, files in os.walk(directory_path):
        for filename in files:
            if not filename.endswith('.md'):
                continue
            file_path = os.path.join(root, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    content_length = len(content)
                    if content_length > max_length:
                        max_length = content_length
                        max_length_file = filename
            except Exception as e:
                logging.warning(f"无法读取文件 {file_path}: {str(e)}")

    if max_length == 0:
        logging.info("文件夹中没有有效的 Markdown 文件")
        return None, None

    return max_length, max_length_file


def log_file_stats(directory_path):
    """
    统计并记录文件夹的文件信息，包括文件数量和最大文本块长度。

    主要实现方式：
        调用 count_files_in_directory 统计文件数量和分类信息。
        调用 find_max_text_length 获取最大文本块长度及文件名。
        使用 logging 模块记录统计结果。

    Args:
        directory_path (str): 文件夹路径
    """
    # 统计文件数量
    stats = count_files_in_directory(directory_path)
    if not stats:
        return

    total = stats['total_files']
    logging.info(f"文件夹总文件数量: {total}")
    logging.info(f"单一文件总数量: {stats['unique_files']}")
    logging.info(f"小文件数量: {stats['small_files']} ({stats['small_files'] / total:.2%})")
    logging.info(f"中文件数量: {stats['medium_files']} ({stats['medium_files'] / total:.2%})")
    logging.info(f"大文件数量: {stats['large_files']} ({stats['large_files'] / total:.2%})")

    # 统计最大文本块长度
    max_length, max_length_file = find_max_text_length(directory_path)
    if max_length is not None:
        logging.info(f"最大文本块长度: {max_length} 字符 (文件名: {max_length_file})")


# 示例使用
if __name__ == "__main__":
    test_path = r"D:\Project\1. Super_Computer\2025\c03_js_wang_OpenAI_use\project-2\data\c2_split_within_20000_document"  # 请替换为实际路径
    log_file_stats(test_path)