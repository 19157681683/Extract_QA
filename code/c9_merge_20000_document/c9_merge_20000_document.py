# -*- coding: utf-8 -*-
"""
@author: 李林名
Created on 2025/3/25 12:22
"""

import os
import json
import shutil
import logging
from typing import Dict, List

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_file_base_name(file_name: str) -> str:
    """
    获取文件的基础名称（去掉切割序号部分）

    Args:
        file_name (str): 文件名，例如 "普通用户手册-0.md.json"

    Returns:
        str: 基础文件名，例如 "普通用户手册"
    """
    if '-' in file_name and file_name.endswith('.md.json'):
        parts = file_name.split('-')
        # 检查最后一个部分是否为数字
        if parts[-1].replace('.md.json', '').isdigit():
            return '-'.join(parts[:-1])
    return file_name.replace('.md.json', '')


def load_json_file(file_path: str) -> Dict:
    """
    加载 JSON 文件内容

    Args:
        file_path (str): JSON 文件路径

    Returns:
        Dict: JSON 文件内容
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json_file(file_path: str, data: Dict) -> None:
    """
    保存 JSON 数据到文件

    Args:
        file_path (str): 输出文件路径
        data (Dict): 要保存的 JSON 数据
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def merge_json_files(input_dir: str, output_dir: str) -> None:
    """
    合并输入文件夹中的 JSON 文件，并保存到输出文件夹

    Args:
        input_dir (str): 输入文件夹路径
        output_dir (str): 输出文件夹路径
    """
    # 确保输出文件夹存在
    os.makedirs(output_dir, exist_ok=True)

    # 获取输入和输出文件夹中的文件列表
    input_files = set(os.listdir(input_dir))
    output_files = set(os.listdir(output_dir))

    # 获取基础文件名集合
    input_base_names = {get_file_base_name(f) for f in input_files if f.endswith('.md.json')}
    output_base_names = {f.replace('.json', '') for f in output_files if f.endswith('.json')}

    # 需要处理的文件（输入中有但输出中没有）
    to_process_base_names = input_base_names - output_base_names

    # 处理需要合并的文件
    for base_name in to_process_base_names:
        # 找到所有相关的切分文件
        related_files = [f for f in input_files if get_file_base_name(f) == base_name and f.endswith('.md.json')]

        if len(related_files) == 1 and not related_files[0].startswith(f"{base_name}-"):
            # 无序号文件，直接复制
            src_path = os.path.join(input_dir, related_files[0])
            dst_path = os.path.join(output_dir, f"{base_name}.json")
            shutil.copy(src_path, dst_path)
            continue

        # 按切割序号排序
        related_files.sort(key=lambda x: int(x.split('-')[-1].replace('.md.json', '')) if '-' in x else 0)

        # 合并 JSON 数据
        merged_json: Dict[str, Dict] = {}
        current_idx = 0
        for file_name in related_files:
            file_path = os.path.join(input_dir, file_name)
            json_data = load_json_file(file_path)
            for key in sorted(json_data.keys(), key=int):
                merged_json[str(current_idx)] = json_data[key]
                current_idx += 1

        # 保存合并后的 JSON 文件
        output_file = os.path.join(output_dir, f"{base_name}.json")
        save_json_file(output_file, merged_json)

    # 打印日志
    input_file_count = len([f for f in input_files if f.endswith('.md.json')])
    output_file_count = len([f for f in os.listdir(output_dir) if f.endswith('.json')])
    logger.info(f"输入文件夹文件数量: {input_file_count}")
    logger.info(f"输出文件夹文件数量: {output_file_count}")


def main():
    """
    主函数，执行文件合并任务
    """
    # # window部署
    # input_dir = r"D:\Project\1. Super_Computer\2025\c03_js_wang_OpenAI_use\project-2\data\c8_check_a"  # 输入文件夹路径
    # output_dir = r"D:\Project\1. Super_Computer\2025\c03_js_wang_OpenAI_use\project-2\data\c9_merge_20000_document"  # 输出文件夹路径


    # linux
    input_dir = "/x32001214/project/2025/c03_js_wang_QA/project-2/data/c8_check_a"  # 输入文件夹路径
    output_dir = "/x32001214/project/2025/c03_js_wang_QA/project-2/data/c9_merge_20000_document"  # 输出文件夹路径
    merge_json_files(input_dir, output_dir)


if __name__ == "__main__":
    main()
