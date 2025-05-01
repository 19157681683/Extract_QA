# -*- coding: utf-8 -*-
"""
@author: 李林名
Created on 2025/3/25 12:21
"""

import os
import json
from typing import Dict, Any

def count_files_and_json_objects(folder_path: str) -> None:
    """
    统计文件夹中总文件数量、JSON总对象数量、含question的JSON总数量及其比例。

    主要实现方式：
        1. 遍历文件夹，统计总文件数量。
        2. 读取每个文件内容，解析为JSON对象。
        3. 统计所有JSON对象数量。
        4. 检查每个JSON对象是否包含"question"字段，统计数量。
        5. 计算比例并打印结果。

    入参说明：
        folder_path (str): 要统计的文件夹路径。

    返回结果说明：
        无返回值，直接打印统计结果。
    """
    total_files = 0
    total_json_objects = 0
    total_with_question = 0

    # 遍历文件夹
    for root, _, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            total_files += 1

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    data = json.loads(content)

                    # 检查是否为字典类型（JSON对象）
                    if isinstance(data, dict):
                        for key, value in data.items():
                            if isinstance(value, dict):
                                total_json_objects += 1
                                if "question" in value:
                                    total_with_question += 1
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                print(f"Error parsing file {file_name}: {e}")
                continue

    # 计算比例
    proportion = (total_with_question / total_json_objects * 100) if total_json_objects > 0 else 0

    # 打印统计结果
    print(f"统计结果：")
    print(f"总文件数量: {total_files}")
    print(f"总JSON对象数量: {total_json_objects}")
    print(f"含question的JSON数量: {total_with_question}")
    print(f"含有question的JSON比例: {proportion:.2f}%")

# 示例调用
if __name__ == "__main__":
    # window
    # folder_path = r"D:\Project\1. Super_Computer\2025\c03_js_wang_OpenAI_use\project-2\data\c3_extract_q"

    # linux
    folder_path = "/x32001214/project/2025/c03_js_wang_QA/project-2/data/c3_extract_q"  # 示例输入文件夹
    count_files_and_json_objects(folder_path)
