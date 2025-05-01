# -*- coding: utf-8 -*-
"""
@author: Python高级工程师
Created on 2025/3/26
如果json文件中，is_correct为false，则针对该问题单独校验答案。如果答案正确，则修改is_correct为true；如果答案错误，则修改is_correct为false

"""

import os
import json
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Callable, Optional
from colorama import Fore, Style, init
from openai import OpenAI
import time

# 初始化colorama
init(autoreset=True)



# 常量定义
MAX_RETRIES = 10
PROMPT_TEMPLATE = """
请根据提供的源文本判断以下问题的答案是否正确。只需回答"true"或"false"。

源文本:
{source_text}

问题:
{question}

提供的答案:
{answer}

请严格只返回"true"或"false"，不要包含任何其他内容或解释。
"""


class Logger:
    """自定义日志记录器"""

    def __init__(self):
        self.start_time = time.time()
        self.total_files = 0
        self.processed_files = 0
        self.success_count = 0
        self.failure_count = 0

    def log(self, message: str, color: str = Fore.WHITE) -> None:
        """记录日志信息"""
        elapsed = time.time() - self.start_time
        print(f"{color}[{elapsed:.2f}s] {message}{Style.RESET_ALL}")

    def update_progress(self, filename: str, success: bool) -> None:
        """更新处理进度"""
        self.processed_files += 1
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1

        progress = self.processed_files / self.total_files * 100
        status = f"{Fore.GREEN}成功" if success else f"{Fore.RED}失败"
        self.log(f"[{self.processed_files}/{self.total_files} {progress:.1f}%] 处理完成: {filename} - {status}")


logger = Logger()


def validate_answer(source_text: str, question: str, answer: str) -> bool:
    """
    调用LLM验证答案的正确性

    参数:
        source_text: 源文本内容
        question: 问题文本
        answer: 待验证的答案

    返回:
        bool: 答案是否正确
    """
    prompt = PROMPT_TEMPLATE.format(
        source_text=source_text,
        question=question,
        answer=answer
    )

    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=model_uid,
                temperature=0.1,
                max_tokens=10
            )
            result = response.choices[0].message.content.strip().lower()
            if result == "true":
                return True
            elif result == "false":
                return False
        except Exception as e:
            logger.log(f"验证答案时出错(尝试{attempt + 1}/{MAX_RETRIES}): {str(e)}", Fore.YELLOW)

    return False


def process_single_file(filepath: str, callback: Optional[Callable[[str, bool], None]] = None) -> bool:
    """
    处理单个JSON文件，验证其中is_correct为false的条目

    参数:
        filepath: JSON文件路径
        callback: 处理完成后的回调函数

    返回:
        bool: 是否处理成功
    """
    filename = os.path.basename(filepath)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        modified = False
        total_false = 0
        processed = 0

        # 统计需要处理的条目
        for key, entry in data.items():
            if isinstance(entry, dict) and entry.get('is_correct') is False:
                total_false += 1

        if total_false == 0:
            logger.log(f"文件 {filename} 没有需要验证的条目", Fore.CYAN)
            if callback:
                callback(filename, True)
            return True

        logger.log(f"开始处理文件: {filename} - 需要验证 {total_false} 个答案", Fore.CYAN)

        # 处理每个is_correct为false的条目
        for key, entry in data.items():
            if isinstance(entry, dict) and entry.get('is_correct') is False:
                processed += 1
                logger.log(f"处理进度: {processed}/{total_false} - 验证问题: {entry.get('question')}", Fore.BLUE)

                is_correct = validate_answer(
                    entry.get('source_text', ''),
                    entry.get('question', ''),
                    entry.get('answer', '')
                )

                entry['is_correct'] = is_correct
                modified = True

                status = Fore.GREEN + "正确" if is_correct else Fore.RED + "错误"
                logger.log(f"验证结果: {status}", Fore.BLUE)

        if modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        if callback:
            callback(filename, True)
        return True

    except Exception as e:
        logger.log(f"处理文件 {filename} 时出错: {str(e)}", Fore.RED)
        if callback:
            callback(filename, False)
        return False


def process_files_concurrently(input_dir: str, max_workers: int = 5) -> None:
    """
    并发处理输入目录中的所有JSON文件

    参数:
        input_dir: 输入目录路径
        max_workers: 最大并发数
    """
    if not os.path.isdir(input_dir):
        logger.log("错误: 输入路径不是一个有效的目录", Fore.RED)
        return

    # 收集所有JSON文件
    json_files = []
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith('.json'):
                json_files.append(os.path.join(root, file))

    if not json_files:
        logger.log("警告: 没有找到JSON文件", Fore.YELLOW)
        return

    logger.total_files = len(json_files)
    logger.log(f"开始处理 {logger.total_files} 个文件...", Fore.GREEN)

    # 定义回调函数
    def completion_callback(filename: str, success: bool) -> None:
        """文件处理完成后的回调函数"""
        logger.update_progress(filename, success)

    # 使用线程池并发处理
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 使用map保持提交顺序
        results = list(executor.map(
            lambda f: process_single_file(f, completion_callback),
            json_files
        ))

    logger.log(f"\n处理完成! 成功: {logger.success_count}, 失败: {logger.failure_count}, 总计: {logger.total_files}",
               Fore.GREEN)


if __name__ == "__main__":
    input_dir = r"D:\Project\1.Super_Computer\2025\c07_superComputer_li_knowledge-base\data\c2_markdown2qa\v0.2\c4_check_answer"
    workers = 10

    process_files_concurrently(input_dir, workers)