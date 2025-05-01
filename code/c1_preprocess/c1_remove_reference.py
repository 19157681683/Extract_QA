#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：project-2 
@File    ：c1_remove_reference.py
@IDE     ：PyCharm 
@Author  ：李林名
@Date    ：2025/4/27 14:17 
@Usage   ：删除原始论文文本中Reference部分
'''
import os
import re
import logging
from pathlib import Path
import shutil


def setup_logging():
    """
    配置日志记录
    主要实现方式：使用logging模块配置日志，输出到控制台
    返回结果：无
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def count_files(input_dir: str) -> int:
    """
    统计输入文件夹中的Markdown文件数量
    主要实现方式：遍历文件夹，筛选扩展名为.md的文件
    入参说明：
        input_dir (str): 输入文件夹路径
    返回结果：
        int: Markdown文件数量
    """
    try:
        input_path = Path(input_dir)
        md_files = list(input_path.glob('*.md'))
        return len(md_files)
    except Exception as e:
        logging.error(f"统计文件数量失败: {str(e)}")
        return 0


def create_output_dir(output_dir: str) -> bool:
    """
    创建输出文件夹
    主要实现方式：检查输出文件夹是否存在，不存在则创建
    入参说明：
        output_dir (str): 输出文件夹路径
    返回结果：
        bool: 创建是否成功
    """
    try:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logging.error(f"创建输出文件夹失败: {str(e)}")
        return False


def process_file(input_file: str, output_file: str) -> bool:
    """
    处理单个Markdown文件，删除Reference部分
    主要实现方式：读取文件，匹配Reference部分，保留之前内容，写入新文件
    入参说明：
        input_file (str): 输入文件路径
        output_file (str): 输出文件路径
    返回结果：
        bool: 处理是否成功
    """
    try:
        # 读取文件内容
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 匹配Reference部分的正则表达式
        reference_pattern = r'^(#+)\s*(References?|Bibliography)\s*$'
        lines = content.split('\n')
        output_lines = []
        in_reference_section = False

        for line in lines:
            # 检查是否进入Reference部分
            if not in_reference_section and re.match(reference_pattern, line, re.IGNORECASE):
                in_reference_section = True
                continue
            # 如果不在Reference部分，保留该行
            if not in_reference_section:
                output_lines.append(line)

        # 写入处理后的内容
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_lines))
        return True
    except Exception as e:
        logging.error(f"处理文件 {input_file} 失败: {str(e)}")
        return False


def remove_references(input_dir: str, output_dir: str) -> None:
    """
    删除文件夹中所有Markdown文件的Reference部分
    主要实现方式：遍历输入文件夹，处理每个文件，保存到输出文件夹
    入参说明：
        input_dir (str): 输入文件夹路径
        output_dir (str): 输出文件夹路径
    返回结果：
        None
    """
    setup_logging()

    # 统计文件数量
    file_count = count_files(input_dir)
    logging.info(f"输入文件夹中共有 {file_count} 个Markdown文件")

    # 创建输出文件夹
    if not create_output_dir(output_dir):
        return

    # 处理每个文件
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    for input_file in input_path.glob('*.md'):
        output_file = output_path / input_file.name
        logging.info(f"正在处理文件: {input_file}")
        if process_file(input_file, output_file):
            logging.info(f"成功处理文件: {input_file} -> {output_file}")
        else:
            logging.error(f"处理文件失败: {input_file}")


if __name__ == "__main__":
    # 示例用法
    input_directory = r"D:\Project\1. Super_Computer\2025\c03_js_wang_OpenAI_use\project-2\data\c1_preprocess\c1_rename_file"
    output_directory = r"D:\Project\1. Super_Computer\2025\c03_js_wang_OpenAI_use\project-2\data\c1_preprocess\c2_remove_reference"
    remove_references(input_directory, output_directory)