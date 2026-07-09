import pandas as pd
import nltk
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge_score import rouge_scorer
from tqdm import tqdm

# 下载 nltk 必需的组件包（第一次运行会自动下载）
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    print("正在下载必要的 NLTK 组件，请稍候...")
    nltk.download('punkt')
    nltk.download('punkt_tab')

def calculate_similarity(generated_texts, test_texts):
    """
    计算生成数据集和测试集之间的最大与平均相似度 (BLEU-4 和 ROUGE-L)
    """
    # 初始化 ROUGE 计分器
    scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
    # BLEU 平滑函数（防止因为题目太短导致得分为0）
    smoothie = SmoothingFunction().method1

    max_bleu_overall = 0.0
    max_rouge_overall = 0.0

    sum_max_bleu = 0.0
    sum_max_rouge = 0.0

    print(f"开始计算相似度... 生成集规模: {len(generated_texts)}, 测试集规模: {len(test_texts)}")

    # 遍历每一道生成的题目
    for gen_text in tqdm(generated_texts, desc="Processing Generated Texts"):
        # 转为字符串并分词 (英文题目使用word_tokenize，如果是中文请用jieba.lcut)
        gen_str = str(gen_text).lower()
        gen_tokens = nltk.word_tokenize(gen_str)

        best_bleu_for_current = 0.0
        best_rouge_for_current = 0.0

        # 与测试集中的每一道题进行对比
        for test_text in test_texts:
            test_str = str(test_text).lower()
            test_tokens = nltk.word_tokenize(test_str)

            # 1. 计算 BLEU-4 (4-gram匹配度)
            bleu_score = sentence_bleu([test_tokens], gen_tokens,
                                       weights=(0.25, 0.25, 0.25, 0.25),
                                       smoothing_function=smoothie)

            # 2. 计算 ROUGE-L
            rouge_score = scorer.score(test_str, gen_str)
            rouge_l_f1 = rouge_score['rougeL'].fmeasure

            # 记录当前生成题目与测试集中最像的那道题的分数
            if bleu_score > best_bleu_for_current:
                best_bleu_for_current = bleu_score
            if rouge_l_f1 > best_rouge_for_current:
                best_rouge_for_current = rouge_l_f1

        # 累加每道题的最大分数，用于最后算平均值
        sum_max_bleu += best_bleu_for_current
        sum_max_rouge += best_rouge_for_current

        # 记录全局的最高分数
        if best_bleu_for_current > max_bleu_overall:
            max_bleu_overall = best_bleu_for_current
        if best_rouge_for_current > max_rouge_overall:
            max_rouge_overall = best_rouge_for_current

    # 计算平均最大相似度
    avg_max_bleu = sum_max_bleu / len(generated_texts)
    avg_max_rouge = sum_max_rouge / len(generated_texts)

    print("\n" + "=" * 40)
    print("🌟 数据泄露检测报告 🌟")
    print("=" * 40)
    print(f"最大 BLEU-4 分数 (Max BLEU-4): {max_bleu_overall:.4f}")
    print(f"平均 BLEU-4 分数 (Avg BLEU-4): {avg_max_bleu:.4f}")
    print("-" * 40)
    print(f"最大 ROUGE-L 分数 (Max ROUGE-L): {max_rouge_overall:.4f}")
    print(f"平均 ROUGE-L 分数 (Avg ROUGE-L): {avg_max_rouge:.4f}")
    print("=" * 40)


if __name__ == "__main__":
    # 您的文件路径
    gen_file_path = r"D:\PythonProjects\AstroCalcBoost\main\AstroConcept\6.数据生成\output_walk_steps_4\Earth_output_walk_result_steps_4.xlsx"
    test_file_path = r"D:\PythonProjects\eval\Astro_Cal_Eval\eval_data\eval_file\Astro_Cal_Eval_EN_test.xlsx"

    print("正在读取 Excel 文件...")
    # 读取 Excel 文件
    df_gen = pd.read_excel(gen_file_path)
    df_test = pd.read_excel(test_file_path)

    # 【重要提示！】：请将 'instruction' 修改为您 Excel 表格中真正存储“题目内容”的那一列的表头名称！
    # 例如：如果您的题目放在 'Question' 列，就改为 df_gen['Question']
    gen_column_name = 'Question'  # 请核对您的 steps6.xlsx 的列名
    test_column_name = 'Question'  # 请核对您的 Astro_Cal_Eval_EN_test.xlsx 的列名

    try:
        # 提取题目列并去除空值
        generated_questions = df_gen[gen_column_name].dropna().astype(str).tolist()
        test_questions = df_test[test_column_name].dropna().astype(str).tolist()

        # 开始计算
        calculate_similarity(generated_questions, test_questions)
    except KeyError as e:
        print(
            f"❌ 错误: 找不到列名 {e}。请检查您的 Excel 文件，确保填写的列名（gen_column_name 和 test_column_name）是正确的！")