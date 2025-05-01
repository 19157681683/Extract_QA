#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：project-2 
@File    ：c5_expand_q_integrity_status.py
@IDE     ：PyCharm 
@Author  ：李林名
@Date    ：2025/4/28 16:58 
@Usage   ：统计指定文件夹中 JSON 文件的相关信息，包括文件总数、JSON 对象总数、question 对象总数、以及特定字段的统计数据（如 check_question_can_answer 为 true 的总数、expand_question 非空的总数等）
'''

import os
import json
import logging
from typing import Dict, Tuple
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def list_json_files(folder_path: str) -> list[str]:
    """
    主要实现方式：递归遍历指定文件夹，筛选出所有以 .json 结尾的文件路径。

    入参说明：
        folder_path (str): 输入的文件夹路径。

    返回结果说明：
        list[str]: 包含所有 JSON 文件路径的列表。
    """
    json_files = []
    try:
        folder = Path(folder_path)
        if not folder.exists() or not folder.is_dir():
            logger.error(f"路径 {folder_path} 不存在或不是文件夹")
            return json_files

        for file_path in folder.rglob("*.json"):
            json_files.append(str(file_path))
        logger.info(f"找到 {len(json_files)} 个 JSON 文件")
        return json_files
    except Exception as e:
        logger.error(f"遍历文件夹 {folder_path} 时出错: {e}")
        return json_files

def parse_json_file(file_path: str) -> Dict:
    """
    主要实现方式：读取并解析 JSON 文件内容，返回字典格式的数据。

    入参说明：
        file_path (str): JSON 文件的路径。

    返回结果说明：
        Dict: 解析后的 JSON 数据。如果解析失败，返回空字典。
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.info(f"成功解析文件: {file_path}")
            return data
    except json.JSONDecodeError as e:
        logger.error(f"解析 JSON 文件 {file_path} 失败: {e}")
        return {}
    except Exception as e:
        logger.error(f"读取文件 {file_path} 时出错: {e}")
        return {}

def analyze_json_data(data: Dict) -> Tuple[int, int, int, int]:
    """
    主要实现方式：分析 JSON 数据，统计 JSON 对象数、question 对象数、check_question_can_answer 为 true 的数、expand_question 非空数。

    入参说明：
        data (Dict): 解析后的 JSON 数据。

    返回结果说明：
        Tuple[int, int, int, int]: 包含以下统计结果的元组：
            - JSON 对象总数
            - question 对象总数
            - check_question_can_answer 为 true 的总数
            - expand_question 非空总数
    """
    json_object_count = 0
    question_count = 0
    can_answer_count = 0
    expand_question_count = 0

    for key, value in data.items():
        json_object_count += 1
        if isinstance(value, dict):
            if "question" in value:
                question_count += 1
            if value.get("check_question_can_answer") is True:
                can_answer_count += 1
            if value.get("expand_question") and value["expand_question"].strip():
                expand_question_count += 1

    return json_object_count, question_count, can_answer_count, expand_question_count

def compute_statistics(folder_path: str) -> Dict[str, float]:
    """
    主要实现方式：统计指定文件夹中所有 JSON 文件的相关数据，并计算所需的统计指标。

    入参说明：
        folder_path (str): 输入的文件夹路径。

    返回结果说明：
        Dict[str, float]: 包含以下统计结果的字典：
            - file_count: 文件总数
            - json_object_count: JSON 对象总数
            - question_count: question 对象总数
            - question_ratio: question 对象总数/JSON 对象总数
            - can_answer_count: check_question_can_answer 为 true 的总数
            - can_answer_ratio: check_question_can_answer 为 true 总数/JSON 对象总数
            - expand_question_count: expand_question 非空总数
            - expand_question_ratio: expand_question 非空总数/JSON 对象总数
    """
    json_files = list_json_files(folder_path)
    total_json_objects = 0
    total_questions = 0
    total_can_answer = 0
    total_expand_questions = 0

    for file_path in json_files:
        data = parse_json_file(file_path)
        if data:
            json_count, question_count, can_answer_count, expand_count = analyze_json_data(data)
            total_json_objects += json_count
            total_questions += question_count
            total_can_answer += can_answer_count
            total_expand_questions += expand_count

    # 计算比例，防止除零错误
    question_ratio = total_questions / total_json_objects if total_json_objects > 0 else 0.0
    can_answer_ratio = total_can_answer / total_json_objects if total_json_objects > 0 else 0.0
    expand_question_ratio = total_expand_questions / total_json_objects if total_json_objects > 0 else 0.0

    stats = {
        "file_count": len(json_files),
        "json_object_count": total_json_objects,
        "question_count": total_questions,
        "question_ratio": question_ratio,
        "can_answer_count": total_can_answer,
        "can_answer_ratio": can_answer_ratio,
        "expand_question_count": total_expand_questions,
        "expand_question_ratio": expand_question_ratio
    }

    logger.info("统计结果：")
    for key, value in stats.items():
        logger.info(f"{key}: {value}")

    return stats

if __name__ == "__main__":
    # 示例用法
    # # window部署
    # folder_path = r"D:\Project\1. Super_Computer\2025\c03_js_wang_OpenAI_use\project-2\data\c5_expand_q_integrity"

    # linux
    folder_path = "/x32001214/project/2025/c03_js_wang_QA/project-2/data/c5_expand_q_integrity"
    stats = compute_statistics(folder_path)
    print("统计结果：")
    for key, value in stats.items():
        print(f"{key}: {value}")