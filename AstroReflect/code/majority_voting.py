import re
# import pandas as pd
from typing import List, Dict, Any
from collections import Counter


def _fix_fracs(string):
    substrs = string.split("\\frac")
    new_str = substrs[0]
    if len(substrs) > 1:
        substrs = substrs[1:]
        for substr in substrs:
            new_str += "\\frac"
            if substr[0] == "{":
                new_str += substr
            else:
                try:
                    assert len(substr) >= 2
                except:
                    return string
                a = substr[0]
                b = substr[1]
                if b != "{":
                    if len(substr) > 2:
                        post_substr = substr[2:]
                        new_str += "{" + a + "}{" + b + "}" + post_substr
                    else:
                        new_str += "{" + a + "}{" + b + "}"
                else:
                    if len(substr) > 2:
                        post_substr = substr[2:]
                        new_str += "{" + a + "}" + b + post_substr
                    else:
                        new_str += "{" + a + "}" + b
    string = new_str
    return string


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

    # 找到所有匹配的内容
    matches = re.findall(pattern, s)

    if matches:
        # 只返回最后一个匹配的内容
        return matches[-1]
    return s


def is_equiv(str1, str2, verbose=False, tolerance=1e-2):
    """比较两个字符串是否等价，支持数值比较"""
    if str1 is None and str2 is None:
        if verbose:
            print("WARNING: Both None")
        return True
    if str1 is None or str2 is None:
        return False

    try:
        # 尝试数值比较
        num1 = float(str1)
        num2 = float(str2)
        # 使用相对容差进行比较
        if abs(num1 - num2) <= tolerance * max(abs(num1), abs(num2)):
            return True
    except:
        pass

    try:
        ss1 = _strip_string(str1)
        ss2 = _strip_string(str2)
        if verbose:
            print(f"Stripped strings: '{ss1}' vs '{ss2}'")
        return ss1 == ss2
    except Exception as e:
        if verbose:
            print(f"Error in is_equiv: {e}")
        return str1 == str2


def extract_final_answer(content: str) -> str:
    """
    从响应内容中提取最终答案，返回规范化后的答案字符串
    """
    if not content:
        return ""

    # 首先尝试匹配 \boxed{...} 格式（最常见）
    boxed_pattern = r'\\boxed\{(.*(?:\{[^}]*\}[^}]*)*)\}'
    matches = re.findall(boxed_pattern, content, re.DOTALL)

    if matches:
        # 返回最后一个 \boxed 中的内容（可能有多个\boxed）
        answer = matches[-1].strip()
        # 移除可能的额外空白字符
        answer = re.sub(r'\s+', ' ', answer)
        return answer

    # 如果没有找到 \boxed，尝试匹配其他常见格式
    patterns = [
        r'Final\s*answer\s*[:：]\s*(.*?)(?:\n|$)',
        r'Answer\s*[:：]\s*(.*?)(?:\n|$)',
        r'最终答案\s*[:：]\s*(.*?)(?:\n|$)',
        r'答案\s*[:：]\s*(.*?)(?:\n|$)',
        r'结果为\s*[:：]\s*(.*?)(?:\n|$)',
        r'result\s*is\s*[:：]\s*(.*?)(?:\n|$)',
        r'is\s*[:：]\s*(.*?)(?:\n|$)'
    ]

    for pattern in patterns:
        matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
        if matches:
            answer = matches[0].strip()
            # 移除可能的额外空白字符
            answer = re.sub(r'\s+', ' ', answer)
            return answer

    # 如果没有找到明确的答案格式，返回空字符串
    return ""


def simplify_numeric_string(s: str) -> str:
    """简化数值字符串，提取数值部分"""
    if not s:
        return ""

    # 尝试提取数值部分
    # 匹配数字（包括小数和科学计数法）
    numeric_pattern = r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?'
    matches = re.findall(numeric_pattern, s)

    if matches:
        # 返回第一个数值
        return matches[0]

    return s


def get_majority_vote_answer(all_completions: List, verbose: bool = False) -> str:
    """
    从所有响应中通过投票选出最常见的答案

    Args:
        all_completions: 所有生成的响应列表
        verbose: 是否输出详细信息

    Returns:
        投票选出的答案
    """
    if not all_completions:
        return ""

    # 提取所有答案
    all_answers = []
    for i, completion in enumerate(all_completions):
        try:
            content = completion[0]["content"]
            answer = extract_final_answer(content)
            if answer:  # 只收集非空答案
                # 移除\boxed包装（如果还有的话）
                answer = remove_boxed(answer)
                # 提取数值部分
                simplified = simplify_numeric_string(answer)
                if simplified:
                    all_answers.append((simplified, answer, i))
                    if verbose:
                        print(f"Response {i}: extracted '{simplified}' from '{answer[:50]}...'")
                else:
                    if verbose:
                        print(f"Response {i}: No numeric answer found in '{answer[:50]}...'")
            else:
                if verbose:
                    print(f"Response {i}: No answer found")
        except Exception as e:
            if verbose:
                print(f"Response {i}: Error extracting answer: {e}")
            continue

    if not all_answers:
        print("No valid answers extracted from any response")
        return ""

    # 统计答案出现次数（使用简化的数值）
    answer_counter = Counter()
    answer_details = {}

    for simplified, original, idx in all_answers:
        answer_counter[simplified] += 1
        if simplified not in answer_details:
            answer_details[simplified] = []
        answer_details[simplified].append((original, idx))

    # 如果没有有效的答案，返回空字符串
    if not answer_counter:
        print("No valid numeric answers found after simplification")
        return ""

    # 找出出现次数最多的答案
    majority_answer, count = answer_counter.most_common(1)[0]

    print(f"\nVoting Results:")
    print(f"Total responses analyzed: {len(all_completions)}")
    print(f"Valid answers extracted: {len(all_answers)}")
    print(f"Most common answer: '{majority_answer}' (count: {count}/{len(all_answers)})")

    # 打印所有答案分布
    if verbose:
        print(f"Answer distribution:")
        for answer, count in answer_counter.most_common():
            details = answer_details[answer]
            indices = [idx for _, idx in details]
            print(f"  '{answer}': {count} responses (indices: {indices})")

    return majority_answer

def get_majority_vote_answer(all_completions: List, verbose: bool = False) -> str:
    """
    从所有响应中通过投票选出最常见的答案

    Args:
        all_completions: 所有生成的响应列表
        verbose: 是否输出详细信息

    Returns:
        投票选出的答案
    """
    if not all_completions:
        return ""

    # 提取所有答案
    all_answers = []
    for i, completion in enumerate(all_completions):
        try:
            content = completion[0]["content"]
            answer = extract_final_answer(content)
            if answer:  # 只收集非空答案
                # 移除\boxed包装（如果还有的话）
                answer = remove_boxed(answer)
                # 提取数值部分
                simplified = simplify_numeric_string(answer)
                if simplified:
                    all_answers.append((simplified, answer, i))
                    if verbose:
                        print(f"Response {i}: extracted '{simplified}' from '{answer[:50]}...'")
                else:
                    if verbose:
                        print(f"Response {i}: No numeric answer found in '{answer[:50]}...'")
            else:
                if verbose:
                    print(f"Response {i}: No answer found")
        except Exception as e:
            if verbose:
                print(f"Response {i}: Error extracting answer: {e}")
            continue

    if not all_answers:
        print("No valid answers extracted from any response")
        return ""

    # 统计答案出现次数（使用简化的数值）
    answer_counter = Counter()
    answer_details = {}

    for simplified, original, idx in all_answers:
        answer_counter[simplified] += 1
        if simplified not in answer_details:
            answer_details[simplified] = []
        answer_details[simplified].append((original, idx))

    # 如果没有有效的答案，返回空字符串
    if not answer_counter:
        print("No valid numeric answers found after simplification")
        return ""

    # 找出出现次数最多的答案
    majority_answer, count = answer_counter.most_common(1)[0]

    print(f"\nVoting Results:")
    print(f"Total responses analyzed: {len(all_completions)}")
    print(f"Valid answers extracted: {len(all_answers)}")
    print(f"Most common answer: '{majority_answer}' (count: {count}/{len(all_answers)})")

    # 打印所有答案分布
    if verbose:
        print(f"Answer distribution:")
        for answer, count in answer_counter.most_common():
            details = answer_details[answer]
            indices = [idx for _, idx in details]
            print(f"  '{answer}': {count} responses (indices: {indices})")

    return majority_answer


def correctness_reward_func(completions, **kwargs) -> List[float]:
    """
    通过投票机制计算正确性奖励分数

    Args:
        completions: 需要评分的响应列表，格式为 [[{"content": "response text"}]]
        **kwargs: 其他参数
            - verbose: 是否输出详细信息

    Returns:
        每个响应的正确性奖励分数列表（正确=1.0，错误=0.0）
    """
    rewards = []

    if not completions:
        print("Warning: No completions to score")
        return []

    # 通过投票选出参考答案（使用传入的所有响应）
    reference_answer = get_majority_vote_answer(completions, verbose=kwargs.get('verbose', False))

    if not reference_answer:
        print("Warning: Could not determine reference answer from voting, returning zero rewards")
        return [0.0] * len(completions)

    print(f"\nReference answer selected by voting: '{reference_answer}'")

    # 计算每个响应的奖励
    for idx, completion in enumerate(completions):
        try:
            content = completion[0]["content"]

            # 提取模型生成的最终答案
            predicted_answer = extract_final_answer(content)
            predicted_answer = remove_boxed(predicted_answer)

            # 简化预测答案
            simplified_predicted = simplify_numeric_string(predicted_answer)

            # 比较答案是否等价（使用更宽松的比较）
            is_correct = is_equiv(reference_answer, simplified_predicted,
                                  verbose=kwargs.get('verbose', False))

            # 计算奖励：正确得1分，错误得0分
            reward = 1.0 if is_correct else 0.0

            # 可选：输出详细信息用于调试
            verbose = kwargs.get('verbose', False)
            if verbose:
                print(f"\nCompletion {idx}:")
                print(f"  Reference (voted): '{reference_answer}'")
                print(f"  Predicted (raw): '{predicted_answer}'")
                print(f"  Predicted (simplified): '{simplified_predicted}'")
                print(f"  Is correct: {is_correct}")
                print(f"  Reward: {reward}")

            rewards.append(reward)

        except Exception as e:
            print(f"Error processing completion {idx}: {e}")
            rewards.append(0.0)  # 处理出错时给0分

    print(f"\nFinal Correctness Rewards List: {rewards}")
    return rewards



