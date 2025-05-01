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
from typing import List
from concurrent.futures import ThreadPoolExecutor
from colorama import Fore, Style, init
from openai import OpenAI

init(autoreset=True)

# 调用本地模型
client = openai.Client(api_key="not empty", base_url="http://10.160.199.27:30535/v1")
model_uid = "DeepSeek-R1-Distill-Qwen-32B"

# 常量定义
MAX_ATTEMPTS = 10
PROMPT_TEMPLATE = """
角色: 你是一名高级语言专家
任务：你当前的任务是根据以下源文本，判断每个问题是否可以依据源文本进行回答：

## 问题列表：
{questions}

## 源文本：
{source_text}

## 问题列表：
{questions}


## 输出格式：
- 如果问题可以由源文本回答，则对应的数组为true，否则为false
- 输出的 JSON 数组必须严格符合以下结构：
```json
[true, false]
```
"""


def combine_prompt(source_text: str, questions: List[str]) -> str:
    """组合prompt模板与具体内容"""
    return PROMPT_TEMPLATE.format(
        source_text=source_text,
        questions=json.dumps(questions, ensure_ascii=False),
    )


def response2list(response: str) -> List[bool]:
    """将模型返回的JSON字符串转换为布尔值列表"""
    try:
        # 使用正则表达式匹配JSON数组
        pattern = r'```json\n(.*?)\n```'
        match = re.search(pattern, response, re.DOTALL)
        if match:
            json_str = match.group(1)
            try:
                # 将JSON字符串转换为Python列表
                json_array = json.loads(json_str)
                return json_array
            except json.JSONDecodeError as e:
                print("解析JSON时出错:", e)
    except json.JSONDecodeError:
        return []


def generate_answer(prompt: str) -> List[bool]:
    """调用大语言模型生成答案"""
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=model_uid,
        max_tokens=20000
    )
    return response2list(chat_completion.choices[0].message.content)


def process_file(input_path: str, output_path: str, filename: str) -> tuple[str, bool]:
    """处理单个文件的核心逻辑

    Args:
        input_path: 输入文件夹路径
        output_path: 输出文件夹路径
        filename: 需要处理的文件名

    Returns:
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

        return filename, True

    except Exception as e:
        print(Fore.RED + f"处理文件{filename}时发生错误: {str(e)}")
        return filename, False


def main(input_dir: str, output_dir: str, concurrency: int) -> None:
    """主处理函数

    Args:
        input_dir: 输入文件夹路径
        output_dir: 输出文件夹路径
        concurrency: 并发数量
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 获取需要处理的文件列表
    input_files = set(os.listdir(input_dir))
    output_files = set(os.listdir(output_dir))
    todo_files = sorted(input_files - output_files)

    total = len(todo_files)
    print(Fore.RED + f"总共需要处理文件：{total}个")

    # 使用executor.map保证任务顺序执行
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        # 准备参数列表（input_dir, output_dir, filename）
        params = [(input_dir, output_dir, filename) for filename in todo_files]

        # 提交任务并获取生成器（保持提交顺序）
        results = executor.map(lambda p: process_file(*p), params)

        # 处理结果并显示进度
        for i, (filename, success) in enumerate(results, 1):
            status = Fore.GREEN + "成功" if success else Fore.RED + "失败"
            print(f"{Fore.GREEN}[{i}/{total}] 处理完成: {filename} {status}{Style.RESET_ALL}")


if __name__ == "__main__":
    # 示例调用（根据实际情况修改参数）
    main(
        # window部署
        # input_dir=r"D:\Project\1. Super_Computer\2025\c03_js_wang_OpenAI_use\project-2\data\c3_extract_q",
        # output_dir=r"D:\Project\1. Super_Computer\2025\c03_js_wang_OpenAI_use\project-2\data\c4_check_q_can_answer",

        # linux
        input_dir="/x32001214/project/2025/c03_js_wang_QA/project-2/data/c3_extract_q",  # 示例输入文件夹
        output_dir = "/x32001214/project/2025/c03_js_wang_QA/project-2/data/c4_check_q_can_answer",  # 示例输出文件夹
        concurrency=30
    )