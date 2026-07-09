from eval_step_content import compare_step_content
from eval_step_cal_NEW import calculation_eval
from eval_gt import compare_gt

def print_comparison_results(results):
    """ 输出比较结果的分数和平均分数 """
    # 输出所有分数
    all_scores = results['all_scores']
    average_scores = results['average_scores']

    # for i, score in enumerate(all_scores):
    #     print(f"第 {i + 1} 行的分数: {score}")

    print("解题步骤得分:")
    if average_scores:
        for key, value in average_scores.items():
            print(f"{key.capitalize()} Score: {value:.2f}")
    else:
        print("没有有效的平均分数数据。")

    return average_scores["final"]


if __name__ == "__main__":
    # 指定要比较的两个 Excel 文件路径和第7列的索引（6）
    # reference_file = "D:\PythonProjects\gpt-4o\格式标准化\gpt-4o-mini基础天文学计算题整理-英文版.xlsx"  # 替换为您的第一个 Excel 文件路径
    # reference_file = r"D:\PythonProjects\eval\Astro_Cal_Eval\eval_data\reference_file\Astro_Cal_Ref_EN.xlsx"
    # reference_file = r"D:\PythonProjects\AstroCalcBoost2\main\formula_scale_exp\formula_overall_scale_90.xlsx"
    # reference_file = r"D:\PythonProjects\eval\Astro_Cal_Eval\eval_data\reference_file\NASA_Ref_3_9.xlsx"
    reference_file = r"D:\PythonProjects\eval\Astro_Cal_Eval\eval_data\reference_file\Astro_Cal_Ref_EN_test.xlsx"
    reference_index = 4
    # reference_index = 8

    # student_file = r"C:\Users\lijie\Downloads\Astro_Cal_Eval_EN_Llama-3-8B-Step4678-SFT-1129.xlsx"
    # student_file =r"C:\Users\lijie\Documents\NetSarang Computer\8\Xftp\Temporary\Astro_Cal_Eval_EN_Llama-3-8B-AstroConcept-0302.xlsx"
    student_file = r"D:\PythonProjects\AstroCalcBoost2\main\new2\test_results\qwen\Astro_Cal_Eval_test_qwen_32B_CoC.xlsx"
    # "C:\Users\lijie\Downloads\Astro_Cal_Eval_EN_Qwen3-32B-astroconcept0126.xlsx"
    # "D:\PythonProjects\eval\Astro_Cal_Eval\eval_results\GPT\Astro_Cal_Eval_EN_GPT-4o-mini_NASA_3_9 -175.xlsx"
    # "D:\PythonProjects\AstroCalcBoost2\main\test_results\NASA_Eval_3_9_GPT-4o-mini.xlsx"
    # "D:\PythonProjects\eval\Astro_Cal_Eval\eval_results\GPT\Astro_Cal_Eval_EN_GPT-4o-mini_NASA_3_9.xlsx"
    # "D:\PythonProjects\AstroCalcBoost2\main\new\test_results\NASA_Eval_3_9_GPT-4o-mini_PoT.xlsx"
    # "D:\PythonProjects\AstroCalcBoost2\main\new\test_results\NASA_Eval_3_9_GPT-4o-mini_CoT+py.xlsx"
    # "D:\PythonProjects\AstroCalcBoost2\main\new\test_results\NASA_Eval_3_9_GPT-4o-mini_CoT+py_new.xlsx"
    # "D:\PythonProjects\eval\Astro_Cal_Eval\eval_results\GPT\Astro_Cal_Eval_EN_GPT-4o-mini_NASA_3_9.xlsx"
    # "D:\PythonProjects\eval\Astro_Cal_Eval\eval_results\AstroConcept\Astro_Cal_Eval_EN_Qwen3-14B-SFT.xlsx"
    # "C:\Users\lijie\Downloads\Astro_Cal_Eval_EN_Qwen3-14B-astroconcept0122.xlsx"
    # "C:\Users\lijie\Downloads\AstroConcept8B_NASA3_9.xlsx"
    # "D:\PythonProjects\eval\Astro_Cal_Eval\eval_results\AstroConcept\Astro_Cal_Eval_EN_Llama-3-8B-Instruct-SFT_NASA-3_9.xlsx"
    # "D:\PythonProjects\eval\Astro_Cal_Eval\eval_results\AstroConcept\Astro_Cal_Eval_EN_Llama-3-8B-astroconcept0110_NASA_3_9.xlsx"
    # "C:\Users\lijie\Downloads\AstroConcept8B_NASA3_9_0128.xlsx"
    # "D:\PythonProjects\AstroCalcBoost2\main\new2\test_results\NASA_Eval_3_9_GPT-4o-mini_CoT+py_new2.xlsx"
    # "D:\PythonProjects\AstroCalcBoost2\main\Chain of Code\NASA_Eval_3_9_CoC_Result.xlsx"
    # "D:\PythonProjects\AstroCalcBoost2\main\CoT\NASA_Eval_3_9_CoT_Result.xlsx"
    # "D:\PythonProjects\AstroCalcBoost2\main\PoT\NASA_Eval_3_9_PoT_Result.xlsx"
    # "D:\PythonProjects\AstroCalcBoost2\main\new2\ablation_results\ablation_on_stage1.xlsx"
    # "D:\PythonProjects\AstroCalcBoost2\main\new2\ablation_results\ablation_on_stage3.xlsx"
    # "D:\PythonProjects\eval\Astro_Cal_Eval\eval_results\GPT\Astro_Cal_Eval_EN_GPT-4o-mini_3_9_0306.xlsx"
    # "D:\PythonProjects\AstroCalcBoost2\main\new2\ablation_results\ablation_on_stage2.xlsx"
    # "D:\PythonProjects\AstroCalcBoost2\main\new2\test_results\NASA_Eval_3_9_GPT-4o-mini_CoT+py_new2_0311.xlsx"
    # "D:\PythonProjects\AstroCalcBoost2\main\new2\ablation_results\ablation_on_stage1_0313.xlsx"

    student_index = 4
    # 题目个数
    # QA_Count = 1609
    QA_Count = 457
    # QA_Count = 316
    # QA_Count = 260
    # QA_Count = 175
    # QA_Count = 95

    # 解题步骤评估
    content_results = compare_step_content(reference_file, student_file, reference_index, student_index)
    content_final_score = print_comparison_results(content_results)
    astrocalc_content_score = content_final_score*0.3
    print(f"AstroCal-Step-Content得分：{astrocalc_content_score}")
    print('-' * 50)  # 分隔线

    # 计算能力评估
    total_count, total_score = calculation_eval(student_file, student_index)
    print("计算过程得分:")
    print(f"计算题总数 = {total_count}, 计算题总得分 = {total_score}, 计算题总正确率 = {total_score/total_count*100:.2f}%")
    astrocalc_calc_score = (total_score/total_count)*20
    print(f"AstroCal-Cal-Step得分：{astrocalc_calc_score}")
    print('-' * 50)  # 分隔线
    #
    # 最终答案评估
    gt_results = compare_gt(reference_file, student_file, reference_index, student_index)
    print(f"最终答案正确数量：{gt_results}\n")
    astrocalc_gt_score = (gt_results/QA_Count)*50
    print(f"AstroCal-Final_Answer得分：{astrocalc_gt_score}")
    print('-' * 50)  # 分隔线
    #
    final_3_score = astrocalc_gt_score + astrocalc_calc_score + astrocalc_content_score
    # final_3_score = astrocalc_gt_score + astrocalc_content_score
    print(f"大模型天文计算推理能力评估最终得分：{final_3_score}")