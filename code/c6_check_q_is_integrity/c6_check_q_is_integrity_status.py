#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：project-2 
@File    ：c6_check_q_is_integrity_status.py
@IDE     ：PyCharm 
@Author  ：李林名
@Date    ：2025/4/29 11:21 
@Usage   ：
'''
import os
import json
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def list_json_files(folder_path: str) -> list:
    """
    遍历指定文件夹，获取所有 JSON 文件的路径列表。

    主要实现方式：
        使用 os.walk 递归遍历文件夹，筛选出以 .json 结尾的文件。

    入参说明：
        folder_path (str): 输入文件夹路径。

    返回结果说明：
        list: 包含所有 JSON 文件路径的列表。

    """
    json_files = []
    try:
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith('.json'):
                    json_files.append(os.path.join(root, file))
        return json_files
    except Exception as e:
        logger.error(f"遍历文件夹 {folder_path} 失败: {e}")
        return []


def process_json_file(file_path: str) -> dict:
    """
    处理单个 JSON 文件，统计相关指标。

    主要实现方式：
        读取 JSON 文件，解析为字典，遍历每个键值对，统计 question、check_question_can_answer、
        expand_question 和 check_question_is_integrity 相关的指标。

    入参说明：
        file_path (str): JSON 文件的路径。

    返回结果说明：
        dict: 包含以下统计指标的字典：
            - json_objects: JSON 对象总数
            - question_objects: question 对象总数
            - can_answer_true: check_question_can_answer 为 True 的总数
            - expand_question_not_empty: expand_question 非空总数
            - integrity_true: check_question_is_integrity 为 True 的总数
    """
    stats = {
        'json_objects': 0,
        'question_objects': 0,
        'can_answer_true': 0,
        'expand_question_not_empty': 0,
        'integrity_true': 0
    }

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 统计 JSON 对象总数
        stats['json_objects'] = len(data)

        # 遍历每个 JSON 对象
        for key, value in data.items():
            # 统计 question 对象
            if 'question' in value and value['question']:
                stats['question_objects'] += 1

            # 统计 check_question_can_answer 为 True
            if value.get('check_question_can_answer') is True:
                stats['can_answer_true'] += 1

            # 统计 expand_question 非空
            if 'expand_question' in value and value['expand_question']:
                stats['expand_question_not_empty'] += 1

            # 统计 check_question_is_integrity 为 True
            if value.get('check_question_is_integrity') is True:
                stats['integrity_true'] += 1

        logger.info(f"文件 {file_path} 统计结果: {stats}")
        return stats

    except json.JSONDecodeError as e:
        logger.error(f"解析 JSON 文件 {file_path} 失败: {e}")
        return stats
    except Exception as e:
        logger.error(f"处理文件 {file_path} 失败: {e}")
        return stats


def calculate_stats(folder_path: str) -> None:
    """
    统计指定文件夹中所有 JSON 文件的相关指标，并输出汇总结果。

    主要实现方式：
        调用 list_json_files 获取 JSON 文件列表，逐个调用 process_json_file 统计指标，
        汇总所有文件的统计结果，计算占比并输出。

    入参说明：
        folder_path (str): 输入文件夹路径。

    返回结果说明：
        None: 直接通过日志输出统计结果。
    """
    # 获取 JSON 文件列表
    json_files = list_json_files(folder_path)
    total_stats = {
        'file_count': len(json_files),
        'json_objects': 0,
        'question_objects': 0,
        'can_answer_true': 0,
        'expand_question_not_empty': 0,
        'integrity_true': 0
    }

    # 处理每个 JSON 文件
    for file_path in json_files:
        file_stats = process_json_file(file_path)
        total_stats['json_objects'] += file_stats['json_objects']
        total_stats['question_objects'] += file_stats['question_objects']
        total_stats['can_answer_true'] += file_stats['can_answer_true']
        total_stats['expand_question_not_empty'] += file_stats['expand_question_not_empty']
        total_stats['integrity_true'] += file_stats['integrity_true']

    # 计算占比
    json_objects = total_stats['json_objects']
    if json_objects > 0:
        question_ratio = total_stats['question_objects'] / json_objects * 100
        can_answer_ratio = total_stats['can_answer_true'] / json_objects * 100
        expand_question_ratio = total_stats['expand_question_not_empty'] / json_objects * 100
        integrity_ratio = total_stats['integrity_true'] / json_objects * 100
    else:
        question_ratio = 0
        can_answer_ratio = 0
        expand_question_ratio = 0
        integrity_ratio = 0

    # 输出汇总统计
    logger.info("\n=== 汇总统计结果 ===")
    logger.info(f"文件总数: {total_stats['file_count']}")
    logger.info(f"JSON 对象总数: {total_stats['json_objects']}")
    logger.info(f"question 对象总数: {total_stats['question_objects']}")
    logger.info(f"question 对象总数 / JSON 对象总数占比: {question_ratio:.2f}%")
    logger.info(f"check_question_can_answer 为 True 总数: {total_stats['can_answer_true']}")
    logger.info(f"check_question_can_answer 为 True 总数 / JSON 对象总数占比: {can_answer_ratio:.2f}%")
    logger.info(f"expand_question 非空总数: {total_stats['expand_question_not_empty']}")
    logger.info(f"expand_question 非空总数 / JSON 对象总数占比: {expand_question_ratio:.2f}%")
    logger.info(f"check_question_is_integrity 为 True 总数: {total_stats['integrity_true']}")
    logger.info(f"check_question_is_integrity 为 True 总数 / JSON 对象总数占比: {integrity_ratio:.2f}%")


if __name__ == "__main__":
    # 示例调用
    # # window部署
    # folder_path = r"D:\Project\1. Super_Computer\2025\c03_js_wang_OpenAI_use\project-2\data\c6_check_q_is_integrity"
    # linux
    folder_path = "/x32001214/project/2025/c03_js_wang_QA/project-2/data/c6_check_q_is_integrity"
    if not Path(folder_path).is_dir():
        logger.error(f"路径 {folder_path} 不是有效的文件夹")
    else:
        calculate_stats(folder_path)