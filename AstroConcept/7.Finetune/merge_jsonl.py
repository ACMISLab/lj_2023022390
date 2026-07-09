import json


def merge_jsonl(file1_path, file2_path, output_path):
    with open(output_path, 'w', encoding='utf-8') as outfile:
        # 写入第一个文件内容
        with open(file1_path, 'r', encoding='utf-8') as f1:
            for line in f1:
                outfile.write(line)

        # 写入第二个文件内容
        with open(file2_path, 'r', encoding='utf-8') as f2:
            for line in f2:
                outfile.write(line)


# 示例调用
merge_jsonl(r"C:\Users\lijie\Downloads\天文计算题\KG-step-4+6+7+8+Rephrase_NASA+forbar_cot+metamath.jsonl",
            r"D:\PythonProjects\AstroCalcBoost2\main\MAmmoTH\MAmmoTH.jsonl",
            r"C:\Users\lijie\Downloads\天文计算题\KG-step-4+6+7+8+Rephrase_NASA+forbar_cot+metamath+mammoth.jsonl")
# # 统计合并后的文件行数
# with open(r"C:\Users\lijie\Downloads\天文计算题\KG1-4000+Rephrase_NASA.jsonl", 'r', encoding='utf-8') as f:
#     line_count = sum(1 for _ in f)
# print(f"合并后的文件行数为: {line_count}")