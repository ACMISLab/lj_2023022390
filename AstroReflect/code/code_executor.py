import numpy as np
import math
import astropy.units as u
import astropy.constants as const
import io
import sys
import traceback
import threading
import _thread
from contextlib import contextmanager

# ==========================================
# 超时控制上下文管理器
# ==========================================
class ExecutionTimeoutError(Exception):
    """自定义代码执行超时异常"""
    pass

@contextmanager
def time_limit(seconds):
    """
    如果代码执行时间超过 seconds 秒，将强行向主线程抛出 KeyboardInterrupt。
    用于打断 while True 等死循环。
    """
    def timeout_handler():
        _thread.interrupt_main()

    timer = threading.Timer(seconds, timeout_handler)
    timer.start()
    try:
        yield
    except KeyboardInterrupt:
        raise ExecutionTimeoutError(f"⏳ 代码执行超时（限制 {seconds} 秒），已被系统强制终止！请检查代码是否包含死循环或极低效计算。")
    finally:
        timer.cancel()


# ==========================================
# 方案二
# ==========================================
class AstroCodeExecutor:
    def __init__(self):
        # 预设的执行环境，包含常用的天文库
        self.globals = {
            "u": u,
            "const": const,
            "np": np,
            "math": math,
            "sqrt": np.sqrt,
            "print": print
        }

    def execute(self, code_str, timeout_seconds=10):
        """
        执行模型生成的 Python 代码，并捕获输出和错误。
        新增参数 timeout_seconds: 默认 10 秒超时
        返回: (success: bool, output: str, feedback: str)
        """
        # 捕获标准输出
        old_stdout = sys.stdout
        redirected_output = sys.stdout = io.StringIO()

        local_scope = {}

        try:
            # 1. 尝试执行代码（加入 10 秒超时限制）
            with time_limit(timeout_seconds):
                exec(code_str, self.globals, local_scope)

            # 2. 获取打印的输出
            sys.stdout = old_stdout
            stdout_str = redirected_output.getvalue().strip()

            return True, stdout_str, "Execution Successful"

        except ExecutionTimeoutError as timeout_err:
            # 单独捕获超时异常
            sys.stdout = old_stdout
            return False, "", str(timeout_err)

        except Exception as e:
            sys.stdout = old_stdout
            # 获取详细的报错堆栈
            error_msg = traceback.format_exc()

            # 4. 精简报错信息反馈给模型
            feedback = self._format_error_feedback(e, error_msg)
            return False, "", feedback

    def _format_error_feedback(self, error, full_traceback):
        """
        将 Python 报错翻译为模型能理解的物理/逻辑反馈
        """
        error_type = type(error).__name__

        if isinstance(error, u.UnitConversionError):
            return f"物理量纲错误 (UnitConversionError): {str(error)}。请检查你的公式，确保等式两边的单位在物理上是齐次的。"

        if isinstance(error, ZeroDivisionError):
            return "数学错误: 除数为零。请检查分母中的变量是否为零。"

        if isinstance(error, NameError):
            return f"变量未定义 ({str(error)})。请确保所有使用的物理常数或变量都已正确导入或定义（例如使用 const.G）。"

        if isinstance(error, SyntaxError):
            return f"代码语法错误。请检查 Python 语法。\n{full_traceback.splitlines()[-1]}"

        # 默认返回最后一行报错
        return f"运行时错误 ({error_type}): {str(error)}"

    def validate_physical_bounds(self, result_value, target_quantity_type):
        """
        (可选) 阶段三：物理边界检查
        例如：如果是速度，不能 > c
        """
        pass


# ==========================================
# 方案三
# ==========================================
class PythonSession:
    def __init__(self):
        # 1. 初始化沙盒环境 (合并了方案二的常用库支持)
        self.globals = {
            "u": u,
            "const": const,
            "np": np,
            "math": math,
            "sqrt": np.sqrt,
            "print": print,
            "abs": abs,
            "min": min,
            "max": max,
            "pow": pow,
        }
        # 用于存储最后一次执行的输出
        self.last_output = ""

    def _format_error_feedback(self, error, full_traceback):
        """
        【移植自方案二】将 Python 报错翻译为模型能理解的物理/逻辑反馈
        """
        error_type = type(error).__name__

        if isinstance(error, u.UnitConversionError):
            return f"物理量纲错误 (UnitConversionError): {str(error)}。请检查你的公式，确保等式两边的单位在物理上是齐次的 (例如不要将米和秒直接相加)。"

        if isinstance(error, ZeroDivisionError):
            return "数学错误: 除数为零。请检查分母中的变量是否为零。"

        if isinstance(error, NameError):
            return f"变量未定义 ({str(error)})。请确保该变量在之前的代码块中已正确定义，或者检查拼写。"

        if isinstance(error, SyntaxError):
            return f"代码语法错误。请检查 Python 语法 (例如漏了括号或冒号)。\n错误位置: {full_traceback.splitlines()[-1]}"

        if isinstance(error, TypeError):
            return f"类型错误 ({str(error)})。提示: astropy Quantity 对象不能直接与普通数字混合运算，请使用 `.value` 提取数值或给数字赋予单位。"

        return f"运行时错误 ({error_type}): {str(error)}"

    def execute(self, code_snippet, timeout_seconds=10):
        """
        执行代码片段，并保持变量状态 (方案三核心逻辑)
        新增参数 timeout_seconds: 默认 10 秒超时
        """
        # 捕获标准输出
        capture = io.StringIO()
        original_stdout = sys.stdout
        sys.stdout = capture

        try:
            # 【核心改进】加上超时时间限制
            with time_limit(timeout_seconds):
                # 使用 self.globals 作为全局作用域执行，确保变量状态在多轮对话中持久化
                exec(code_snippet, self.globals)

            sys.stdout = original_stdout
            output = capture.getvalue().strip()
            self.last_output = output

            # 成功执行
            return True, output, "Execution Success"

        except ExecutionTimeoutError as timeout_err:
            # 捕获我们的自定义超时异常
            sys.stdout = original_stdout
            return False, "", str(timeout_err)

        except Exception as e:
            sys.stdout = original_stdout
            # 获取详细堆栈
            error_msg = traceback.format_exc()

            # 【改进】使用移植过来的物理反馈机制，而不是简单返回报错
            feedback = self._format_error_feedback(e, error_msg)

            return False, "", feedback