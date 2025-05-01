#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：project-2 
@File    ：c5_expand_q_integrity.py
@IDE     ：PyCharm 
@Author  ：李林名
@Date    ：2025/4/28 16:58 
@Usage   ：对提取的可以回答的问题进行扩展
'''
# -*- coding: utf-8 -*-
"""
@author: 李林名
Created on 2025/3/25 12:22
Updated on 2025/4/28
"""

import os
import json
import openai
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import List, Callable, Optional
import re
from openai import OpenAI
import uuid

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger()

# 定义颜色
RED = '\033[91m'
GREEN = '\033[92m'
RESET = '\033[0m'


def log_info(message: str, color: str = None) -> None:
    """
    记录日志信息，可选择颜色。

    :param message: 日志消息
    :param color: 日志颜色（可选）
    :return: 无返回值
    """
    if color:
        logger.info(f"{color}{message}{RESET}")
    else:
        logger.info(message)


def get_files_to_process(input_dir: str, output_dir: str) -> List[str]:
    """
    获取需要处理的文件列表，即输入文件夹中有但输出文件夹中没有的文件。

    :param input_dir: 输入文件夹路径
    :param output_dir: 输出文件夹路径
    :return: 需要处理的文件名列表
    """
    input_files = set(os.listdir(input_dir))
    output_files = set(os.listdir(output_dir))
    files_to_process = [f for f in input_files if f not in output_files and f.endswith('.json')]
    return files_to_process


# 调用本地模型
client = openai.Client(api_key="not empty", base_url="http://10.160.199.27:30535/v1")
model_uid = "Qwen2.5-72B-Instruct"

prompt_template = """
角色：你是一个语言学专家
任务：你当前的任务是补充问题的完整性，使得问题完整无歧义，无缺乏主语或者实体，类似数据库中ID，独立且唯一标识。
注意：1. 可以采用who（主体）、when（时间）、where（地点）、why、what（对象）、how（方法）的分析框架。
     2. 包括研究主体、研究对象、研究时间、研究地点、研究目的、技术类型、相关细节。
     3. 输出的补充完整语义的问题，请使用中文。

## 输出格式：
 - JSON 数组格式必须正确
- 字段名使用英文双引号
- 输出的 JSON 数组必须严格符合以下结构：
- 对于人名、地名等名称，在提取问题的时候，必须使用英文（中文翻译）方式保留准确性和可读性。比如：英文名称（中文名称）。
```json
["问题1", "问题2", "..."]
```

## 示例
# 样例1:
# 原始问题：
在现场分析中采用了哪些非侵入性成像技术？
# 完整语义的问题：
在2014-2015年意大利考古团队（MAIER）对土耳其Hierapolis of Phrygia（弗里吉亚的希拉波利斯）考古遗址出土的Severan Theatre（塞维鲁剧院）和North Agora（北广场）大理石雕像的现场分析中，研究者采用了哪些非侵入性成像技术来检测古代彩绘痕迹？

# 样例2:
# 原始问题：
研究使用的非侵入性成像技术包括哪些类型？
# 完整语义的问题：
在2014-2015年意大利考古团队（MAIER）对土耳其Hierapolis of Phrygia（赫拉波利斯）遗址的Severan Theatre（塞维鲁剧院）和North Agora（北广场）出土的大理石雕像进行多学科研究中，采用了哪些非侵入性成像技术来检测和分析雕像表面的古代彩绘痕迹？

# 样例3:
# 原始问题：
对Hierapolis（希拉波利斯）雕像进行微破坏的理由是什么？
# 完整语义的问题：
在2014-2015年土耳其Hierapolis（希拉波利斯）考古遗址的雕像研究中，意大利考古团队MAIER为何在非侵入性成像技术（如UVf和VIL）无法完全表征有机染料（如茜素湖）时，对Kore-Persephone雕像和Attis雕像进行微破坏取样？

## 初始问题
{questions}

## 源文章
{text}
"""


def combine_prompt(text: str, questions: List[str]) -> str:
    """
    组合 prompt 模板与具体内容。

    :param text: 源文本
    :param questions: 问题列表
    :return: 组合后的 prompt 字符串
    """
    return prompt_template.replace("{text}", text).replace("{questions}", str(questions))


def response2list(response: str) -> List[str]:
    """
    将模型返回的 JSON 字符串转换为列表。

    :param response: 模型返回的字符串
    :return: 答案列表
    """
    cleaned_text = re.sub(r'```json|```', '', response)
    return json.loads(cleaned_text)


def generate_answer(prompt: str, max_retries: int = 10) -> List[str]:
    """
    调用大语言模型生成答案。

    :param prompt: 输入的 prompt 字符串
    :param max_retries: 最大重试次数，默认值为 10
    :return: 生成的答案列表
    """
    retries = 0
    while retries < max_retries:
        try:
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=model_uid,
                max_tokens=20000
            )

            answer = chat_completion.choices[0].message.content
            answer_list = response2list(answer)

            return answer_list
        except Exception as e:
            retries += 1
            log_info(f"发生异常: {e}. 重试 {retries}/{max_retries}", RED)
            if retries == max_retries:
                raise Exception(f"达到最大重试次数 {max_retries}. 最后一次错误: {e}")


def generate_answers_until_match(prompt: str, expected_count: int, max_attempts: int = 10) -> List[str]:
    """
    生成答案列表，直到生成的答案数量与期望数量一致或达到最大尝试次数。

    :param prompt: 输入的 prompt 字符串
    :param expected_count: 期望的答案数量
    :param max_attempts: 最大尝试次数，默认值为 10
    :return: 生成的答案列表
    """
    attempts = 0
    while attempts < max_attempts:
        attempts += 1
        try:
            answer_list = generate_answer(prompt)
            if len(answer_list) == expected_count:
                return answer_list
            log_info(
                f"生成的答案数量不匹配（需要 {expected_count}，实际 {len(answer_list)}），尝试 {attempts}/{max_attempts}",
                RED)
        except Exception as e:
            log_info(f"生成答案时发生异常: {e}. 尝试 {attempts}/{max_attempts}", RED)

    raise Exception(f"无法在 {max_attempts} 次尝试内生成正确数量的答案")


def process_file(input_dir: str, output_dir: str, filename: str,
                 callback: Optional[Callable[[str], None]] = None) -> None:
    """
    处理单个文件：读取 JSON，筛选可回答问题，生成扩展问题，保存到输出文件夹。

    :主要实现方式:
        1. 读取输入JSON文件，筛选check_question_can_answer为true的条目
        2. 提取question和source_text，调用LLM生成扩展问题
        3. 将扩展问题写入expand_question字段，保存到输出文件夹
    :param input_dir: 输入文件夹路径
    :param output_dir: 输出文件夹路径
    :param filename: 文件名
    :param callback: 處理完成后的回调函数
    :return: 无返回值
    """
    try:
        # 读取 JSON 文件
        with open(os.path.join(input_dir, filename), 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 筛选 check_question_can_answer 为 true 的条目
        valid_entries = [
            (key, entry) for key, entry in data.items()
            if entry.get("check_question_can_answer", False) and entry.get("question", "")
        ]

        if not valid_entries:
            log_info(f"文件 {filename} 中没有可回答的问题，跳过。", RED)
            return

        # 提取问题列表和源文本（假设所有条目共享相同的 source_text）
        questions = [entry["question"] for _, entry in valid_entries]
        source_text = valid_entries[0][1].get("source_text", "")

        # 调用 LLM 生成扩展问题
        prompt_text = combine_prompt(source_text, questions)
        expanded_questions = generate_answers_until_match(prompt_text, len(questions))

        # 将扩展问题写入对应的 expand_question 字段
        for (key, _), expanded_question in zip(valid_entries, expanded_questions):
            data[key]["expand_question"] = expanded_question

        # 保存到输出文件夹
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(os.path.join(output_dir, filename), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        log_info(f"文件 {filename} 处理完成。", GREEN)

        # 调用回调函数
        if callback:
            callback(filename)
    except Exception as e:
        log_info(f"处理文件 {filename} 时发生异常: {e}", RED)


def main(input_dir: str, output_dir: str, concurrency: int) -> None:
    """
    主函数：处理所有需要处理的文件，使用并发处理。

    :主要实现方式:
        1. 获取需要处理的文件列表
        2. 使用ThreadPoolExecutor并发处理文件
        3. 跟踪进度并记录日志
    :param input_dir: 输入文件夹路径
    :param output_dir: 输出文件夹路径
    :param concurrency: 并发数量
    :return: 无返回值
    """
    files_to_process = get_files_to_process(input_dir, output_dir)
    total_files = len(files_to_process)
    log_info(f"总共需要处理 {total_files} 个文件。", RED)

    if total_files == 0:
        log_info("没有需要处理的文件。", GREEN)
        return

    # 进度跟踪变量
    completed_files = 0

    def update_progress(filename: str) -> None:
        """更新进度并打印绿色日志"""
        nonlocal completed_files
        completed_files += 1
        progress = completed_files / total_files * 100
        log_info(f"进度: {completed_files}/{total_files} ({progress:.1f}%) - 已完成 {filename}", GREEN)

    # 使用ThreadPoolExecutor处理文件
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        executor.map(
            lambda f: process_file(input_dir, output_dir, f, update_progress),
            files_to_process
        )

    log_info("所有文件处理完成!", GREEN)


if __name__ == "__main__":
    # # window部署
    # input_directory = r"D:\Project\1. Super_Computer\2025\c03_js_wang_OpenAI_use\project-2\data\c4_check_q_can_answer"
    # output_directory = r"D:\Project\1. Super_Computer\2025\c03_js_wang_OpenAI_use\project-2\data\c5_expand_q_integrity"

    # linux
    input_directory = "/x32001214/project/2025/c03_js_wang_QA/project-2/data/c4_check_q_can_answer"
    output_directory = "/x32001214/project/2025/c03_js_wang_QA/project-2/data/c5_expand_q_integrity"
    concurrency_level = 30  # 并发数量
    main(input_directory, output_directory, concurrency_level)