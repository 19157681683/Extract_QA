# -*- coding: utf-8 -*-
"""
@author: 李林名
Created on 2025/3/25 12:22
Updated on 2025/4/29 to include check_answer_is_correct statistics
"""
import os
import json
import logging
from typing import Dict, List, Tuple
from pathlib import Path
import uuid

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_json_files(input_dir: str) -> List[str]:
    """
    获取输入文件夹中所有 JSON 文件的列表。

    主要实现方式：
        - 使用 os.listdir 遍历输入文件夹。
        - 过滤出以 .json 结尾的文件。

    入参说明：
        - input_dir (str): 输入文件夹路径。

    返回结果说明：
        - List[str]: JSON 文件名列表。
    """
    try:
        json_files = [
            f for f in os.listdir(input_dir)
            if f.endswith('.json') and os.path.isfile(os.path.join(input_dir, f))
        ]
        logger.info(f"找到 {len(json_files)} 个 JSON 文件")
        return json_files
    except Exception as e:
        logger.error(f"获取 JSON 文件列表失败: {e}")
        return []

def process_json_file(file_path: str) -> Tuple[int, Dict[str, int]]:
    """
    处理单个 JSON 文件，统计相关指标。

    主要实现方式：
        - 读取 JSON 文件内容。
        - 遍历 JSON 对象，统计 question, check_question_can_answer, expand_question,
          check_question_is_integrity, answer, check_answer_is_correct 相关的指标。
        - 返回 JSON 对象总数和各指标的计数。

    入参说明：
        - file_path (str): JSON 文件的完整路径。

    返回结果说明：
        - Tuple[int, Dict[str, int]]: 包含 JSON 对象总数和指标计数字典。
          计数字典包含以下键：
            - question_count: 包含 question 字段的对象数
            - can_answer_count: check_question_can_answer 为 true 的对象数
            - expand_question_count: expand_question 非空的对象数
            - integrity_count: check_question_is_integrity 为 true 的对象数
            - answer_count: answer 非空的对象数
            - correct_answer_count: check_answer_is_correct 为 true 的对象数
    """
    stats = {
        "question_count": 0,
        "can_answer_count": 0,
        "expand_question_count": 0,
        "integrity_count": 0,
        "answer_count": 0,
        "correct_answer_count": 0
    }
    json_object_count = 0

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 确保 data 是字典
        if not isinstance(data, dict):
            logger.warning(f"文件 {file_path} 的 JSON 格式不正确，跳过")
            return 0, stats

        json_object_count = len(data)
        for entry in data.values():
            # 统计 question
            if entry.get("question"):
                stats["question_count"] += 1

            # 统计 check_question_can_answer
            if entry.get("check_question_can_answer") is True:
                stats["can_answer_count"] += 1

            # 统计 expand_question 非空
            if entry.get("expand_question") and entry["expand_question"].strip():
                stats["expand_question_count"] += 1

            # 统计 check_question_is_integrity
            if entry.get("check_question_is_integrity") is True:
                stats["integrity_count"] += 1

            # 统计 answer 非空
            if entry.get("answer") and entry["answer"].strip():
                stats["answer_count"] += 1

            # 统计 check_answer_is_correct
            if entry.get("check_answer_is_correct") is True:
                stats["correct_answer_count"] += 1

        logger.info(f"处理文件 {file_path} 完成，JSON 对象数: {json_object_count}")
        return json_object_count, stats

    except json.JSONDecodeError as e:
        logger.error(f"解析 JSON 文件 {file_path} 失败: {e}")
        return 0, stats
    except Exception as e:
        logger.error(f"处理文件 {file_path} 时发生异常: {e}")
        return 0, stats

def calculate_statistics(input_dir: str) -> Dict[str, float]:
    """
    计算所有 JSON 文件的统计指标。

    主要实现方式：
        - 遍历所有 JSON 文件，调用 process_json_file 统计各文件指标。
        - 汇总文件总数、JSON 对象总数和各指标计数。
        - 计算各指标的占比（相对于 JSON 对象总数）。
        - 返回包含所有统计结果的字典。

    入参说明：
        - input_dir (str): 输入文件夹路径。

    返回结果说明：
        - Dict[str, float]: 包含以下统计指标的字典：
            - file_count: 文件总数
            - json_object_count: JSON 对象总数
            - question_count: question 对象总数
            - question_ratio: question 对象占比
            - can_answer_count: check_question_can_answer 为 true 的总数
            - can_answer_ratio: check_question_can_answer 为 true 的占比
            - expand_question_count: expand_question 非空总数
            - expand_question_ratio: expand_question 非空占比
            - integrity_count: check_question_is_integrity 为 true 的总数
            - integrity_ratio: check_question_is_integrity 为 true 的占比
            - answer_count: answer 总数
            - answer_ratio: answer 占比
            - correct_answer_count: check_answer_is_correct 为 true 的总数
            - correct_answer_ratio: check_answer_is_correct 为 true 的占比
    """
    stats = {
        "file_count": 0,
        "json_object_count": 0,
        "question_count": 0,
        "can_answer_count": 0,
        "expand_question_count": 0,
        "integrity_count": 0,
        "answer_count": 0,
        "correct_answer_count": 0
    }

    # 获取 JSON 文件列表
    json_files = get_json_files(input_dir)
    stats["file_count"] = len(json_files)

    if not json_files:
        logger.warning("输入文件夹中没有 JSON 文件")
        return stats

    # 处理每个 JSON 文件
    for filename in json_files:
        file_path = os.path.join(input_dir, filename)
        json_count, file_stats = process_json_file(file_path)
        stats["json_object_count"] += json_count
        for key in file_stats:
            stats[key] += file_stats[key]

    # 计算占比
    json_count = stats["json_object_count"]
    stats["question_ratio"] = stats["question_count"] / json_count if json_count > 0 else 0.0
    stats["can_answer_ratio"] = stats["can_answer_count"] / json_count if json_count > 0 else 0.0
    stats["expand_question_ratio"] = stats["expand_question_count"] / json_count if json_count > 0 else 0.0
    stats["integrity_ratio"] = stats["integrity_count"] / json_count if json_count > 0 else 0.0
    stats["answer_ratio"] = stats["answer_count"] / json_count if json_count > 0 else 0.0
    stats["correct_answer_ratio"] = stats["correct_answer_count"] / json_count if json_count > 0 else 0.0

    return stats

def print_statistics(stats: Dict[str, float]) -> None:
    """
    打印统计结果。

    主要实现方式：
        - 将统计结果格式化为易读的字符串。
        - 使用 logger 输出到控制台。

    入参说明：
        - stats (Dict[str, float]): 包含统计指标的字典。

    返回结果说明：
        - None
    """
    logger.info("\n=== 统计结果 ===")
    logger.info(f"文件总数: {stats['file_count']}")
    logger.info(f"JSON 对象总数: {stats['json_object_count']}")
    logger.info(f"question 对象总数: {stats['question_count']}")
    logger.info(f"question 对象占比: {stats['question_ratio']:.2%}")
    logger.info(f"check_question_can_answer 为 true 的总数: {stats['can_answer_count']}")
    logger.info(f"check_question_can_answer 为 true 的占比: {stats['can_answer_ratio']:.2%}")
    logger.info(f"expand_question 非空总数: {stats['expand_question_count']}")
    logger.info(f"expand_question 非空占比: {stats['expand_question_ratio']:.2%}")
    logger.info(f"check_question_is_integrity 为 true 的总数: {stats['integrity_count']}")
    logger.info(f"check_question_is_integrity 为 true 的占比: {stats['integrity_ratio']:.2%}")
    logger.info(f"answer 总数: {stats['answer_count']}")
    logger.info(f"answer 占比: {stats['answer_ratio']:.2%}")
    logger.info(f"check_answer_is_correct 为 true 的总数: {stats['correct_answer_count']}")
    logger.info(f"check_answer_is_correct 为 true 的占比: {stats['correct_answer_ratio']:.2%}")
    logger.info("================\n")

def main(input_dir: str) -> None:
    """
    主函数，执行统计任务。

    主要实现方式：
        - 检查输入文件夹是否存在。
        - 调用 calculate_statistics 计算统计指标。
        - 调用 print_statistics 打印结果。

    入参说明：
        - input_dir (str): 输入文件夹路径。

    返回结果说明：
        - None
    """
    input_path = Path(input_dir)
    if not input_path.exists() or not input_path.is_dir():
        logger.error(f"输入文件夹 {input_dir} 不存在或不是文件夹")
        return

    stats = calculate_statistics(input_dir)
    print_statistics(stats)

if __name__ == "__main__":
    # # window部署
    # input_directory = r"D:\Project\1. Super_Computer\2025\c03_js_wang_OpenAI_use\project-2\data\c9_merge_20000_document"

    # linux
    input_directory = "/x32001214/project/2025/c03_js_wang_QA/project-2/data/c9_merge_20000_document"
    main(input_directory)