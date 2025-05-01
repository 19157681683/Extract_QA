# -*- coding: utf-8 -*-
"""
@author: 李林名
Created on 2025/3/26 18:21
"""

import os
import json
from typing import Dict, List


def process_json_files(input_folder: str, output_folder: str) -> None:
    """
    处理输入文件夹中的JSON文件，将其转换为统一的格式并保存到输出文件夹

    参数:
        input_folder (str): 输入文件夹路径
        output_folder (str): 输出文件夹路径

    返回:
        None
    """
    # 确保输出文件夹存在
    os.makedirs(output_folder, exist_ok=True)

    # 初始化结果列表
    result_data = []

    # 统计文件数量
    file_count = 0
    processed_entries = 0

    # 遍历输入文件夹
    for filename in os.listdir(input_folder):
        if filename.endswith('.json'):
            file_path = os.path.join(input_folder, filename)
            file_count += 1

            try:
                # 读取JSON文件
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # 处理每个条目
                for key, entry in data.items():
                    if isinstance(entry, dict) and 'expand_question' in entry and 'answer' in entry:
                        # 构建新的JSON对象
                        new_entry = {
                            "instruction": entry["expand_question"],
                            "input": "",
                            "output": entry["answer"]
                        }
                        result_data.append(new_entry)
                        processed_entries += 1

                print(f"处理完成: {filename} (共处理 {len(data)} 个条目)")

            except Exception as e:
                print(f"处理文件 {filename} 时出错: {str(e)}")

    # 输出统计信息
    print(f"\n处理完成 - 总文件数: {file_count}, 总处理条目数: {processed_entries}")

    # 将结果写入输出文件
    output_path = os.path.join(output_folder, 'super_computer.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)

    print(f"\n结果已保存到: {output_path}")


def main():
    # 示例用法
    # # window部署
    # input_folder = r"D:\Project\1. Super_Computer\2025\c03_js_wang_OpenAI_use\project-2\data\c9_merge_20000_document"  # 替换为实际输入文件夹路径
    # output_folder = r"D:\Project\1. Super_Computer\2025\c03_js_wang_OpenAI_use\project-2\data\c10_finetune_format\c1_source"  # 替换为实际输出文件夹路径

    # linux
    input_folder = "/x32001214/project/2025/c03_js_wang_QA/project-2/data/c9_merge_20000_document"  # 替换为实际输入文件夹路径
    output_folder = "/x32001214/project/2025/c03_js_wang_QA/project-2/data/c10_finetune_format\c1_source"  # 替换为实际输出文件夹路径

    print("开始处理JSON文件...\n")
    process_json_files(input_folder, output_folder)


if __name__ == "__main__":
    main()