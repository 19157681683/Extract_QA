# -*- coding: utf-8 -*-
"""
@author: 李林名
Created on 2025/3/25 12:22
"""

import os
import json
import openai
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import List, Callable, Optional
import re
from openai import OpenAI

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

    主要实现方式：
        根据是否提供颜色参数，将消息以指定颜色记录到日志中。

    入参说明：
        message (str): 日志消息。
        color (str, optional): 日志颜色（例如 RED、GREEN）。

    返回结果说明：
        None: 直接记录日志。
    """
    if color:
        logger.info(f"{color}{message}{RESET}")
    else:
        logger.info(message)

def get_files_to_process(input_dir: str, output_dir: str) -> List[str]:
    """
    获取需要处理的文件列表，即输入文件夹中有但输出文件夹中没有的文件。

    主要实现方式：
        比较输入和输出文件夹的文件列表，筛选出输入文件夹中独有的 JSON 文件。

    入参说明：
        input_dir (str): 输入文件夹路径。
        output_dir (str): 输出文件夹路径。

    返回结果说明：
        List[str]: 需要处理的文件名列表。
    """
    input_files = set(os.listdir(input_dir))
    output_files = set(os.listdir(output_dir))
    files_to_process = [f for f in input_files if f not in output_files and f.endswith('.json')]
    return files_to_process

# 调用本地模型
client = openai.Client(api_key="not empty", base_url="http://10.160.199.27:30535/v1")
model_uid = "Qwen2.5-72B-Instruct"

prompt_template = """
# Role: 微调数据集生成专家
## Profile:
- Description: 你是一名微调数据集生成专家，擅长从给定的内容中生成准确的问题答案，确保答案的准确性和相关性。只是生成{expand_question_number}个答案。

## Skills   :
1. 答案必须基于给定的内容
2. 答案必须准确，不能胡编乱造
3. 答案必须与问题相关
4. 答案必须符合逻辑
5. 需要生成{expand_question_number}个答案
6. 如果问题为空字符串，则答案也为空字符串。

## Workflow:
1. Take a deep breath and work on this problem step-by-step.
2. 首先，分析给定的文件内容
3. 然后，从内容中提取关键信息
4. 接着，生成与问题相关的准确答案
5. 最后，确保答案的准确性和相关性

## 输出示例
\`\`\`json
[ "xx","xx"]
 \`\`\`

## 源文本
{text}

## 问题列表
{expand_questions}

## Constrains:
1. 答案必须基于给定的内容
2. 答案必须准确，必须与问题相关，不能胡编乱造
3. 答案必须充分、详细、包含所有必要的信息、适合微调大模型训练使用
4. 只是生成{expand_question_number}个答案。
"""

def combine_prompt(text: str, expand_questions: List[str]) -> str:
    """
    组合 prompt 模板与具体内容。

    主要实现方式：
        将源文本和问题列表插入到预定义的 prompt 模板中。

    入参说明：
        text (str): 源文本。
        expand_questions (List[str]): 问题列表。

    返回结果说明：
        str: 组合后的 prompt 字符串。
    """
    return prompt_template.replace("{expand_question_number}", str(len(expand_questions))).replace("{text}", text).replace(
        "{expand_questions}", str(expand_questions))

def response2list(response: str) -> List[str]:
    """
    将模型返回的 JSON 字符串转换为列表。

    主要实现方式：
        去除 JSON 字符串中的 ```json 和 ``` 标记，解析为 Python 列表。

    入参说明：
        response (str): 模型返回的字符串。

    返回结果说明：
        List[str]: 答案列表。
    """
    cleaned_text = re.sub(r'```json|```', '', response)
    return json.loads(cleaned_text)

def generate_answer(prompt: str, max_retries: int = 10) -> List[str]:
    """
    调用大语言模型生成答案。

    主要实现方式：
        使用 OpenAI 客户端调用模型生成答案，支持重试机制以处理异常。

    入参说明：
        prompt (str): 输入的 prompt 字符串。
        max_retries (int): 最大重试次数，默认为 10。

    返回结果说明：
        List[str]: 生成的答案列表。
    """
    retries = 0
    while retries < max_retries:
        try:
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=model_uid,
                max_tokens=20000,
                temperature=0.9
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

    主要实现方式：
        重复调用 generate_answer，直到答案数量匹配或达到最大尝试次数。

    入参说明：
        prompt (str): 输入的 prompt 字符串。
        expected_count (int): 期望的答案数量。
        max_attempts (int): 最大尝试次数，默认为 10。

    返回结果说明：
        List[str]: 生成的答案列表。
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
    处理单个文件：读取 JSON，提取源文本和问题，调用 LLM 生成答案，保存到输出文件夹。

    主要实现方式：
        读取输入 JSON 文件，检查 check_question_is_integrity 为 False 的情况并设置 expand_question 为空，
        提取源文本和非空问题列表，调用 LLM 生成答案，更新 JSON 数据并保存到输出文件夹。

    入参说明：
        input_dir (str): 输入文件夹路径。
        output_dir (str): 输出文件夹路径。
        filename (str): 文件名。
        callback (Optional[Callable[[str], None]]): 处理完成后的回调函数。

    返回结果说明：
        None: 处理结果直接保存到输出文件夹。
    """
    try:
        # 读取 JSON 文件
        with open(os.path.join(input_dir, filename), 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 处理 check_question_is_integrity 为 False 的情况
        for key, entry in data.items():
            if not isinstance(entry, dict):
                continue
            if entry.get('check_question_is_integrity', None) is False:
                entry['expand_question'] = ''
                log_info(f"文件 {filename} 中 {key} 的 check_question_is_integrity 为 False，设置 expand_question 为空", RED)

        # 提取源文本和问题列表
        source_text = data.get("0", {}).get("source_text", "")

        # 生成 expand_questions，仅包含非空且 check_question_is_integrity 不为 False 的问题
        expand_questions = [entry["expand_question"] for entry in data.values()
                           if "expand_question" in entry and
                           entry.get("check_question_is_integrity", True) is not False and
                           entry["expand_question"].strip()]

        if not expand_questions:
            log_info(f"文件 {filename} 中没有有效问题，跳过。", RED)
            return

        # 调用 LLM 生成答案
        prompt_text = combine_prompt(source_text, expand_questions)
        answer_list = generate_answers_until_match(prompt_text, len(expand_questions))

        # 将答案添加到 JSON 中
        answer_index = 0
        for i, entry in enumerate(data.values()):
            if "expand_question" in entry and entry["expand_question"].strip() and entry.get("check_question_is_integrity", True) is not False:
                entry["answer"] = answer_list[answer_index]
                answer_index += 1

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

    主要实现方式：
        获取需要处理的文件列表，使用 ThreadPoolExecutor 并发处理每个文件，跟踪进度并记录日志。

    入参说明：
        input_dir (str): 输入文件夹路径。
        output_dir (str): 输出文件夹路径。
        concurrency (int): 并发数量。

    返回结果说明：
        None: 处理结果保存到输出文件夹，进度通过日志输出。
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
        # 使用map方法并传入回调函数
        executor.map(
            lambda f: process_file(input_dir, output_dir, f, update_progress),
            files_to_process
        )

    log_info("所有文件处理完成!", GREEN)

if __name__ == "__main__":
    # # window部署
    # input_directory = r"D:\Project\1. Super_Computer\2025\c03_js_wang_OpenAI_use\project-2\data\c6_check_q_is_integrity"
    # output_directory = r"D:\Project\1. Super_Computer\2025\c03_js_wang_OpenAI_use\project-2\data\c7_extract_a"

    # linux
    input_directory = "/x32001214/project/2025/c03_js_wang_QA/project-2/data/c6_check_q_is_integrity"
    output_directory = "/x32001214/project/2025/c03_js_wang_QA/project-2/data/c7_extract_a"
    concurrency_level = 30  # 并发数量
    main(input_directory, output_directory, concurrency_level)