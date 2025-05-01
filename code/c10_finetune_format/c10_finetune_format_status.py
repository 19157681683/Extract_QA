import json

def count_json_objects(file_path):
    """
    统计输入文件中的总JSON对象数量

    主要实现方式：
        1. 打开并读取指定路径的文件内容
        2. 使用json模块解析文件内容为Python对象（通常是列表）
        3. 计算列表的长度即为JSON对象的数量
        4. 返回统计结果

    入参说明：
        file_path (str): 输入文件的路径，文件应包含有效的JSON数据（通常是一个JSON数组）

    返回结果说明：
        int: 文件中JSON对象的数量
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            if isinstance(data, list):
                return len(data)
            else:
                # 如果文件内容不是列表，则视为包含一个JSON对象
                return 1
    except FileNotFoundError:
        print(f"错误：文件 '{file_path}' 未找到。")
        return 0
    except json.JSONDecodeError:
        print(f"错误：文件 '{file_path}' 不是有效的JSON格式。")
        return 0
    except Exception as e:
        print(f"发生未知错误：{e}")
        return 0

# 示例用法
if __name__ == "__main__":
    # # window部署
    # file_path = r"D:\Project\1. Super_Computer\2025\c03_js_wang_OpenAI_use\project-2\data\c10_finetune_format\c2_deduplication"

    # window
    file_path = "/x32001214/project/2025/c03_js_wang_QA/project-2/data/c10_finetune_format\c2_deduplication"
    count = count_json_objects(file_path)
    print(f"文件中的JSON对象数量为：{count}")
