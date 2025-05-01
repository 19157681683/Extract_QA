#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：project-2 
@File    ：c1_rename_file.py
@IDE     ：PyCharm 
@Author  ：李林名
@Date    ：2025/4/27 14:10 
@Usage   ：从输入每个输入文件夹中一级子文件夹中，取其中md文件，并按照一级子文件重新命名该md文件，保存到输出文件夹中。
'''
import os
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def setup_output_directory(output_path: str) -> Path:
    """
    创建输出文件夹（如果不存在）。

    实现方式：
        使用 Path 模块检查输出文件夹路径，如果不存在则创建。

    入参说明：
        output_path (str): 输出文件夹的路径。

    返回结果说明：
        Path: 输出文件夹的 Path 对象。
    """
    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def find_md_files(input_path: str) -> list[tuple[Path, Path]]:
    """
    遍历输入文件夹，查找一级子文件夹中的 md 文件。

    实现方式：
        遍历输入文件夹的一级子文件夹，检查每个子文件夹中的 full.md 文件。
        返回包含子文件夹路径和 md 文件路径的列表。

    入参说明：
        input_path (str): 输入文件夹的路径。

    返回结果说明：
        list[tuple[Path, Path]]: 包含 (子文件夹路径, md 文件路径) 的列表。
    """
    input_dir = Path(input_path)
    if not input_dir.exists() or not input_dir.is_dir():
        logging.error(f"输入文件夹 {input_path} 不存在或不是文件夹")
        return []

    md_files = []
    subdirs = [d for d in input_dir.iterdir() if d.is_dir()]
    for subdir in subdirs:
        md_file = subdir / "full.md"
        if md_file.exists() and md_file.is_file():
            md_files.append((subdir, md_file))

    return md_files


def process_md_files(md_files: list[tuple[Path, Path]], output_dir: Path) -> int:
    """
    处理 md 文件，将其重命名并保存到输出文件夹。

    实现方式：
        遍历 md 文件列表，读取每个 md 文件内容，以子文件夹名称重命名后保存到输出文件夹。

    入参说明：
        md_files (list[tuple[Path, Path]]): 包含 (子文件夹路径, md 文件路径) 的列表。
        output_dir (Path): 输出文件夹的 Path 对象。

    返回结果说明：
        int: 成功处理的 md 文件数量。
    """
    processed_count = 0
    for subdir, md_file in md_files:
        try:
            # 读取 md 文件内容
            content = md_file.read_text(encoding='utf-8')
            # 使用子文件夹名称作为新文件名
            new_filename = f"{subdir.name}.md"
            output_file = output_dir / new_filename
            # 保存到输出文件夹
            output_file.write_text(content, encoding='utf-8')
            logging.info(f"已处理: {md_file} -> {output_file}")
            processed_count += 1
        except Exception as e:
            logging.error(f"处理文件 {md_file} 时出错: {e}")

    return processed_count


def main(input_path: str, output_path: str) -> None:
    """
    主函数，执行 md 文件的重命名和保存操作。

    实现方式：
        调用相关函数，完成输入文件夹的 md 文件查找、处理和日志记录。

    入参说明：
        input_path (str): 输入文件夹的路径。
        output_path (str): 输出文件夹的路径。

    返回结果说明：
        None
    """
    # 设置输出文件夹
    output_dir = setup_output_directory(output_path)

    # 查找 md 文件
    md_files = find_md_files(input_path)
    total_subdirs = len([d for d in Path(input_path).iterdir() if d.is_dir()])
    total_md_files = len(md_files)

    # 处理 md 文件
    processed_count = process_md_files(md_files, output_dir)

    # 输出日志
    logging.info(f"输入文件夹中的一级子文件夹数量: {total_subdirs}")
    logging.info(f"找到的 md 文件数量: {total_md_files}")
    logging.info(f"成功处理的 md 文件数量: {processed_count}")
    logging.info(f"输出文件夹目录: {output_dir}")
    logging.info(f"输出文件夹内容: {[f.name for f in output_dir.iterdir()]}")


if __name__ == "__main__":
    input_folder = r"D:\Project\1. Super_Computer\2025\c03_js_wang_OpenAI_use\project-2\data\c0_source_document"  # 替换为实际输入文件夹路径
    output_folder = r"D:\Project\1. Super_Computer\2025\c03_js_wang_OpenAI_use\project-2\data\c1_preprocess\c1_rename_file"  # 替换为实际输出文件夹路径
    main(input_folder, output_folder)