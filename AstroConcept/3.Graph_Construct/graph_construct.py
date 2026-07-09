# import pandas as pd
# import numpy as np
# from collections import defaultdict
# from math import log
#
# # 定义一个小常数ε
# epsilon = 1e-5
#
# # 读取 Excel 文件
# file_path = r'D:\PythonProjects\AstroCalcBoost\main\KnowledgeGraph\data\NASA知识图谱_主题知识点分离.xlsx'  # Excel 文件路径
# data = pd.read_excel(file_path)
#
# # 创建一个字典来存储共现计数
# co_occurrence_counts = defaultdict(int)
#
# # 提取所有唯一主题和知识点
# all_topics = set()
# all_knowledge_points = set()
#
# # 迭代每一行数据
# for index, row in data.iterrows():
#     topics = [row[f'topic_{i}'] for i in range(1, 7) if pd.notna(row[f'topic_{i}'])]
#     knowledge_points = [row[f'knowledge_point_{i}'] for i in range(1, 6) if pd.notna(row[f'knowledge_point_{i}'])]
#
#     all_topics.update(topics)
#     all_knowledge_points.update(knowledge_points)
#
#     # 更新主题之间的共现计数
#     for i in range(len(topics)):
#         for j in range(i + 1, len(topics)):
#             co_occurrence_counts[(topics[i], topics[j])] += 1
#
#     # 更新主题和知识点之间的共现计数
#     for topic in topics:
#         for kp in knowledge_points:
#             co_occurrence_counts[(topic, kp)] += 1
#
#     # 更新知识点之间的共现计数
#     for i in range(len(knowledge_points)):
#         for j in range(i + 1, len(knowledge_points)):
#             co_occurrence_counts[(knowledge_points[i], knowledge_points[j])] += 1
#
# # 将边和权重保存到列表
# edges = []
# unknown_edges = []  # 用于存储未知类型的边
# for (u, v), count in co_occurrence_counts.items():
#     if count > 0:  # 只添加有共现的边
#         # weight = log(count + epsilon)
#         weight = log(count)
#
#         # 确定边的类型
#         if u in all_topics and v in all_topics:
#             edge_type = 'Topic to Topic'
#         elif u in all_topics and v in all_knowledge_points:
#             edge_type = 'Topic to Knowledge Point'
#         elif u in all_knowledge_points and v in all_knowledge_points:
#             edge_type = 'Knowledge Point to Knowledge Point'
#         else:
#             edge_type = '未知边类型'  # 记录未知类型
#             unknown_edges.append((u, v))  # 存储未知边
#
#         # 只添加权重不等于 1.00E-05 的边
#         if weight != 0:
#             edges.append((edge_type, u, v, weight))
#
# # 打印未知边的信息
# if unknown_edges:
#     print("Unknown edges:")
#     for u, v in unknown_edges:
#         print(f"Unknown Edge: ({u}, {v})")
#
# # 打印边和权重
# if edges:
#     for edge_type, u, v, weight in edges:
#         print(f"Edge Type: {edge_type}, Edge: ({u}, {v}), Weight: {weight}")
# else:
#     print("No edges found.")
#
# # 创建带有 ID 的边 DataFrame
# edges_with_id = pd.DataFrame(edges, columns=['Edge Type', 'Source', 'Target', 'Weight'])
# edges_with_id.insert(0, 'ID', range(1, len(edges_with_id) + 1))  # 添加 ID 列
#
# # 保存边到 CSV 文件（适用于 Neo4j 导入）
# edges_with_id.to_csv('edges_with_id_without_1E-05.csv', index=False)
#
# print("Edges with ID saved to edges_with_id.csv.")

#############################################################
#   添加节点类型
#############################################################

import pandas as pd
import numpy as np
from collections import defaultdict
from math import log

# 定义一个小常数ε
epsilon = 1e-5

# 读取 Excel 文件
file_path = r'D:\PythonProjects\AstroCalcBoost\main\KnowledgeGraph\data\BasicAstronomy_Topic_KP主题知识点分离.xlsx'  # Excel 文件路径
data = pd.read_excel(file_path)

# 创建一个字典来存储共现计数
co_occurrence_counts = defaultdict(int)

# 提取所有唯一主题和知识点
all_topics = set()
all_knowledge_points = set()

# 迭代每一行数据
for index, row in data.iterrows():
    topics = [row[f'topic_{i}'] for i in range(1, 2) if pd.notna(row[f'topic_{i}'])]
    knowledge_points = [row[f'knowledge_point_{i}'] for i in range(1, 6) if pd.notna(row[f'knowledge_point_{i}'])]

    all_topics.update(topics)
    all_knowledge_points.update(knowledge_points)

    # 更新主题之间的共现计数
    for i in range(len(topics)):
        for j in range(i + 1, len(topics)):
            co_occurrence_counts[(topics[i], topics[j])] += 1

    # 更新主题和知识点之间的共现计数
    for topic in topics:
        for kp in knowledge_points:
            co_occurrence_counts[(topic, kp)] += 1

    # 更新知识点之间的共现计数
    for i in range(len(knowledge_points)):
        for j in range(i + 1, len(knowledge_points)):
            co_occurrence_counts[(knowledge_points[i], knowledge_points[j])] += 1

# 将边和权重保存到列表
edges = []
unknown_edges = []  # 用于存储未知类型的边
for (u, v), count in co_occurrence_counts.items():
    if count > 0:  # 只添加有共现的边
        # weight = log(count + epsilon)
        weight = log(count)

        # 确定边的类型
        if u in all_topics and v in all_topics:
            edge_type = 'Topic to Topic'
            u_type = 'Topic'
            v_type = 'Topic'
        elif u in all_topics and v in all_knowledge_points:
            edge_type = 'Topic to Knowledge Point'
            u_type = 'Topic'
            v_type = 'Knowledge Point'
        elif u in all_knowledge_points and v in all_knowledge_points:
            edge_type = 'Knowledge Point to Knowledge Point'
            u_type = 'Knowledge Point'
            v_type = 'Knowledge Point'
        else:
            edge_type = '未知边类型'  # 记录未知类型
            unknown_edges.append((u, v))  # 存储未知边
            u_type = '未知'
            v_type = '未知'

        # 只添加权重不等于 1.00E-05 的边
        if weight != 0:
            edges.append((edge_type, u, v, weight, u_type, v_type))

# 打印未知边的信息
if unknown_edges:
    print("Unknown edges:")
    for u, v in unknown_edges:
        print(f"Unknown Edge: ({u}, {v})")

# 打印边和权重
if edges:
    for edge_type, u, v, weight, u_type, v_type in edges:
        print(f"Edge Type: {edge_type}, Edge: ({u}, {v}), Weight: {weight}, Node Types: ({u_type}, {v_type})")
else:
    print("No edges found.")

# 创建带有 ID 的边 DataFrame
edges_with_id = pd.DataFrame(edges, columns=['Edge Type', 'Source', 'Target', 'Weight', 'Source Node Type', 'Target Node Type'])
edges_with_id.insert(0, 'ID', range(1, len(edges_with_id) + 1))  # 添加 ID 列

# 保存边到 CSV 文件（适用于 Neo4j 导入）
edges_with_id.to_csv('D:\PythonProjects\AstroCalcBoost\main\KnowledgeGraph\BasicA_edges_with_id_without_1E-05.csv', index=False)

print("Edges with ID saved to edges_with_id_without_1E-05_2.csv.")