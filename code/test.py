#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：project-2
@File    ：c4_check_q_can_answer.py
@IDE     ：PyCharm
@Author  ：李林名
@Date    ：2025/4/29 11:10
@Usage   ：对提取的问题进行校验,是否能够回答
'''

import re
import os
import json
import openai
from typing import List, Callable, Optional
from concurrent.futures import ThreadPoolExecutor
from colorama import Fore, Style, init
from openai import OpenAI
import logging

# 初始化colorama
init(autoreset=True)

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger()

# 调用本地模型
client = openai.Client(api_key="not empty", base_url="http://10.160.199.27:30535/v1")
model_uid = "DeepSeek-R1-Distill-Qwen-32B"

# 常量定义
MAX_ATTEMPTS = 10
PROMPT_TEMPLATE = """"""


def log_info(message: str, color: str = None) -> None:
    """
    记录日志信息，可选择颜色。

    主要实现方式：
        使用logging模块记录日志，支持彩色输出。
    入参说明：
        message: 日志消息
        color: 日志颜色（可选，Fore.GREEN或Fore.RED等）
    返回结果说明：
        无返回值
    """
    if color:
        logger.info(f"{color}{message}{Style.RESET_ALL}")
    else:
        logger.info(message)


def combine_prompt(source_text: str, questions: List[str]) -> str:
    """
    组合prompt模板与具体内容。

    主要实现方式：
        使用PROMPT_TEMPLATE格式化源文本和问题列表。
    入参说明：
        source_text: 源文本内容
        questions: 问题列表
    返回结果说明：
        格式化后的prompt字符串
    """
    return PROMPT_TEMPLATE.format(
        source_text=source_text,
        questions=json.dumps(questions, ensure_ascii=False),
    )


def response2list(response: str) -> List[bool]:
    """
    将模型返回的JSON字符串转换为布尔值列表。

    主要实现方式：
        使用正则表达式提取JSON数组，解析为Python列表。
    入参说明：
        response: 模型返回的字符串
    返回结果说明：
        布尔值列表，表示问题是否可回答
    """
    try:
        pattern = r'```json\n(.*?)\n```'
        match = re.search(pattern, response, re.DOTALL)
        if match:
            json_str = match.group(1)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                log_info(f"解析JSON时出错: {e}", Fore.RED)
    except json.JSONDecodeError:
        return []


def generate_answer(prompt: str) -> List[bool]:
    """
    调用大语言模型生成答案。

    主要实现方式：
        使用OpenAI客户端调用模型，获取响应并解析。
    入参说明：
        prompt: 输入的prompt字符串
    返回结果说明：
        布尔值列表，表示问题是否可回答
    """
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=model_uid,
        max_tokens=20000
    )
    return response2list(chat_completion.choices[0].message.content)


def process_file(input_path: str, output_path: str, filename: str,
                callback: Optional[Callable[[str, bool], None]] = None) -> tuple[str, bool]:
    """
    处理单个文件的核心逻辑。

    主要实现方式：
        1. 读取输入JSON文件，提取源文本和问题
        2. 调用模型生成答案，更新check_question_can_answer字段
        3. 保存结果到输出文件
        4. 调用回调函数记录处理状态
    入参说明：
        input_path: 输入文件夹路径
        output_path: 输出文件夹路径
        filename: 需要处理的文件名
        callback: 处理完成后的回调函数（可选）
    返回结果说明：
        tuple: (文件名, 是否处理成功)
    """
    try:
        # 读取输入文件
        with open(os.path.join(input_path, filename), 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 提取必要信息
        entries = list(data.values())
        source_text = entries[0]['source_text']
        questions = [entry['question'] for entry in entries]

        # 生成prompt并调用模型
        prompt = combine_prompt(source_text, questions)
        attempts = 0
        result = []

        while attempts < MAX_ATTEMPTS and len(result) != len(questions):
            attempts += 1
            result = generate_answer(prompt)

        # 更新check_question_can_answer字段
        for idx, entry in enumerate(entries):
            entry['check_question_can_answer'] = result[idx] if idx < len(result) else None

        # 保存结果到输出文件
        with open(os.path.join(output_path, filename), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # 调用回调函数
        if callback:
            callback(filename, True)

        return filename, True

    except Exception as e:
        log_info(f"处理文件 {filename} 时发生错误: {str(e)}", Fore.RED)
        if callback:
            callback(filename, False)
        return filename, False


def main(input_dir: str, output_dir: str, concurrency: int) -> None:
    """
    主处理函数。

    主要实现方式：
        1. 获取需要处理的文件列表
        2. 使用ThreadPoolExecutor并发处理文件
        3. 定义回调函数跟踪进度并记录日志
    入参说明：
        input_dir: 输入文件夹路径
        output_dir: 输出文件夹路径
        concurrency: 并发数量
    返回结果说明：
        无返回值，处理结果通过日志输出
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 获取需要处理的文件列表
    input_files = set(os.listdir(input_dir))
    output_files = set(os.listdir(output_dir))
    todo_files = sorted(input_files - output_files)

    total = len(todo_files)
    log_info(f"总共需要处理文件：{total}个", Fore.RED)

    if total == 0:
        log_info("没有需要处理的文件。", Fore.GREEN)
        return

    # 进度跟踪变量
    completed_files = 0

    def update_progress(filename: str, success: bool) -> None:
        """
        更新进度并打印日志。

        主要实现方式：
            记录文件处理状态和进度百分比。
        入参说明：
            filename: 处理的文件名
            success: 是否处理成功
        返回结果说明：
            无返回值
        """
        nonlocal completed_files
        completed_files += 1
        progress = completed_files / total * 100
        status = Fore.GREEN + "成功" if success else Fore.RED + "失败"
        log_info(
            f"进度: {completed_files}/{total} ({progress:.1f}%) - 处理完成: {filename} {status}",
            status
        )

    # 使用executor.map保证任务顺序执行
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        # 准备参数列表
        params = [(input_dir, output_dir, filename, update_progress) for filename in todo_files]

        # 提交任务并获取生成器
        executor.map(lambda p: process_file(*p), params)

    log_info("所有文件处理完成!", Fore.GREEN)


if __name__ == "__main__":
    main(
        input_dir="/x32001214/project/2025/c03_js_wang_QA/project-2/data/",
        output_dir="/x32001214/project/2025/c03_js_wang_QA/project-2/data/test",
        concurrency=10
    )