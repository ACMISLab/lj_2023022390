# from modelscope import snapshot_download
# target_dir = "D:\models"
# model_dir = snapshot_download('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',
#     cache_dir=target_dir
# )
import json
import os
from sentence_transformers import SentenceTransformer, util
import torch

class AstronomyKnowledgeEngine:
    def __init__(self, file_path):
        self.file_path = file_path
        # 加载高性能、支持中英文的轻量级向量模型
        # self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        # self.model = SentenceTransformer('BAAI/bge-small-zh-v1.5')
        model_path = r"D:\models\sentence-transformers\paraphrase-multilingual-MiniLM-L12-v2"
        self.model = SentenceTransformer(model_path)
        self.formulas = []
        self.load_formulas()

        # 预计算特征向量：结合公式名、分支、适用范围及变量描述，实现“超视距”匹配
        features = []
        for f in self.formulas:
            var_desc = " ".join([v['description'] for v in f['variables'].values()])
            feature_text = f"{f['formula_name']} {f['branch']} {f['applicable_scope']} {var_desc}"
            features.append(feature_text)

        self.embeddings = self.model.encode(features, convert_to_tensor=True)

    def load_formulas(self):
        """解析 JSONL 文件 """
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"未找到公式库文件: {self.file_path}")
        with open(self.file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    self.formulas.append(json.loads(line))

    # def match_formula(self, query, top_k=1):
    #     """执行语义检索"""
    #     query_embedding = self.model.encode(query, convert_to_tensor=True)
    #     cos_scores = util.cos_sim(query_embedding, self.embeddings)[0]
    #
    #     best_idx = cos_scores.argmax().item()
    #     confidence = cos_scores[best_idx].item()
    #
    #     if confidence < 0.3:  # 语义相关性阈值
    #         return None, confidence
    #
    #     return self.formulas[best_idx], confidence
        # formula_retrieval.py (仅修改 match_formula 部分)

    # def match_formula(self, query, top_k, threshold):
    #     """
    #     执行语义检索
    #     :param threshold: 相似度阈值 (建议降低到 0.25 以适应短查询)
    #     """
    #     query_embedding = self.model.encode(query, convert_to_tensor=True)
    #     cos_scores = util.cos_sim(query_embedding, self.embeddings)[0]
    #
    #     # 获取前 k 个最高分
    #     top_results = torch.topk(cos_scores, k=top_k)
    #
    #     results = []
    #     for score, idx in zip(top_results.values, top_results.indices):
    #         if score.item() > threshold:
    #             results.append(self.formulas[idx.item()])
    #
    #     return results

    def match_formula(self, query, top_k=1, threshold=0.25):
        """
        执行混合检索：关键词强匹配 + 语义向量检索
        """
        results = []
        seen_names = set()

        # --- 策略 A: 关键词强匹配 (Keyword Hard Match) ---
        # 针对专有名词（如 "Stefan-Boltzmann"），只要公式名包含它，优先召回
        query_lower = query.lower()
        for f in self.formulas:
            # 检查公式名是否包含查询词 (支持中英文)
            # 例如 query="Stefan-Boltzmann", f_name="Stefan-Boltzmann Law (斯特藩-玻尔兹曼定律)"
            if query_lower in f['formula_name'].lower():
                results.append(f)
                seen_names.add(f['formula_name'])
                print(f"   🎯 [Keyword Match] 强匹配命中: {f['formula_name']}")

        # 如果强匹配已经找到了足够的结果，可以提前返回，或者继续补充
        # 这里我们选择继续补充，防止漏掉语义相关的

        # --- 策略 B: 语义向量检索 (Semantic Vector Search) ---
        query_embedding = self.model.encode(query, convert_to_tensor=True)
        cos_scores = util.cos_sim(query_embedding, self.embeddings)[0]

        # 获取前 k + 2 个最高分 (多取一点，防止被去重过滤光了)
        top_results = torch.topk(cos_scores, k=top_k + 2)

        for score, idx in zip(top_results.values, top_results.indices):
            f_data = self.formulas[idx.item()]
            f_name = f_data['formula_name']

            # 1. 过滤掉已经通过关键词匹配到的
            if f_name in seen_names:
                continue

            # 2. 阈值过滤
            if score.item() > threshold:
                results.append(f_data)
                seen_names.add(f_name)

        # 返回前 top_k 个结果
        return results[:top_k]

    # def generate_instruction(self, formula_data):
    #     """
    #     利用变量元数据构建阶段一的‘强约束提示词’
    #     """
    #     vars_info = formula_data['variables']
    #     constraints = formula_data.get('constraints', [])
    #
    #     # 自动生成变量单位表
    #     unit_table = "\n".join([
    #         f"- {v_name}: {v_data['description']} (Unit: {v_data['unit']})"
    #         for v_name, v_data in vars_info.items()
    #     ])
    #
    #     instruction = (
    #         f"Detected core formula: {formula_data['formula_name']}\n"
    #         f"Standard LaTeX formula: $${formula_data['latex']}$$\n\n"
    #         f"The derivation must satisfy the following dimensional constraints:\n{unit_table}\n\n"
    #         f"constants: {', '.join(formula_data['constants'])}\n"
    #         f"Applicable domain: {formula_data['applicable_scope']}\n"
    #         f"Calculation requirement: Unit pre-conversion must be performed, and dimensional closure must be verified after each computational step."
    #     )
    #     # instruction = (
    #     #     f"检测到核心规律:  {formula_data['formula_name']}\n"
    #     #     f"标准 LaTeX 公式: $${formula_data['latex']}$$\n\n"
    #     #     f"推导必须满足以下量纲约束:\n{unit_table}\n\n"
    #     #     f"物理常数参考:  {', '.join(formula_data['constants'])}\n"
    #     #     f"适用边界:  {formula_data['applicable_scope']}\n"
    #     #     f"计算要求: 必须执行单位预转换，并在每步计算后标注量纲闭合性。"
    #     # )
    #     return instruction

    def generate_instruction(self, formula_data):
        """
        利用变量元数据构建 PoT (Program of Thought) 提示词
        """
        vars_info = formula_data['variables']

        # 生成 Python 变量定义提示
        python_mapping = []
        for v_name, v_data in vars_info.items():
            # 尝试映射 latex 符号到 python 变量名 (简单处理: 去掉特殊字符)
            py_name = v_name.replace('\\', '').replace('{', '').replace('}', '')
            unit_str = v_data['unit']
            # 这里做一个简单的单位映射提示，实际项目中可以建一个映射字典
            python_mapping.append(f"# {v_name}: {v_data['description']} (Target Unit: {unit_str})")

        instruction = (
                f"Reference Formula: {formula_data['formula_name']}\n"
                f"Math Formula: $${formula_data['latex']}$$\n"
                f"Variables info:\n" + "\n".join(python_mapping) + "\n"
                f"Constants used: {', '.join(formula_data['constants'])}\n"
        )
        return instruction
    
# # --- 实例化并运行 ---
# FILE_PATH = r"D:\PythonProjects\AstroCalcBoost\main\AstroCalcBoost\formula\astronomy_formulas_processed.jsonl"
# engine = AstronomyKnowledgeEngine(FILE_PATH)
# #
# # # 测试匹配
# # test_query = r"已知地球质量 $5.97 \times 10^{24}$ kg，求距离 38 万千米的引力"
# test_query = r"Known Earth mass $5.97 \times 10^{24}$ kg, find the gravitational force at a distance of 380,000 km."
# matched_formula, score = engine.match_formula(test_query)
# #
# if matched_formula:
#     print(f"匹配置信度: {score:.4f}")
#     print(engine.generate_instruction(matched_formula))
