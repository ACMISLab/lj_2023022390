import pandas as pd
import jieba
import re
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge import Rouge
import sacrebleu
from typing import Dict
import sys
from rouge_score import rouge_scorer
# import threading
# threading.stack_size(128*1024*1024)
sys.setrecursionlimit(100000)  # 增加递归深度限制

# 然后再运行你的ROUGE计算代码

def clean_text(text: str) -> str:
    """ 清理文本，去除多余空格（不去除标点符号） """
    cleaned_text = re.sub(r'\s+', ' ', text)  # 去除多余空格
    return cleaned_text.strip()  # 去除首尾空格


def extract_steps(text: str) -> str:
    # """ 提取解题步骤部分 """
    # # steps_start = re.search(r'解题步骤|步骤|Solution Steps|Solution steps', text)
    # # steps_start = re.search(r'.* ?|解题步骤|步骤', text)
    # steps_start = re.search(r'^.*$', text, re.DOTALL)  # 从开头到结尾匹配所有内容
    # if steps_start:
    #     steps_text = text[steps_start.start():]
    #     answer_start = re.search(r'最终答案|步骤数|答案|Final Answer|Answer|Final answer', steps_text)
    #     if answer_start:
    #         return steps_text[:answer_start.start()].strip()  # 提取到答案或步骤数前
    #     return steps_text.strip()
    # return ""
    if not isinstance(text, str):  # 增加类型检查，防止 NaN 报错
        return ""

        # 原来的 re.search(r'^.*$', text, re.DOTALL) 完全多余，text 本身就是全部内容
    steps_text = text

    # # 查找答案结束的位置
    # answer_start = re.search(r'最终答案|步骤数|答案|Final Answer|Answer|Final answer', steps_text)
    # if answer_start:
    #     return steps_text[:answer_start.start()].strip()
    return steps_text.strip()


def calculate_bleu(reference: str, student: str) -> float:
    reference_tokens = " ".join(jieba.cut(reference))  # 使用 jieba 分词
    student_tokens = " ".join(jieba.cut(student))  # 使用 jieba 分词

    # 使用 SmoothingFunction
    smoothing_function = SmoothingFunction().method1  # 选择平滑方法
    score = sentence_bleu([reference_tokens.split()], student_tokens.split(), smoothing_function=smoothing_function)

    return score * 100  # 转为百分制


# def calculate_rouge(reference: str, student: str) -> Dict[str, float]:
#     rouge = Rouge()
#     scores = rouge.get_scores(student, reference)[0]  # 直接使用原始文本
#     return {
#         'rouge-1': scores['rouge-1']['f'],
#         'rouge-2': scores['rouge-2']['f'],
#         'rouge-l': scores['rouge-l']['f']
#     }


def calculate_rouge(reference_steps: str, student_steps: str) -> Dict[str, float]:
    # 针对中文评估：使用 jieba 分词并用空格连接，确保 rouge_score 能正确按词级计算
    ref_tokens = " ".join(jieba.cut(reference_steps))
    stu_tokens = " ".join(jieba.cut(student_steps))

    # 初始化 scorer
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)

    # 计算分数
    scores = scorer.score(ref_tokens, stu_tokens)

    # 提取 F1 分数 (fmeasure)，并转换成你原代码字典期望的键名格式，保证向下兼容
    return {
        'rouge-1': scores['rouge1'].fmeasure,
        'rouge-2': scores['rouge2'].fmeasure,
        'rouge-l': scores['rougeL'].fmeasure
    }


def calculate_chrf(reference: str, student: str) -> float:
    score = sacrebleu.corpus_chrf([student], [[reference]])
    return score.score


def calculate_containment_score(reference: str, student: str) -> int:
    reference_words = set(jieba.cut(reference))  # 分词并去重
    student_words = set(jieba.cut(student))  # 分词并去重

    if reference_words.issubset(student_words):
        return 100  # 满分

    matched_words = len(reference_words.intersection(student_words))  # 计算重合的词
    total_words = len(reference_words)

    score = (matched_words / total_words) * 100 if total_words > 0 else 0
    return int(score)


def evaluate_answers(reference: str, student: str) -> Dict[str, float]:
    # if not reference or not student:
    #     return None
    reference_steps = extract_steps(reference)
    student_steps = extract_steps(student)

    if not reference_steps or not student_steps:
        # print("参考答案或学生答案为空，无法进行评估。")
        return None  # 返回 None，表示无法评估
    # if not reference_steps:
        # print("参考答案为空，无法进行评估。")
    #     return None  # 返回 None，表示无法评估
    # if not student_steps:
    #     print("学生答案为空，无法进行评估。")
    #     return None  # 返回 None，表示无法评估

    containment_score = calculate_containment_score(reference_steps, student_steps)
    bleu_score = calculate_bleu(reference_steps, student_steps)
    rouge_scores = calculate_rouge(reference_steps, student_steps)
    chrf_score = calculate_chrf(reference_steps, student_steps)

    integrated_score = (
            0.7 * containment_score +
            0.1 * bleu_score +
            0.1 * rouge_scores['rouge-1'] * 100 +  # 将 ROUGE 分数转换为百分制
            0.1 * chrf_score
    )

    # 输出各个分数
    # print(f"Containment Score: {containment_score:.2f}")
    # print(f"BLEU Score: {bleu_score:.2f}")
    # print(f"ROUGE-1 Score: {rouge_scores['rouge-1']:.2f}")
    # print(f"ROUGE-2 Score: {rouge_scores['rouge-2']:.2f}")
    # print(f"ROUGE-L Score: {rouge_scores['rouge-l']:.2f}")
    # print(f"chrF Score: {chrf_score:.2f}")
    # print(f"Integrated Score: {integrated_score:.2f}")

    return containment_score, bleu_score, rouge_scores['rouge-1'] * 100, rouge_scores['rouge-2'] * 100, rouge_scores['rouge-l'] * 100, chrf_score, integrated_score


def compare_step_content(file1: str, file2: str, reference_index: int, student_index: int) -> dict:
    df1 = pd.read_excel(file1)
    df2 = pd.read_excel(file2)

    column1 = df1.iloc[:, reference_index]
    column2 = df2.iloc[:, student_index]

    min_length = min(len(column1), len(column2))

    # 初始化分值总和
    total_scores = {
        "containment": 0,
        "bleu": 0,
        "rouge_1": 0,
        "rouge_2": 0,
        "rouge_l": 0,
        "chrf": 0,
        "integrated": 0,
        "final": 0,  # 新增 final score
    }

    valid_comparisons = 0  # 计数有效比较的行数

    # 用于保存每一行的分数
    all_scores = []  # 用于记录每一行的所有分数

    for i in range(min_length):
        reference = str(column1.iloc[i]).strip()  # 获取第7列的对应行数据并去除首尾空格
        student = str(column2.iloc[i]).strip()    # 获取第7列的对应行数据并去除首尾空格

        # 增加判断：如果转换后是 'nan'，则视为空
        if reference.lower() == 'nan': reference = ""
        if student.lower() == 'nan': student = ""
        reference_steps = extract_steps(reference)
        student_steps = extract_steps(student)
        if not reference_steps:
            print(f"第 {i + 1} 行参考答案为空，无法进行评估。")
        if not student_steps:
            print(f"第 {i + 1} 行学生答案为空，无法进行评估。")

        # 检查是否为空
        if not reference or not student:
            print(f"第 {i + 1} 行数据为空，跳过这一行。")
            continue

        # print(f"Comparing row {i + 1}:")
        scores = evaluate_answers(reference, student)

        if scores is None:  # 如果无法评估，跳过
            continue

        # 获取第11列和第12列的值
        weight_step = df1.iloc[i, 7]  # 第11列（索引为10）
        # weight_cal = df1.iloc[i, 11]  # 第12列（索引为11）

        # 将分值累加
        total_scores["containment"] += scores[0]
        total_scores["bleu"] += scores[1]
        total_scores["rouge_1"] += scores[2]
        total_scores["rouge_2"] += scores[3]
        total_scores["rouge_l"] += scores[4]
        total_scores["chrf"] += scores[5]

        # 计算 final score
        integrated_score = scores[6]

        # final_score = integrated_score * weight_cal * weight_step  # 计算 final score
        final_score = integrated_score * weight_step
        # final_score = integrated_score
        # print(f"Final Score for row {i + 1}: {final_score:.2f}")
        total_scores["integrated"] += integrated_score
        total_scores["final"] += final_score  # 累加 final score

        # 记录当前行的所有分数
        all_scores.append({
            "containment": scores[0],
            "bleu": scores[1],
            "rouge_1": scores[2],
            "rouge_2": scores[3],
            "rouge_l": scores[4],
            "chrf": scores[5],
            "integrated": integrated_score,
            "final": final_score
        })

        valid_comparisons += 1  # 计数有效行

        # print('-' * 50)  # 分隔线

    # 计算并输出各个分值的平均值
    if valid_comparisons > 0:
        avg_scores = {key: total / valid_comparisons for key, total in total_scores.items()}
        # print("各个分值的平均值：")
        # print(f"Average Containment Score: {avg_scores['containment']:.2f}")
        # print(f"Average BLEU Score: {avg_scores['bleu']:.2f}")
        # print(f"Average ROUGE-1 Score: {avg_scores['rouge_1']:.2f}")
        # print(f"Average ROUGE-2 Score: {avg_scores['rouge_2']:.2f}")
        # print(f"Average ROUGE-L Score: {avg_scores['rouge_l']:.2f}")
        # print(f"Average chrF Score: {avg_scores['chrf']:.2f}")
        # print(f"Average Integrated Score: {avg_scores['integrated']:.2f}")
        # print(f"Average Final Score: {avg_scores['final']:.2f}")  # 输出平均 final score

        # 将平均分数添加到返回结果中
        return {
            "all_scores": all_scores,
            "average_scores": avg_scores
        }
    else:
        print("没有有效的比较数据。")
        return {
            "all_scores": all_scores,
            "average_scores": None
        }


# if __name__ == "__main__":
#     # 指定要比较的两个 Excel 文件路径和第7列的索引（6）
#     reference_file = "D:\pythonprojects\gpt-4o\格式标准化\gpt-4o-mini基础天文学计算题整理.xlsx"  # 替换为您的第一个 Excel 文件路径
#     student_file = "D:\pythonprojects\eval\data\qwen-plus基础天文学计算题.xlsx"  # 替换为您的第二个 Excel 文件路径
#     column_index = 6  # 第7列的索引
#     compare_excel_columns(reference_file, student_file, column_index)