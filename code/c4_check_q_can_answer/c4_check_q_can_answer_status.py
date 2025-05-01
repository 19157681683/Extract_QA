#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：project-2 
@File    ：c4_check_q_can_answer_status.py
@IDE     ：PyCharm 
@Author  ：李林名
@Date    ：2025/4/29 11:11 
@Usage   ：检测校验Q能否回答的效果
'''
import os
import json
from typing import Tuple


def read_json_files(folder_path: str) -> list:
    """
    读取指定文件夹中的所有 JSON 文件内容。

    主要实现方式：
        遍历指定文件夹，筛选以 .json 结尾的文件，读取并解析 JSON 内容。

    入参说明：
        folder_path (str): 文件夹路径。

    返回结果说明：
        list: 包含所有 JSON 文件内容的列表，每个元素为解析后的 JSON 数据（通常为 dict 或 list）。

    Raises:
        FileNotFoundError: 如果文件夹路径不存在。
        json.JSONDecodeError: 如果 JSON 文件格式错误。
    """
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"文件夹路径 {folder_path} 不存在")

    json_data_list = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                    json_data_list.append(json_data)
            except json.JSONDecodeError as e:
                print(f"警告: 文件 {filename} 格式错误，无法解析: {e}")
            except Exception as e:
                print(f"警告: 读取文件 {filename} 失败: {e}")

    return json_data_list


def analyze_json_data(json_data_list: list) -> Tuple[int, int, int]:
    """
    分析 JSON 数据，统计对象总数、question 总数和 check_question_can_answer 为 true 的总数。

    主要实现方式：
        遍历 JSON 数据，统计每条记录的字段信息，累计总数。

    入参说明：
        json_data_list (list): 包含所有 JSON 文件内容的列表。

    返回结果说明：
        Tuple[int, int, int]: 包含以下三个值的元组：
            - total_objects: JSON 对象总数。
            - total_questions: question 非空记录总数。
            - total_true_answers: check_question_can_answer 为 true 的记录总数。
    """
    total_objects = 0
    total_questions = 0
    total_true_answers = 0

    for json_data in json_data_list:
        # 假设 JSON 数据为字典，键为记录 ID，值为记录内容
        for record in json_data.values():
            total_objects += 1
            # 检查 question 字段是否非空
            if record.get('question', '').strip():
                total_questions += 1
            # 检查 check_question_can_answer 是否为 true
            check_value = record.get('check_question_can_answer')
            if isinstance(check_value, bool) and check_value:
                total_true_answers += 1
            elif isinstance(check_value, str) and check_value.lower() == 'true':
                total_true_answers += 1

    return total_objects, total_questions, total_true_answers


def print_log_summary(folder_path: str) -> None:
    """
    打印文件夹中 JSON 日志的统计信息。

    主要实现方式：
        调用 read_json_files 和 analyze_json_data 函数，统计并格式化输出结果。

    入参说明：
        folder_path (str): 文件夹路径。

    返回结果说明：
        None: 直接打印统计结果到控制台。
    """
    try:
        # 读取 JSON 文件
        json_data_list = read_json_files(folder_path)

        # 分析数据
        total_objects, total_questions, total_true_answers = analyze_json_data(json_data_list)

        # 计算比例
        question_ratio = (total_questions / total_objects * 100) if total_objects > 0 else 0
        true_answer_ratio = (total_true_answers / total_questions * 100) if total_questions > 0 else 0

        # 打印结果
        print("日志统计结果：")
        print(f"JSON 对象总数: {total_objects}")
        print(f"question 总数: {total_questions}")
        print(f"question 总数占 JSON 总数比例: {question_ratio:.2f}%")
        print(f"check_question_can_answer 为 true 总数: {total_true_answers}")
        print(f"check_question_can_answer 为 true 总数 / question 总数比例: {true_answer_ratio:.2f}%")

    except Exception as e:
        print(f"错误: 处理日志时发生异常: {e}")


if __name__ == "__main__":
    # 示例用法
    # # window
    # folder_path = r"D:\Project\1. Super_Computer\2025\c03_js_wang_OpenAI_use\project-2\data\c4_check_q_can_answer"  # 替换为实际文件夹路径

    # linux
    folder_path = "/x32001214/project/2025/c03_js_wang_QA/project-2/data/c4_check_q_can_answer"  # 替换为实际文件夹路径
    print_log_summary(folder_path)