#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：project-2
@File    ：c2_split_within_20000_document.py
@IDE     ：PyCharm
@Author  ：李林名
@Date    ：2025/4/27 14:57
@Usage   ：提取Q
'''
#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：project-2
@File    ：c2_split_within_20000_document.py
@IDE     ：PyCharm
@Author  ：李林名
@Date    ：2025/4/27 14:57
@Usage   ：提取Q
'''

import os
import json
import re
from typing import List, Dict
import concurrent.futures
from openai import OpenAI
import openai
from tqdm import tqdm
from colorama import Fore, Style


class QuestionGenerator:
    def __init__(self, input_dir: str, output_dir: str, concurrency: int = 4, chars_per_extracted_question: int = 500, max_retries: int = 10):
        """
        初始化问题生成器

        参数:
            input_dir: 输入文件夹路径
            output_dir: 输出文件夹路径
            c0_concurrency: 并发数量 (默认4)
            max_retries: 最大重试次数 (默认10)
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.concurrency = concurrency
        self.chars_per_extracted_question = chars_per_extracted_question
        self.max_retries = max_retries

        # 创建输出目录如果不存在
        os.makedirs(self.output_dir, exist_ok=True)

        # # 调用本地模型
        self.client = openai.Client(api_key="not empty", base_url="http://10.160.199.27:30535/v1")
        self.model_uid = "Qwen2.5-72B-Instruct"

        # 日志颜色
        self.color_error = Fore.RED
        self.color_success = Fore.GREEN
        self.color_info = Fore.BLUE
        self.color_reset = Style.RESET_ALL

    def get_pending_files(self) -> List[str]:
        """
        获取待处理的文件列表（存在于输入目录但不存在于输出目录）

        返回:
            待处理的文件名列表
        """
        input_files = set(os.listdir(self.input_dir))
        output_files = set(f.replace('.json', '') for f in os.listdir(self.output_dir))
        pending_files = list(input_files - output_files)

        print(f"{self.color_error}总待处理文件数: {len(pending_files)}{self.color_reset}")
        return pending_files

    @staticmethod
    def response2list(response: str) -> List[str]:
        """将模型返回的 JSON 字符串转换为列表"""
        try:
            cleaned_text = re.sub(r'```json|```', '', response)
            return json.loads(cleaned_text)
        except json.JSONDecodeError:
            return []

    def combine_prompt(self, text: str, number: int) -> str:
        """组合 prompt 模板与具体内容"""
        prompt = """
        # 角色使命
        你是一位专业的文本分析专家，擅长从复杂文本中提取关键信息并生成可用于模型微调的结构化数据（仅生成问题）。

        ## 核心任务
        根据用户提供的文本，生成不少于 ${number} 个高质量问题，问题使用中文描述。


        ## 约束条件（重要！）
        ✔️ 必须基于文本内容直接生成
        ✔️ 问题应具有明确答案指向性
        ✔️ 需覆盖文本的不同方面
        ✔️ 保证生成的问题的多样性
        ❌ 禁止生成假设性、重复或相似问题

        ## 处理流程
        1. 【文本解析】分段处理内容，识别关键实体和核心概念
        2. 【问题生成】基于信息密度选择最佳提问点
        3. 【质量检查】确保：
           - 问题答案可在原文中找到依据
           - 标签与问题内容强相关
           - 无格式错误

        ## 输出格式
         - JSON 数组格式必须正确
        - 字段名使用英文双引号
        - 输出的 JSON 数组必须严格符合以下结构：
        ```json
        ["问题1", "问题2", "..."]
        ```

        ## 输出内容
        - 对于人名、地名等名称，在提取问题的时候，必须使用英文（中文翻译）方式保留准确性和可读性。比如：英文名称（中文名称）。
        - 禁止输出格式：生成的问题禁止输出&quot

        ## 输出示例
        ```json
        [
          "Hierapolis of Phrygia（弗里吉亚的希拉波利斯）出土的大理石雕像上使用了哪些主要的着色材料？",
          "Severan Theatre（塞维兰剧院）的浮雕和装饰雕像上发现了哪些色彩痕迹？",
           "文中提到的雕像的女孩形象代表什么样的文化意义？",
          "分析过程中遇到的光照和环境干扰问题有哪些？",
          "研究结果对于理解古代艺术风格的意义是什么？",
        ]
         ```

        ## 待处理文本
        ${text}

        ## 限制
        - 必须按照规定的 JSON 格式输出，不要输出任何其他不相关内容
        - 生成不少于 ${number} 个高质量问题
        - 问题不要和材料本身相关，例如禁止出现作者、章节、目录等相关问题
        """
        return prompt.replace("${text}", text).replace("${number}", str(number))

    def generate_questions(self, text: str, required_num: int) -> List[str]:
        """
        调用大语言模型生成问题

        参数:
            text: 输入文本
            required_num: 需要的问题数量

        返回:
            生成的问题列表
        """
        for _ in range(self.max_retries):
            try:
                prompt = self.combine_prompt(text, required_num)
                chat_completion = self.client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=self.model_uid,
                    max_tokens=20000
                )
                questions = chat_completion.choices[0].message.content
                question_list = self.response2list(questions)

                if len(question_list) >= required_num:
                    return question_list[:required_num]

            except Exception as e:
                print(f"{self.color_error}生成问题出错: {e}{self.color_reset}")
                continue

        print(f"{self.color_error}达到最大重试次数 {self.max_retries} 仍无法生成足够问题{self.color_reset}")
        return []

    def process_file(self, filename: str, progress_bar: tqdm = None):
        """
        处理单个文件

        参数:
            filename: 文件名
            progress_bar: 进度条对象 (可选)
        """
        try:
            # 读取文件内容
            input_path = os.path.join(self.input_dir, filename)
            with open(input_path, 'r', encoding='utf-8') as f:
                text = f.read()

            # 计算需要的问题数量
            text_length = len(text)
            question_num = max(1, text_length // self.chars_per_extracted_question)

            print(
                f"{self.color_info}处理文件: {filename}, 字数: {text_length}, 需要问题数: {question_num}{self.color_reset}")

            # 生成问题
            questions = self.generate_questions(text, question_num)

            if not questions:
                raise ValueError("无法生成问题")

            # 构建结果JSON
            result = {
                "0": {
                    "filename": filename,
                    "source_text": text,
                    "question": questions[0],
                    "check_question_can_answer": "",
                    "expand_question": "",
                    "check_question_is_integrity": "",
                    "answer": "",
                    "check_answer_is_correct": ""
                }
            }

            for i in range(1, len(questions)):
                result[str(i)] = {
                    "filename": filename,
                    "source_text": text,
                    "question": questions[i],
                    "check_question_can_answer": "",
                    "expand_question": "",
                    "check_question_is_integrity": "",
                    "answer": "",
                    "check_answer_is_correct": ""
                }

            # 保存结果
            output_path = os.path.join(self.output_dir, f"{filename}.json")
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            print(f"{self.color_success}完成文件: {filename}{self.color_reset}")

        except Exception as e:
            print(f"{self.color_error}处理文件 {filename} 出错: {e}{self.color_reset}")
        finally:
            if progress_bar:
                progress_bar.update(1)

    def run(self):
        """执行主处理流程"""
        pending_files = self.get_pending_files()
        total_files = len(pending_files)

        if not total_files:
            print(f"{self.color_info}没有需要处理的文件{self.color_reset}")
            return

        with tqdm(total=total_files, desc="处理进度") as pbar:
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.concurrency) as executor:
                futures = []
                for filename in pending_files:
                    futures.append(executor.submit(self.process_file, filename, pbar))

                for future in concurrent.futures.as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        print(f"{self.color_error}处理出错: {e}{self.color_reset}")

        print(f"{self.color_success}处理完成! 共处理 {total_files} 个文件{self.color_reset}")


if __name__ == "__main__":
    # window
    # input_dir = r"D:\Project\1. Super_Computer\2025\c03_js_wang_OpenAI_use\project-2\data\c2_split_within_20000_document"  # 示例输入文件夹
    # output_dir = r"D:\Project\1. Super_Computer\2025\c03_js_wang_OpenAI_use\project-2\data\c3_extract_q"  # 示例输出文件夹

    # linux
    input_dir = "/x32001214/project/2025/c03_js_wang_QA/project-2/data/c2_split_within_20000_document"  # 示例输入文件夹
    output_dir = "/x32001214/project/2025/c03_js_wang_QA/project-2/data/c3_extract_q"  # 示例输出文件夹
    concurrency = 30  # 示例并发数量
    chars_per_extracted_question = 500  # 每个问题从多少个英文字符中抽取
    generator = QuestionGenerator(
        input_dir=input_dir,
        output_dir=output_dir,
        concurrency=concurrency,
        chars_per_extracted_question=chars_per_extracted_question,
    )
    generator.run()
