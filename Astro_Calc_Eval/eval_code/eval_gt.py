import pandas as pd
import re
from eval_step_calc import validate_calculation

# def _fix_fracs(string):
#     substrs = string.split("\\frac")
#     new_str = substrs[0]
#     if len(substrs) > 1:
#         substrs = substrs[1:]
#         for substr in substrs:
#             new_str += "\\frac"
#             if substr[0] == "{":
#                 new_str += substr
#             else:
#                 try:
#                     assert len(substr) >= 2
#                 except:
#                     return string
#                 a = substr[0]
#                 b = substr[1]
#                 if b != "{":
#                     if len(substr) > 2:
#                         post_substr = substr[2:]
#                         new_str += "{" + a + "}{" + b + "}" + post_substr
#                     else:
#                         new_str += "{" + a + "}{" + b + "}"
#                 else:
#                     if len(substr) > 2:
#                         post_substr = substr[2:]
#                         new_str += "{" + a + "}" + b + post_substr
#                     else:
#                         new_str += "{" + a + "}" + b
#     string = new_str
#     return string
def _fix_fracs(string):
    # 使用正则表达式查找所有\frac{分子}{分母}格式的内容
    pattern = r'\\frac\{([^}]+)\}\{([^}]+)\}'

    def replace_frac(match):
        numerator = match.group(1)
        denominator = match.group(2)

        try:
            # 尝试将分子和分母转换为数值
            num_val = float(numerator)
            den_val = float(denominator)

            if den_val == 0:
                return match.group(0)  # 分母为0，保持原样

            result = num_val / den_val
            return f"{result:.6f}"  # 返回6位小数的结果
        except (ValueError, ZeroDivisionError):
            # 如果转换失败，保持原样
            return match.group(0)

    # 替换所有\frac{}{}格式
    new_string = re.sub(pattern, replace_frac, string)
    return new_string

def _fix_a_slash_b(string):
    if len(string.split("/")) != 2:
        return string
    a = string.split("/")[0]
    b = string.split("/")[1]
    try:
        a = int(a)
        b = int(b)
        assert string == "{}/{}".format(a, b)
        new_string = "\\frac{" + str(a) + "}{" + str(b) + "}"
        return new_string
    except:
        return string


def _remove_right_units(string):
    if "\\text{ " in string:
        splits = string.split("\\text{ ")
        assert len(splits) == 2
        return splits[0]
    else:
        return string


def _fix_sqrt(string):
    if "\\sqrt" not in string:
        return string
    splits = string.split("\\sqrt")
    new_string = splits[0]
    for split in splits[1:]:
        if split[0] != "{":
            a = split[0]
            new_substr = "\\sqrt{" + a + "}" + split[1:]
        else:
            new_substr = "\\sqrt" + split
        new_string += new_substr
    return new_string


def _strip_string(string):
    # remove dollar signs
    string = string.replace("$", "")
    string = string.replace("\\$", "")

    # linebreaks
    string = string.replace("\n", "")

    # remove inverse spaces
    string = string.replace("\\!", "")

    # replace \\ with \
    string = string.replace("\\\\", "\\")

    # replace tfrac and dfrac with frac
    string = string.replace("tfrac", "frac")
    string = string.replace("dfrac", "frac")

    # remove \left and \right
    string = string.replace("\\left", "")
    string = string.replace("\\right", "")

    # Remove circ (degrees)
    string = string.replace("^{\\circ}", "")
    string = string.replace("^\\circ", "")

    # remove units (on the right)
    string = _remove_right_units(string)

    # Handle scientific notation
    string = re.sub(r'(\d+\.?\d*) \\times 10\^(\d+)',
                     lambda match: str(int(float(match.group(1)) * (10 ** int(match.group(2))))),
                     string)

    # remove percentage
    string = string.replace("\\%", "")
    string = string.replace("\%", "")

    # " 0." equivalent to " ." and "{0." equivalent to "{." Alternatively, add "0" if "." is the start of the string
    string = string.replace(" .", " 0.")
    string = string.replace("{.", "{0.")

    # if empty, return empty string
    if len(string) == 0:
        return string
    if string[0] == ".":
        string = "0" + string

    # to consider: get rid of e.g. "k = " or "q = " at beginning
    if len(string.split("=")) == 2:
        if len(string.split("=")[0]) <= 2:
            string = string.split("=")[1]

    # fix sqrt3 --> sqrt{3}
    string = _fix_sqrt(string)

    # remove spaces
    string = string.replace(" ", "")

    # \frac1b or \frac12 --> \frac{1}{b} and \frac{1}{2}, etc. Even works with \frac1{72} (but not \frac{72}1). Also does a/b --> \\frac{a}{b}
    string = _fix_fracs(string)

    # manually change 0.5 --> \frac{1}{2}
    if string == "0.5":
        string = "\\frac{1}{2}"

    # NOTE: X/Y changed to \frac{X}{Y} in dataset, but in simple cases fix in case the model output is X/Y
    string = _fix_a_slash_b(string)

    # Remove all non-numeric characters except for signs and dots
    numeric_string = ''.join(c for c in string if c.isdigit() or c in '-.')

    # Remove leading '-' if present
    if numeric_string.startswith('-'):
        numeric_string = numeric_string[1:]  # Remove the negative sign

    # Convert units: km/s to m/s for specific cases
    if 'km/s' in string:
        try:
            speed_kmh = float(numeric_string)
            speed_mps = speed_kmh * 1000  # Convert km/s to m/s
            numeric_string = str(int(speed_mps))  # Convert to integer string
        except ValueError:
            return numeric_string
    elif 'km' in string:
        try:
            speed_km = float(numeric_string)
            speed_mps = speed_km * 1000  # Convert km to m/s
            numeric_string = str(int(speed_mps))  # Convert to integer string
        except ValueError:
            return numeric_string

    # Convert to float and round to 2 decimal places for comparison
    try:
        numeric_value = float(numeric_string)
        rounded_value = round(numeric_value, 2)
        numeric_string = f"{rounded_value:.2f}"  # Format back to string with 2 decimal places
    except ValueError:
        # Handle cases where conversion to float fails
        return string

    return numeric_string


def remove_boxed(s):
    # 用正则表达式匹配以 \boxed{ 开头并以最后一个 } 结尾的内容
    pattern = r'\\boxed\{(.*(?:\{[^}]*\}[^}]*)*)\}'  # 非贪婪匹配，直到最后一个 }
    # pattern = r'boxed\{(.*(?:\{[^}]*\}[^}]*)*)\}'  # 非贪婪匹配，直到最后一个 }

    # 找到所有匹配的内容
    matches = re.findall(pattern, s)

    if matches:
        # 只返回最后一个匹配的内容
        return matches[-1]
    # return s
    # # return matches
    # 如果没有匹配到 \boxed{}，返回 None
    return '0'

def is_equiv(str1, str2):
    if str1 is None and str2 is None:
        print("WARNING: Both None")
        return True
    if str1 is None or str2 is None:
        return False

    try:
        ss1 = _strip_string(str1)
        ss2 = _strip_string(str2)
        # if verbose:
        #     print(ss1, ss2)
        # return validate_calculation(ss1) == validate_calculation(ss2)
        return ss1 == ss2
    except:
        return str1 == str2


# def compare_gt(file1, file2, reference_index, student_index):
#     # 读取 Excel 文件
#     df1 = pd.read_excel(file1)
#     df2 = pd.read_excel(file2)
#
#     # 确保两个 DataFrame 行数一致
#     if len(df1) != len(df2):
#         print("两文件行数不一致！")
#         return
#
#     # 遍历每一行进行比较
#     final_score = 0
#     for i in range(len(df1)):
#         reference = df1.iloc[i]
#         output = df2.iloc[i]
#
#         str1 = str(reference.iloc[reference_index])
#         str2 = str(output.iloc[student_index])
#
#         # 使用 remove_boxed 函数处理字符串
#         str1 = remove_boxed(str1)
#         str2 = remove_boxed(str2)
#
#         # 添加新规则：检查提取到的内容是否包含10个以上的0
#         # 检查str2（学生答案）中连续0的个数
#         if str2 is not None:
#             # 方法1：统计所有0的个数
#             # zero_count = str2.count('0')
#
#             # 方法2：统计连续0的个数（如果需要更严格的判断）
#             continuous_zeros = re.findall(r'0{10,}', str2)
#             has_excessive_zeros = len(continuous_zeros) > 0
#
#             # 如果0的个数超过10个，直接判断为错
#             if zero_count >= 10:
#                 # print(f"Row {i+1}: 检测到{zero_count}个0，直接判断为错")
#                 continue  # 不增加分数，跳过当前循环
#
#         # print(f"str1:'{str1}',str2:'{str2}'")
#
#         result = is_equiv(str1, str2)
#         if result:
#             final_score += 1
#         print(f"Row {i+1}: Comparing '{str1}' and '{str2}' => Result: {result}")
#
#     return final_score


def compare_gt(file1, file2, reference_index, student_index):
    # 读取 Excel 文件
    df1 = pd.read_excel(file1)
    df2 = pd.read_excel(file2)

    # 确保两个 DataFrame 行数一致
    if len(df1) != len(df2):
        print("两文件行数不一致！")
        return

    # 遍历每一行进行比较
    final_score = 0
    for i in range(len(df1)):
        reference = df1.iloc[i]
        output = df2.iloc[i]

        str1 = str(reference.iloc[reference_index])
        str2 = str(output.iloc[student_index])

        # 使用 remove_boxed 函数处理字符串
        str1 = remove_boxed(str1)
        str2 = remove_boxed(str2)

        # 检查str2（学生答案）中是否包含20个或以上的连续0
        if str2 is not None:
            # 使用正则表达式查找连续0的序列
            continuous_zeros_matches = re.findall(r'0{20,}', str2)

            # 检查是否存在连续20个或更多0的序列
            if continuous_zeros_matches:
                # 获取最大连续0的个数
                max_continuous_zeros = max(len(match) for match in continuous_zeros_matches)
                # print(f"Row {i+1}: 检测到{max_continuous_zeros}个连续0，直接判断为错")
                continue  # 不增加分数，跳过当前循环

        # print(f"str1:'{str1}',str2:'{str2}'")

        result = is_equiv(str1, str2)
        if result:
            final_score += 1
        # print(f"Row {i + 1}: Comparing '{str1}' and '{str2}' => Result: {result}")

    return final_score
#
# if __name__ == "__main__":
# #     # 替换为你的 Excel 文件路径
# #     # reference_file = r"C:\Users\lijie\Downloads\天文计算题\GSM8K_test.xlsx"
#     reference_file = r"D:\PythonProjects\eval\RandomGenerate\finance_precision_test.xlsx"
# # #     reference_file = r"C:\Users\lijie\Downloads\天文计算题\OlympiadBench_test.xlsx"
#     output_file = r"D:\PythonProjects\AstroCalcBoost2\main\formula_scale_exp\eval_results\Finance_Eval_GPT-4o-mini.xlsx"
# # #     # output_file = r"C:\Users\lijie\Documents\NetSarang Computer\8\Xftp\Temporary\Qwen_ours_3B-0629 [2].xlsx"
# # #     # output_file = r"C:\Users\lijie\Documents\NetSarang Computer\8\Xftp\Temporary\Qwen_GRPO_3B-0629 [2].xlsx"
# # #     # output_file = r"C:\Users\lijie\Documents\NetSarang Computer\8\Xftp\Temporary\Qwen_7B-0629.xlsx"
# # #     # 指定要比较的列，可以根据需要修改
#     reference_index = 10 # 替换为实际的列名
#     student_index = 10
# # #
#     compare_gt(reference_file, output_file, reference_index,student_index)


# print(is_equiv(r"\\frac{65}{90}",r"\\frac{13}{18}"))
# print(is_equiv(r"\[\boxed{\frac{65}{90}}\]",r"$\boxed{\frac{13}{18}}$"))
# print(remove_boxed(r"e identified as coinciding with Halo Events is $\boxed{\frac{13}{18}}$."))
# print(remove_boxed(r"\["
#                r"\boxed{1.66 \times 10^{32}}"
#                r"\]"))