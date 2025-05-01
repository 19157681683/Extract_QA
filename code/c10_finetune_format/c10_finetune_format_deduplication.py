#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：c07_superComputer_li_knowledge-base
@File    ：c10_finetune_format_deduplication.py
@IDE     ：PyCharm
@Author  ：李林名
@Date    ：2025/4/8 9:21
@Usage   ：
'''
import json
import os
from typing import List, Dict, Any
import logging

# 配置日志格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def read_json_file(file_path: str) -> List[Dict[str, Any]]:
    """
    读取JSON文件并返回解析后的数据

    参数:
        file_path (str): JSON文件路径

    返回:
        List[Dict[str, Any]]: 解析后的JSON数据列表
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {str(e)}")
        raise

def deduplicate_instructions(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    对JSON数据中的instruction字段进行去重，并去除instruction为空的对象

    参数:
        data (List[Dict[str, Any]]): 原始JSON数据

    返回:
        List[Dict[str, Any]]: 去重后的数据
    """
    seen_instructions = set()
    deduplicated_data = []
    duplicates_count = 0
    empty_instruction_count = 0

    for item in data:
        instruction = item.get('instruction', '')
        if instruction == '':
            empty_instruction_count += 1
            continue
        if instruction not in seen_instructions:
            seen_instructions.add(instruction)
            deduplicated_data.append(item)
        else:
            duplicates_count += 1

    logger.info(f"Removed {duplicates_count} duplicate instructions")
    logger.info(f"Removed {empty_instruction_count} items with empty instructions")
    return deduplicated_data

def write_json_file(data: List[Dict[str, Any]], file_path: str) -> None:
    """
    将数据写入JSON文件

    参数:
        data (List[Dict[str, Any]]): 要写入的数据
        file_path (str): 输出文件路径
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error writing file {file_path}: {str(e)}")
        raise

def process_json_files(input_dir: str, output_dir: str) -> None:
    """
    处理输入文件夹中的所有JSON文件，去重后保存到输出文件夹

    参数:
        input_dir (str): 输入文件夹路径
        output_dir (str): 输出文件夹路径
    """
    if not os.path.exists(input_dir):
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logger.info(f"Created output directory: {output_dir}")

    total_files = 0
    total_duplicates = 0
    total_original = 0
    total_deduplicated = 0

    for filename in os.listdir(input_dir):
        if filename.endswith('.json'):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)

            try:
                # 读取原始数据
                data = read_json_file(input_path)
                original_count = len(data)
                total_original += original_count

                # 去重处理
                deduplicated_data = deduplicate_instructions(data)
                deduplicated_count = len(deduplicated_data)
                total_deduplicated += deduplicated_count
                total_duplicates += (original_count - deduplicated_count)

                # 写入结果
                write_json_file(deduplicated_data, output_path)
                total_files += 1

                logger.info(f"Processed {filename}: original={original_count}, deduplicated={deduplicated_count}")

            except Exception as e:
                logger.error(f"Failed to process file {filename}: {str(e)}")
                continue

    # 汇总日志
    logger.info("\n=== Summary ===")
    logger.info(f"Total files processed: {total_files}")
    logger.info(f"Total original records: {total_original}")
    logger.info(f"Total deduplicated records: {total_deduplicated}")
    logger.info(f"Total duplicates removed: {total_duplicates}")

def main():
    """
    主函数，不需要命令行参数
    """
    # 这里设置你的输入输出路径
    # # window部署
    # input_directory = r"D:\Project\1. Super_Computer\2025\c03_js_wang_OpenAI_use\project-2\data\c10_finetune_format\c1_source"  # 修改为你的输入文件夹路径
    # output_directory = r"D:\Project\1. Super_Computer\2025\c03_js_wang_OpenAI_use\project-2\data\c10_finetune_format\c2_deduplication"  # 修改为你的输出文件夹路径

    # linux
    input_directory = "/x32001214/project/2025/c03_js_wang_QA/project-2/data/c10_finetune_format\c1_source"  # 修改为你的输入文件夹路径
    output_directory = "/x32001214/project/2025/c03_js_wang_QA/project-2/data/c10_finetune_format\c2_deduplication"  # 修改为你的输出文件夹路径

    try:
        logger.info("Starting JSON instruction deduplication process")
        process_json_files(input_directory, output_directory)
        logger.info("Process completed successfully")
    except Exception as e:
        logger.error(f"Process failed: {str(e)}")

if __name__ == "__main__":
    main()