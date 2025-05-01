#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：c07_superComputer_li_knowledge-base
@File    ：c10_finetune_format_deduplication_status.py
@IDE     ：PyCharm
@Author  ：李林名
@Date    ：2025/4/8 9:25
@Usage   ：对指定文件夹中的所有JSON文件进行instruction字段去重分析
'''

import json
import os
from collections import defaultdict


def load_json_file(file_path):
    """
    加载JSON文件
    :param file_path: JSON文件路径
    :return: 解析后的JSON数据（列表形式）
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data


def check_duplicate_instructions(data):
    """
    检查JSON数据中instruction字段的重复情况
    :param data: JSON数据（列表形式，每个元素是一个字典）
    :return:
        - duplicate_count: 重复的instruction数量（出现次数大于1的instruction的数量）
        - unique_count: 非重复的instruction数量（出现次数等于1的instruction的数量）
        - total_count: 总的instruction数量
        - deduplicate_ratio: 去重后的instruction占总instruction的比例
        - instruction_counts: 每个instruction及其出现次数的字典
    """
    instruction_counts = defaultdict(int)
    for item in data:
        instruction = item.get('instruction', '')
        instruction_counts[instruction] += 1

    total_count = len(data)
    duplicate_count = sum(1 for count in instruction_counts.values() if count > 1)
    unique_count = sum(1 for count in instruction_counts.values() if count == 1)
    deduplicate_ratio = (duplicate_count + unique_count) / total_count if total_count > 0 else 0.0

    return duplicate_count, unique_count, total_count, deduplicate_ratio, instruction_counts


def print_duplicate_info(file_name, duplicate_count, unique_count, total_count, deduplicate_ratio):
    """
    打印重复的instruction信息
    :param file_name: 当前处理的文件名
    :param duplicate_count: 重复的instruction数量
    :param unique_count: 非重复的instruction数量
    :param total_count: 总的instruction数量
    :param deduplicate_ratio: 去重后的instruction比例
    """
    print(f"\n文件: {file_name}")
    print(f"  重复的instruction数量: {duplicate_count}")
    print(f"  非重复的instruction数量: {unique_count}")
    print(f"  去重的instruction总数量: {duplicate_count + unique_count}")
    print(f"  instruction总数量: {total_count}")
    print(f"  去重instruction比例: {deduplicate_ratio:.2%}")


def process_folder(folder_path):
    """
    处理文件夹中的所有JSON文件
    :param folder_path: 文件夹路径
    """
    if not os.path.isdir(folder_path):
        print(f"错误：路径 {folder_path} 不是有效的文件夹")
        return

    json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
    if not json_files:
        print(f"警告：文件夹 {folder_path} 中没有找到JSON文件")
        return

    print(f"开始分析文件夹: {folder_path}")
    print(f"找到 {len(json_files)} 个JSON文件")

    for file_name in json_files:
        file_path = os.path.join(folder_path, file_name)
        try:
            data = load_json_file(file_path)
            duplicate_count, unique_count, total_count, deduplicate_ratio, _ = check_duplicate_instructions(data)
            print_duplicate_info(file_name, duplicate_count, unique_count, total_count, deduplicate_ratio)
        except FileNotFoundError:
            print(f"错误：文件 {file_name} 未找到")
        except json.JSONDecodeError:
            print(f"错误：文件 {file_name} 不是有效的JSON格式")
        except Exception as e:
            print(f"处理文件 {file_name} 时发生错误: {str(e)}")


def main():
    # 修改为您的文件夹路径
    # # window部署
    # folder_path = r'D:\Project\1. Super_Computer\2025\c03_js_wang_OpenAI_use\project-2\data\c10_finetune_format\c2_deduplication'

    folder_path = '/x32001214/project/2025/c03_js_wang_QA/project-2/data/c10_finetune_format/c2_deduplication'
    process_folder(folder_path)


if __name__ == "__main__":
    main()