import pandas as pd
import json


def convert_xlsx_to_jsonl(xlsx_filename, jsonl_filename):
    # 读取Excel文件
    # system_prompt = (
    #     f'A conversation between User and Assistant. The user asks a question, and the Assistant solves it.\n '
    #     f'The assistant first thinks about the reasoning process in the mind and then provides the user with the answer.\n '
    #     f'The reasoning process and answer are enclosed within <think> </think> and <answer> </answer> tags, respectively, i.e., <think> reasoning process here </think>: <answer> answer here </answer>.\n '
    # )
    system_prompt = (
        f'A conversation between User and Assistant. The user asks a question, and the Assistant solves it.\n '
        f'The assistant first thinks about the reasoning process in the mind and then provides the user with the answer.\n '
        )
    df = pd.read_excel(xlsx_filename)  # header=None表示没有标题行

    # 打开JSONL文件进行写入
    with open(jsonl_filename, 'w', encoding='utf-8') as jsonl_file:
        # 遍历每一行数据
        for index, row in df.iterrows():
            # 假设think列的索引为3，answer列的索引为7
            think_content = row.iloc[8]  # 获取think列内容
            answer_content = row.iloc[6]  # 获取answer列内容

            # 构造assistant的内容
            think_content1 = f"<think>{think_content}</think>"
            # think_content1 = f"<think>{think_content}</think>"
            answer_content1 = (f"<answer>"
                               f"The answer is {answer_content}"
                               f"</answer>")

            # 构造所需的JSON格式
            conversation_entry = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": row.iloc[2]},  # user列的索引保持为2
                    # {"role": "assistant", "content": think_content1, "tool_calls":None},# 使用组合后的内容
                    {"role": "assistant", "content": think_content1},
                    {"role": "assistant", "content": answer_content1}
                ]
            }
            # 将字典转换为JSON字符串并写入文件
            jsonl_file.write(json.dumps(conversation_entry, ensure_ascii=False) + '\n')


# 使用示例
# xlsx_filename = r"C:\Users\lijie\Downloads\天文计算题\COT.xlsx" # 请替换为你的Excel文件名
# jsonl_filename = r"C:\Users\lijie\Downloads\天文计算题\COT.jsonl"  # 输出的JSONL文件名
xlsx_filename = r"D:\PythonProjects\AstroCalcBoost\main\MetaMath\fobar_cot.xlsx"
jsonl_filename = r"D:\PythonProjects\AstroCalcBoost\main\MetaMath\fobar_cot0514.jsonl"
convert_xlsx_to_jsonl(xlsx_filename, jsonl_filename)

print(f"Excel文件 '{xlsx_filename}' 已成功转换为JSONL格式并保存为 '{jsonl_filename}'")