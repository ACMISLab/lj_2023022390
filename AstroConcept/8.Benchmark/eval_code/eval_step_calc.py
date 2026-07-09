import re
import math
import pandas as pd
from sympy import symbols, simplify, pi, sympify


def _replace_units_with_scalars(expr, mode='scalar'):
    exact_map = {
        'kilometer': '*(1000)',
        'kilometers': '*(1000)',
        'km': '*(1000)',
        'meter': '*(1)',
        'meters': '*(1)',
        'm': '*(1)',
        'millimeter': '*(0.001)',
        'millimeters': '*(0.001)',
        'mm': '*(0.001)',
        'nm': '*(1e-9)',
        'cm': '*(0.01)',
        'W': '*(1)',
        'ergs/sec': '*(1e-7)',
        'erg': '*(1e-7)',
        'ergs': '*(1e-7)',
        'J': '*(1)',
        'sec': '*(1)',
        'seconds': '*(1)',
        'second': '*(1)',
        's': '*(1)',
        'hour': '*(3600)',
        'hours': '*(3600)',
        'hr': '*(3600)',
        'h': '*(3600)',
        'light-year': '*(9.461e15)',
        'ly': '*(9.461e15)',
        'atom/cm^3': '*(1.67e-27)',
        'atom/cm^{3}': '*(1.67e-27)',
        'atom': '*(1.67e-27)',
        'atoms': '*(1.67e-27)',
        'kg': '*(1)',
        'AU': '*(1.496e11)',
        'pc': '*(3.073e16)',
    }

    # 匹配 \text{...}, \mathrm{...}, \mbox{...} 以及可选的后续指数
    pattern = r'\\(?:text|mathrm|mbox|bf|it)\s*\{([^\}]+)\}(\s*\^\s*\{?-?\d+\}?)?'

    def unit_replacer(match):
        content = match.group(1).strip()
        exponent = match.group(2) or ''

        # 剥离模式：直接删除所有文本单位及其指数
        if mode == 'strip':
            return ''

        # 1. 尝试完全匹配（包括指数的情况，如 atom/cm^3）
        combined = content + exponent.replace(' ', '')
        if combined in exact_map:
            return exact_map[combined]

        # 2. 词汇级别匹配替换
        replaced = content
        base_keys = [k for k in exact_map.keys() if '^' not in k]
        for k in sorted(base_keys, key=len, reverse=True):
            val = exact_map[k].replace('*', '')
            replaced = re.sub(r'\b' + re.escape(k) + r'\b', val, replaced)

        # 清理多余的纯字母单词
        replaced = re.sub(r'\b[a-zA-Z]+\b', '', replaced)
        # 去除多余的符号如独立的 / 等
        replaced = replaced.replace('/', '').strip()

        # 如果替换后没有数字剩余，则仅返回可能存在的指数（或者空）
        if not re.search(r'\d', replaced):
            return exponent

        return '*' + replaced.strip() + exponent

    return re.sub(pattern, unit_replacer, expr)


def _convert_scientific_notation(string):
    # 将 LaTeX 科学计数法转换为 Python 数值字符串，支持负指数和花括号
    return re.sub(r'(\d+(?:\.\d+)?)\s*\\times\s*10\^\{?(-?\d+)\}?',
                  lambda match: str(float(match.group(1)) * (10 ** int(match.group(2)))),
                  string)


def _remove_inequality_left(string):
    # 使用正则表达式匹配不等式符号及其左边的内容
    return re.sub(r'.*?(\s*[<>=]\s*|\\geq\s*|\\leq\s*|\\neq\s*)', '', string)


def latex_to_python(expr, mode='scalar'):
    # 1. 先移除不等式左侧（如果是方程右侧校验模式）
    expr = _remove_inequality_left(expr)

    # 2. 根据模式（标量乘数 或 彻底剥离）处理单位
    expr = _replace_units_with_scalars(expr, mode)

    # 3. 清理常见的 LaTeX 间距和特殊符号
    expr = re.sub(r'\\(,|;| |quad|qquad|!)', ' ', expr)

    # 4. 去除千分位逗号，确保不干扰后续科学计数法的解析
    expr = expr.replace(',', '')

    # 5. 转换科学计数法
    expr = _convert_scientific_notation(expr)

    # 6. 替换 \left 和 \right 为普通括号，乘号替换为 *
    expr = expr.replace("\\left", "(").replace("\\right", ")")
    expr = expr.replace('\\times', '*')
    expr = expr.replace('\\cdot', '*')

    # 7. 清理度数符号和其他残留
    expr = expr.replace("^{\\circ}", "").replace("^\\circ", "").replace("'", "").strip()

    # 8. 处理分数
    expr = re.sub(r'\\frac{(.*?)}{(.*?)}', r'(\1)/(\2)', expr)

    # 9. 处理幂运算
    expr = re.sub(r'\^{(.*?)}', r'**(\1)', expr)
    expr = expr.replace('^', '**')

    # 10. 最终清理：删除剩余的反斜杠（非转义字符）
    expr = re.sub(r'(?<!\\)\\(?!frac)', '', expr)
    expr = re.sub(r'\s+', ' ', expr).strip()

    return expr

def extract_calculations_with_equals_after_solution_steps(text):
    # steps_section = re.search(r'解题步骤([\s\S]*?)(最终答案|$)', text)
    # steps_section = re.search(r'Solution steps([\s\S]*?)(Final answer|$)', text)
    # steps_section = re.search(r'<think>([\s\S]*?)<\/think>', text)
    # steps_section = re.search(r'<reasoning>([\s\S]*?)<\/reasoning>', text)
    # steps_section = re.search(r'([\s\S]*?)(最终答案)', text)
    steps_section = re.search(r'(.*)', text, re.DOTALL)
    if steps_section:
        steps_content = steps_section.group(1)
        # 查找所有包含等号的表达式
        calculations_latex = re.findall(r'\\\((.*?)\\\)', steps_content)
        calculations_display = re.findall(r'\\\[(.*?)\\\]', steps_content, re.DOTALL)
        calculations_dollar = re.findall(r'\$(.*?)\$', steps_content)
        calculations_2dollar = re.findall(r'\$\$(.*?)\$\$', steps_content)

        calculations = calculations_latex + calculations_display + calculations_dollar + calculations_2dollar

        calculations_with_equals = []
        for calc in calculations:
            # 将 \approx 转换为 =
            calc = calc.replace('\\approx', '=')
            if '=' in calc:
                parts = calc.split('=')
                if len(parts) == 2:
                    calculations_with_equals.append(calc)
                else:
                    last_part = '='.join(parts[-2:])
                    calculations_with_equals.append(last_part)

        return calculations_with_equals
    return []


def numerical_equal(expression1: str, expression2: str):
    """
    比较两个浮点数表达式，允许一定的误差范围。
    如果能正确解析并比对出结果，返回 1 (Valid)；比对不成立则返回 False，成立返回 True。
    如果遇到解析失败，则返回 0 (Invalid) 和 False。
    """
    try:
        reference = float(expression1)
        prediction = float(expression2)

        # 允许一定误差进行比对
        is_equal = round(reference, 2) == round(prediction, 2)
        is_valid = 1
        return is_valid, is_equal
    except ValueError:
        return 0, False


def validate_calculation(calculation):
    """
    验证一个算式（形如 A = B）两边是否在数值或物理等效上相等。
    使用了“双模式”验证：
    模式1 (Scalar)：将单位转换为物理学标量基数进行等效计算验证（兼容：1 km = 1000 m）。
    模式2 (Strip)：无视/强制剥离所有文本单位后进行纯数字计算验证（兼容：400 * 3600 = 1440000 km/h）。
    """
    try:
        parts = calculation.split('=')
        if len(parts) != 2:
            return None
        left = parts[0].strip()
        right = parts[1].strip()

        # ---------- 模式 1：单位转为标量 ----------
        is_equal_scalar = False
        is_valid_scalar = 0
        try:
            l_expr_s = latex_to_python(left, mode='scalar')
            r_expr_s = latex_to_python(right, mode='scalar')

            l_eval_s = simplify(sympify(l_expr_s))
            r_eval_s = simplify(sympify(r_expr_s))

            is_valid_scalar, is_equal_scalar = numerical_equal(l_eval_s, r_eval_s)
        except Exception:
            pass

        # ---------- 模式 2：完全剥离单位 ----------
        is_equal_strip = False
        is_valid_strip = 0
        try:
            l_expr_st = latex_to_python(left, mode='strip')
            r_expr_st = latex_to_python(right, mode='strip')

            l_eval_st = simplify(sympify(l_expr_st))
            r_eval_st = simplify(sympify(r_expr_st))

            is_valid_strip, is_equal_strip = numerical_equal(l_eval_st, r_eval_st)
        except Exception:
            pass

        # ---------- 综合判定 ----------
        # 任一模式认为计算正确，即返回正确 (1, True)
        if (is_valid_scalar and is_equal_scalar) or (is_valid_strip and is_equal_strip):
            return 1, True

        # 若皆不正确，但至少有一个能正常解析出有效数值，则返回有效但错误 (1, False)
        if is_valid_strip:
            return 1, False
        if is_valid_scalar:
            return 1, False

        # 若都无法正常解析数值，视为无效表达式
        return 0, False

    except Exception as e:
        return None

def calculation_eval(file_path,column_index):
    # 读取 Excel 文件
    df = pd.read_excel(file_path)

    sixth_column_data = df.iloc[:, column_index]  # 第六列索引为 5
    total_count = 0
    total_score = 0
    # 提取计算内容
    for idx, input_text in enumerate(sixth_column_data, start=1):
        cal_score = 0
        valid_count = 0
        input_text = str(input_text)  # 转换为字符串

        # 输出原始内容
        # print(f"第 {idx} 行原始内容: {input_text}")
        # print('-' * 30)  # 分隔线
        extracted_calculations = extract_calculations_with_equals_after_solution_steps(input_text)

        # 统计提取的计算内容数量
        calculation_count = len(extracted_calculations)
        # print(f"第 {idx} 题提取的计算内容数量: {calculation_count}")
        # print('-' * 30)  # 分隔线

        # 验证提取的计算内容
        for calc in extracted_calculations:
            result = validate_calculation(calc)
            if result is not None:
                is_valid, is_equal = result
                # 检查 is_valid，并更新计数器
                if is_valid:
                    valid_count += 1
                if is_equal:
                    cal_score += 1
                # if is_valid and not is_equal:
                #     print(f"第 {idx} 题计算内容: {calc} - 验证结果: {result}")

                    # print(f"第 {idx} 题计算内容: {calc} - 验证结果: {result}")  # 输出验证结果
        total_count += valid_count
        total_score += cal_score
        # print(f"第 {idx} 题的有效计算个数是：{valid_count}")
        # print(f"第 {idx} 题的计算得分是：{cal_score}")
        # if valid_count != 0:
            # print(f"第 {idx} 题的计算正确率是：{cal_score/valid_count*100:.2f}%")
    #     print('-' * 50)  # 分隔线
    # print(f"计算题总数 = {total_count}, 计算题总得分 = {total_score}, 计算题总正确率 = {total_score/total_count*100:.2f}%")

    return total_count, total_score

# calculation_eval(r"D:\PythonProjects\eval\Astro_Cal_Eval\eval_results\GPT\Astro_Cal_Eval_EN_GPT-4o-mini_NASA_3_9 -175.xlsx",4)