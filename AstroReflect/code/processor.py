import re


def _remove_text_units(string):
    # 处理 \text{...} 及其可能带有的指数单位
    modified_string = re.sub(r'\^?\\text\{.*?\}(\s*\^\d+)?\s*', '', string)
    return modified_string


def _remove_mtext_units(string):
    # 处理 \mathrm{...} 单位
    return re.sub(r'\\mathrm\{.*?\}', '', string)


def _convert_scientific_notation(string):
    # 将 1.5 \times 10^{24} 转换为 Python 数值字符串
    return re.sub(r'(\d*\.?\d+)\\times 10\^{(\d+)}',
                  lambda match: str(float(match.group(1)) * (10 ** int(match.group(2)))),
                  string)


def _remove_inequality_left(string):
    # 仅针对不等式符号进行处理，保留等号 '='
    return re.sub(r'.*?(\s*[<>]|\\geq|\\leq|\\neq)\s*', '', string)


def latex_to_python(expr):
    """实现 LaTeX 到 Python 表达式的转换"""
    # 1. 基础预处理
    expr = expr.replace('\\approx', '=')

    # 2. 清洗单位和科学计数法（保留等号）
    expr = _remove_text_units(expr)
    expr = _remove_mtext_units(expr)
    expr = _convert_scientific_notation(expr)

    # 3. 处理括号和符号
    expr = expr.replace("\\left", "(").replace("\\right", ")")
    expr = expr.replace('\\times', '*').replace('\\cdot', '*')
    expr = expr.replace("^{\\circ}", "").replace("^\\circ", "").replace("'", "").strip()

    # 4. 处理分数和幂运算（先处理分数，防止干扰）
    expr = re.sub(r'\\frac{(.*?)}{(.*?)}', r'((\1)/(\2))', expr)
    expr = re.sub(r'\^{(.*?)}', r'**(\1)', expr)
    expr = expr.replace('^', '**')

    # 5. 清理残留的反斜杠指令 (如 \sqrt, \alpha 等，保留字母)
    # 我们希望 \sqrt{x} 变成 sqrt(x)，而不是被删掉
    expr = expr.replace('\\sqrt', 'sqrt')
    expr = re.sub(r'\\([a-zA-Z]+)', r'\1', expr)

    # 6. 最终清理
    expr = expr.replace('{', '(').replace('}', ')')
    expr = re.sub(r'\s+', ' ', expr).strip()
    expr = expr.replace(',', '')
    expr = expr.replace(r'\,', '').replace(r'\ ', '')
    expr = expr.replace('\\', '')  #

    return expr.replace(' ', '')


def extract_calculations_with_equals(text):
    """从文本中提取所有包含等号的 LaTeX 公式"""
    steps_section = re.search(r'(.*)', text, re.DOTALL)
    if not steps_section: return []

    steps_content = steps_section.group(1)
    # 提取多种包裹格式
    patterns = [r'\\\((.*?)\\\)', r'\\\[(.*?)\\\]', r'\$(.*?)\$', r'\$\$(.*?)\$\$']
    calculations = []
    for p in patterns:
        found = re.findall(p, steps_content, re.DOTALL if ']' in p else 0)
        calculations.extend(found)

    calculations_with_equals = []
    for calc in calculations:
        # 在提取阶段不做过多清洗，只做符号统一
        clean_calc = calc.replace('\\approx', '=')
        if '=' in clean_calc:
            # 确保提取完整的等式结构
            calculations_with_equals.append(clean_calc.strip())

    return calculations_with_equals