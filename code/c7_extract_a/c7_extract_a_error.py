# -*- coding: utf-8 -*-
"""
@author: 李林名
Created on 2025/3/25 12:22
如果json文件中，is_correct为false，则针对该问题单独生成答案，修改掉之前的答案
"""

import os
import json
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Optional, Callable
from openai import OpenAI

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger()

# 定义颜色
RED = '\033[91m'
GREEN = '\033[92m'
BLUE = '\033[94m'
RESET = '\033[0m'

# ## DeepSeek 模型配置：
# client = OpenAI(api_key="sk-1fd3f8aae5a3486e8090a888b68c6678", base_url="https://api.deepseek.com")
# model_uid = "deepseek-chat"

def log_info(message: str, color: str = None) -> None:
    """
    记录日志信息，可选择颜色输出。

    :param message: 日志消息内容
    :param color: 日志颜色（可选，例如 RED 或 GREEN）
    """
    if color:
        logger.info(f"{color}{message}{RESET}")
    else:
        logger.info(message)


def generate_new_answer(source_text: str, question: str) -> str:
    """
    调用语言模型生成新答案。

    :param source_text: 源文本，用于生成答案的上下文
    :param question: 问题，需基于此生成答案
    :return: 生成的新答案字符串
    """
    prompt = f"""
    根据以下源文本生成问题的准确答案：
    源文本：{source_text}
    问题：{question}
    要求：
    1. 答案必须基于源文本。
    2. 答案必须准确、相关且符合逻辑。
    """
    try:
        response = client.chat.completions.create(
            model=model_uid,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        log_info(f"生成答案失败: {e}", RED)
        return "生成答案失败"


def process_json_file(filepath: str, callback: Optional[Callable[[str], None]] = None) -> Dict:
    """
    处理单个 JSON 文件，重新生成 `is_correct` 为 False 的答案。

    :param filepath: JSON 文件的完整路径
    :param callback: 处理完成后的回调函数
    :return: 更新后的 JSON 数据字典
    """
    filename = os.path.basename(filepath)
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    updated = False
    for key, entry in data.items():
        if entry.get("is_correct", True) is False:
            source_text = entry.get("source_text", "")
            question = entry.get("question", "")
            new_answer = generate_new_answer(source_text, question)
            entry["answer"] = new_answer
            updated = True
            log_info(f"文件 {filename} - 问题 '{question}' 的答案已更新", GREEN)

    if updated:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    # 调用回调函数
    if callback:
        callback(filename)

    return data


def main(input_dir: str, concurrency: int = 5) -> None:
    """
    主函数：并发处理输入文件夹中的 JSON 文件。

    :param input_dir: 输入文件夹路径
    :param concurrency: 并发线程数，默认为 5
    """
    # 获取所有 JSON 文件
    json_files = [f for f in os.listdir(input_dir) if f.endswith('.json')]
    total_files = len(json_files)

    if total_files == 0:
        log_info("输入文件夹中没有 JSON 文件", RED)
        return

    log_info(f"发现 {total_files} 个 JSON 文件需要处理", GREEN)
    processed_files = 0

    def update_progress(filename: str) -> None:
        """更新处理进度"""
        nonlocal processed_files
        processed_files += 1
        progress = (processed_files / total_files) * 100
        log_info(f"进度: {processed_files}/{total_files} ({progress:.1f}%) - 已完成 {filename}", BLUE)

    # 使用 ThreadPoolExecutor 并发处理
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        file_paths = [os.path.join(input_dir, f) for f in json_files]
        # 使用map方法并传入回调函数
        executor.map(
            lambda fp: process_json_file(fp, update_progress),
            file_paths
        )

    log_info("所有文件处理完成！", GREEN)


if __name__ == "__main__":
    input_directory = r"D:\Project\1.Super_Computer\2025\c07_superComputer_li_knowledge-base\data\c2_markdown2qa\v0.2\c4_check_answer"
    concurrency_level = 50
    main(input_directory, concurrency_level)