from eval_step_content import compare_step_content
from eval_step_calc import calculation_eval
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
    reference_file = r"D:\PythonProjects\eval\Astro_Calc_Eval\eval_data\reference_file\Astro_Cal_Ref_EN_test.xlsx"
    reference_index = 4

    student_file = r"C:\Users\lijie\Downloads\复现\AstroConcept-8B\AstroConcept_8B_复现1.xlsx"
    student_index = 4
    # 题目个数
    QA_Count = 457



    # 解题步骤评估
    content_results = compare_step_content(reference_file, student_file, reference_index, student_index)
    content_final_score = print_comparison_results(content_results)
    astrocalc_content_score = content_final_score*0.25
    print(f"AstroCalcBench-Step-Content得分：{astrocalc_content_score}")
    print('-' * 50)  # 分隔线

    # 计算能力评估
    total_count, total_score = calculation_eval(student_file, student_index)
    print("计算过程得分:")
    print(f"计算题总数 = {total_count}, 计算题总得分 = {total_score}, 计算题总正确率 = {total_score/total_count*100:.2f}%")
    astrocalc_calc_score = (total_score/total_count)*25
    print(f"AstroCalcBench-Calc-Accuracy得分：{astrocalc_calc_score}")
    print('-' * 50)  # 分隔线
    #
    # 最终答案评估
    gt_results = compare_gt(reference_file, student_file, reference_index, student_index)
    print(f"最终答案正确数量：{gt_results}\n")
    astrocalc_gt_score = (gt_results/QA_Count)*50
    print(f"AstroCalcBench-Final_Answer得分：{astrocalc_gt_score}")
    print('-' * 50)  # 分隔线
    #
    final_3_score = astrocalc_gt_score + astrocalc_calc_score + astrocalc_content_score
    # final_3_score = astrocalc_gt_score + astrocalc_content_score
    print(f"大模型天文计算推理能力评估最终得分：{final_3_score}")