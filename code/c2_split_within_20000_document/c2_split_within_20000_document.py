#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：project-2
@File    ：c2_split_within_20000_document.py
@IDE     ：PyCharm
@Author  ：李林名
@Date    ：2025/4/30
@Usage   ：实现对Markdown文件按2万字符切片，并在每个切片首部添加论文标题和摘要，保存到输出文件夹中
'''
import os
import re
import shutil
import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List, Tuple, Optional

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_file_char_count(file_path: str) -> int:
    """获取文件字符数

    主要实现方式：打开文件，读取内容，计算字符长度。

    Args:
        file_path (str): 文件路径

    Returns:
        int: 文件字符数
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return len(content)
    except Exception as e:
        logging.error(f"读取文件 {file_path} 失败: {e}")
        return 0

def parse_markdown_sections(content: str) -> Tuple[Optional[str], Optional[str], List[Tuple[str, str]]]:
    """解析 Markdown 文件为论文标题、摘要和一级标题段落

    主要实现方式：
    1. 使用正则表达式匹配一级标题，提取第一个一级标题作为论文标题。
    2. 查找 # Abstract 或 # a b s t r a c t 标题，提取其内容直到下一个一级标题。
    3. 将剩余内容分割为一级标题段落，每个段落包含标题和内容。

    Args:
        content (str): Markdown 文件内容

    Returns:
        Tuple[Optional[str], Optional[str], List[Tuple[str, str]]]:
            - 论文标题（第一个一级标题，可能为 None）
            - 摘要内容（可能为 None）
            - 包含 (标题, 内容) 的段落列表，标题为空字符串表示无标题部分
    """
    # 匹配一级标题（# 后跟一个空格）
    pattern = r'^# .+$'
    lines = content.splitlines()
    sections = []
    current_section = []
    current_title = ""
    paper_title = None
    abstract = None
    in_abstract = False

    for line in lines:
        line_stripped = line.strip()
        if re.match(pattern, line_stripped, re.MULTILINE):
            # 第一个一级标题作为论文标题
            if paper_title is None:
                paper_title = line_stripped
                current_title = line_stripped
                current_section.append(line)
                continue

            # 处理摘要
            if line_stripped in ("# Abstract", "# a b s t r a c t"):
                in_abstract = True
                current_section = [line]
                current_title = line_stripped
                continue

            # 遇到下一个一级标题，结束摘要
            if in_abstract:
                abstract = "\n".join(current_section)
                in_abstract = False
                sections.append((current_title, abstract))
                current_section = [line]
                current_title = line_stripped
            else:
                # 保存当前段落
                if current_section:
                    sections.append((current_title, "\n".join(current_section)))
                current_title = line_stripped
                current_section = [line]
        else:
            current_section.append(line)

    # 保存最后一个段落
    if current_section:
        if in_abstract:
            abstract = "\n".join(current_section)
            sections.append((current_title, abstract))
        else:
            sections.append((current_title, "\n".join(current_section)))

    # 日志记录
    if paper_title:
        logging.info(f"提取论文标题: {paper_title}")
    else:
        logging.warning("未找到论文标题")
    if abstract:
        logging.info("成功提取摘要")
    else:
        logging.warning("未找到摘要")

    return paper_title, abstract, sections

def split_file(file_path: str, output_dir: str, chunk_size: int = 20000) -> None:
    """将 Markdown 文件按指定字符数切分并保存

    主要实现方式：
    1. 读取文件内容，解析为论文标题、摘要和一级标题段落。
    2. 如果总字符数 <= chunk_size，直接复制。
    3. 否则，按一级标题段落组合或单独切片，确保每个切片接近但不超过 chunk_size。
    4. 每个切片首部添加论文标题和摘要（如果存在），文件名按 {原文件名}-{序号}.md 命名。

    Args:
        file_path (str): 输入文件路径
        output_dir (str): 输出文件夹路径
        chunk_size (int): 每块的最大字符数，默认为 20000

    Returns:
        None
    """
    file_name = Path(file_path).stem
    suffix = Path(file_path).suffix

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        logging.error(f"读取文件 {file_path} 失败: {e}")
        return

    if len(content) <= chunk_size:
        # 小于等于 chunk_size，直接复制
        output_path = os.path.join(output_dir, f"{file_name}{suffix}")
        shutil.copy(file_path, output_path)
        logging.info(f"文件 {file_name}{suffix} 未切分，直接复制")
        return

    # 解析论文标题、摘要和一级标题段落
    paper_title, abstract, sections = parse_markdown_sections(content)
    if not sections:
        logging.warning(f"文件 {file_path} 无内容，跳过")
        return

    # 默认标题
    paper_title = paper_title or "# Untitled"

    # 构造头部内容
    header = paper_title
    if abstract:
        header += "\n\n" + abstract

    # 按 chunk_size 切片
    chunks = []
    current_chunk = []
    current_length = len(header)  # 考虑头部长度

    for title, section_content in sections:
        section_length = len(section_content)
        if section_length > chunk_size:
            # 单一标题段落超过 chunk_size，直接按 chunk_size 切片
            start = 0
            while start < len(section_content):
                chunk = section_content[start:start + chunk_size]
                chunks.append(chunk)
                start += chunk_size
        else:
            # 尝试将段落加入当前切片
            if current_length + section_length <= chunk_size:
                current_chunk.append(section_content)
                current_length += section_length
            else:
                # 当前切片已满，保存并开始新切片
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))
                current_chunk = [section_content]
                current_length = len(header) + section_length

    # 保存最后一个切片
    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    # 保存切片文件
    for i, chunk in enumerate(chunks):
        output_path = os.path.join(output_dir, f"{file_name}-{i}{suffix}")
        try:
            with open(output_path, 'w', encoding='utf-8') as f_out:
                # 首行写入论文标题和摘要
                f_out.write(f"{header}\n\n{chunk}")
            logging.info(f"保存切片 {file_name}-{i}{suffix}")
        except Exception as e:
            logging.error(f"保存切片 {file_name}-{i}{suffix} 失败: {e}")

def process_files(input_dir: str, output_dir: str, concurrency: int) -> None:
    """处理文件夹中的文件并按大小并发切分

    主要实现方式：
    1. 确保输出文件夹存在。
    2. 获取输入文件夹中的 Markdown 文件，排除输出文件夹中已存在的文件。
    3. 按文件大小分类（小、中、大），优先处理小文件。
    4. 使用 ThreadPoolExecutor 并发处理文件。
    5. 记录输入、输出文件夹文件数量及处理结果。

    Args:
        input_dir (str): 输入文件夹路径
        output_dir (str): 输出文件夹路径
        concurrency (int): 并发线程数

    Returns:
        None
    """
    # 确保输出文件夹存在
    os.makedirs(output_dir, exist_ok=True)

    # 获取输入和输出文件夹的文件列表
    input_files = {f for f in os.listdir(input_dir) if f.endswith('.md')}
    output_files = set(os.listdir(output_dir))

    # 只处理输出文件夹中不存在的文件
    to_process = [os.path.join(input_dir, f) for f in input_files if f not in output_files]

    # 按文件大小分类
    small_files = []
    medium_files = []
    large_files = []

    for file_path in to_process:
        char_count = get_file_char_count(file_path)
        if char_count < 20000:
            small_files.append(file_path)
        elif 20000 <= char_count <= 100000:
            medium_files.append(file_path)
        else:
            large_files.append(file_path)

    # 日志记录
    logging.info(f"输入文件夹文件数量: {len(input_files)}")
    logging.info(f"输出文件夹文件数量: {len(output_files)}")

    # 按优先级并发处理
    all_files = [small_files, medium_files, large_files]
    for file_list in all_files:
        if file_list:
            with ThreadPoolExecutor(max_workers=concurrency) as executor:
                executor.map(lambda f: split_file(f, output_dir), file_list)

    # 处理完成后记录输出文件夹文件数量
    final_output_files = len(os.listdir(output_dir))
    logging.info(f"处理完成后输出文件夹文件数量: {final_output_files}")

if __name__ == "__main__":
    # 示例调用
    input_dir = r"D:\Project\1. Super_Computer\2025\c03_js_wang_OpenAI_use\project-2\data\c1_preprocess\c2_remove_reference"
    output_dir = r"D:\Project\1. Super_Computer\2025\c03_js_wang_OpenAI_use\project-2\data\c2_split_within_20000_document"
    concurrency = 4
    process_files(input_dir, output_dir, concurrency)