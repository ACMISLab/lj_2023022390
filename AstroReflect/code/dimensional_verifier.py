import sympy
from processor import latex_to_python


class DimensionalVerifier:
    def __init__(self):
        # 定义基础量纲
        self.L, self.M, self.T = sympy.symbols('L M T', real=True, positive=True)
        # 物理量纲映射表
        self.DIM_REGISTRY = {
            # 能量类 (M * L^2 / T^2)
            'E': self.M * self.L ** 2 / self.T ** 2,
            'U': self.M * self.L ** 2 / self.T ** 2,
            'V': self.M * self.L ** 2 / self.T ** 2,
            'Ek': self.M * self.L ** 2 / self.T ** 2,
            'Ep': self.M * self.L ** 2 / self.T ** 2,

            # 长度类 (L)
            'r': self.L, 'R': self.L, 'd': self.L, 'h': self.L, 's': self.L, 'x': self.L,

            # 速度类 (L / T)
            'v': self.L / self.T, 'u': self.L / self.T, 've': self.L / self.T, 'v0': self.L / self.T,

            # 常量
            'G': self.L ** 3 / (self.M * self.T ** 2),
            'M': self.M, 'm': self.M, 'g': self.L / self.T ** 2,
            'pi': 1, 'sqrt': lambda x: x ** 0.5
        }

    def check_consistency(self, latex_eq):
        """执行量纲校验"""
        print(f"[DEBUG] 转换前内容: {latex_eq}\n")
        py_eq = latex_to_python(latex_eq)
        print(f"[DEBUG] 转换后内容: {py_eq}")
        if '=' not in py_eq:
            return False, "No equation found after conversion"  # 错误用例这里应该返回 False

        try:
            py_eq = latex_to_python(latex_eq)
            if '=' not in py_eq: return True, "Numerical"
            lhs_str, rhs_str = py_eq.split('=')

            # 获取左侧符号
            lhs_syms = sympy.parse_expr(lhs_str).atoms(sympy.Symbol)

            for s in lhs_syms:
                if str(s) not in self.DIM_REGISTRY:
                    print(f"⚠️ 发现未注册符号 '{s}'，自动跳过量纲检查。")
                    return True, f"Unregistered symbol {s} skipped"
            lhs_str, rhs_str = py_eq.split('=')
            # 使用 local_dict 让 sympy 识别物理变量
            lhs_dim = sympy.simplify(sympy.parse_expr(lhs_str.strip(), local_dict=self.DIM_REGISTRY))
            rhs_dim = sympy.simplify(sympy.parse_expr(rhs_str.strip(), local_dict=self.DIM_REGISTRY))

            # 过滤纯数值步骤
            if lhs_dim.is_number or rhs_dim.is_number:
                return True, "Numerical step"

            if lhs_dim == rhs_dim:
                return True, f"Valid ({lhs_dim})"
            else:
                return False, f"Dimension Error: {lhs_dim} vs {rhs_dim}"
        except Exception as e:
            return False, f"Syntax Error: {str(e)}"