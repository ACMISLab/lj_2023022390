# import pandas as pd
# import random
# import numpy as np
# import networkx as nx
#
#
# def load_graph_from_csv(file_path):
#     """从CSV文件加载知识图谱到图中"""
#     # 使用pandas读取CSV文件
#     data = pd.read_csv(file_path)
#
#     # 创建一个无向图
#     G = nx.Graph()
#
#     # 添加边和权重到图中
#     for index, row in data.iterrows():
#         source = row['Source']
#         target = row['Target']
#         edge_type = row['Edge Type']
#         weight = row['Weight']
#
#         # 添加边，假设相同的源和目标可以有多个边
#         G.add_edge(source, target, weight=weight, edge_type=edge_type)
#
#     return G
#
#
# def fco(u, v, graph):
#     """示例函数，用于计算u与v之间的相似度"""
#     return graph[u][v]['weight'] if graph.has_edge(u, v) else 0
#
#
# def random_walk(graph, start_node, steps):
#     """在图中进行随机游走"""
#     current_node = start_node
#     walk_sequence = [current_node]  # 记录游走的节点
#     for _ in range(steps):
#         neighbors = list(graph.neighbors(current_node))
#         if not neighbors:
#             break  # 如果没有邻居，停止游走
#         # 计算概率分布
#         probs = [np.exp(fco(current_node, neighbor, graph)) for neighbor in neighbors]
#         probs_sum = sum(probs)
#         probs = [p / probs_sum for p in probs]  # 归一化概率
#         current_node = random.choices(neighbors, weights=probs)[0]  # 随机选择下一个节点
#         walk_sequence.append(current_node)  # 记录游走路径
#     return walk_sequence
#
#
# def sample_topics_and_kps(graph):
#     """从图中遍历所有主题并记录游走结果"""
#     topics = [node for node in graph.nodes() if 'KP' not in node]  # 假设KPs以'KP'开头
#     results = []  # 用于存储每个主题的游走结果
#     for start_topic in topics:  # 遍历所有主题
#         walk_results = random_walk(graph, start_topic, 3)  # 进行3步随机游走
#         results.append((start_topic, walk_results))  # 保存主题及其游走路径
#     return results
#
#
# # 主程序
# file_path = 'D:\\PythonProjects\\AstroCalcBoost\\main\\KnowledgeGraph\\edges_with_id_without_1E-05.csv'  # 替换为您的CSV文件路径
# G = load_graph_from_csv(file_path)  # 从CSV加载图
# walk_results = sample_topics_and_kps(G)  # 遍历所有主题
#
# # 输出采样结果
# for start_topic, walk_sequence in walk_results:
#     print(f"Starting Topic: {start_topic}, Walk Result: {walk_sequence}")
#
# # 输出遍历的主题总数
# total_topics = len(walk_results)
# print(f"Total number of topics traversed: {total_topics}")
#
#
# # 输出所有节点的数量
# total_nodes = len(G.nodes())
# print(f"Total number of nodes in the graph: {total_nodes}")

##########################################################################################################################
#   添加节点类型
##########################################################################################################################

# import pandas as pd
# import random
# import numpy as np
# import networkx as nx
#
# def load_graph_from_csv(file_path):
#     """从CSV文件加载知识图谱到图中"""
#     # 使用pandas读取CSV文件
#     data = pd.read_csv(file_path)
#
#     # 创建一个无向图
#     G = nx.Graph()
#
#     # 添加边和权重到图中
#     for index, row in data.iterrows():
#         source = row['Source']
#         target = row['Target']
#         edge_type = row['Edge Type']
#         weight = row['Weight']
#
#         # 添加边，假设相同的源和目标可以有多个边
#         G.add_edge(source, target, weight=weight, edge_type=edge_type)
#
#         # 为源节点和目标节点添加标签（节点类型）
#         G.nodes[source]['type'] = row['Source Node Type']
#         G.nodes[target]['type'] = row['Target Node Type']
#
#     return G
#
# def fco(u, v, graph):
#     """示例函数，用于计算u与v之间的相似度"""
#     return graph[u][v]['weight'] if graph.has_edge(u, v) else 0
#
# def random_walk(graph, start_node, steps):
#     """在图中进行随机游走"""
#     current_node = start_node
#     walk_sequence = [current_node]  # 记录游走的节点
#     for _ in range(steps):
#         neighbors = list(graph.neighbors(current_node))
#         if not neighbors:
#             break  # 如果没有邻居，停止游走
#         # 计算概率分布
#         probs = [np.exp(fco(current_node, neighbor, graph)) for neighbor in neighbors]
#         probs_sum = sum(probs)
#         probs = [p / probs_sum for p in probs]  # 归一化概率
#         current_node = random.choices(neighbors, weights=probs)[0]  # 随机选择下一个节点
#         walk_sequence.append(current_node)  # 记录游走路径
#     return walk_sequence
#
# def sample_topics_and_kps(graph):
#     """从图中遍历所有主题并记录游走结果"""
#     # 假设KPs以'KP'开头，假设主题不以'KP'开头
#     topics = [node for node in graph.nodes() if graph.nodes[node]['type'] == 'Topic']
#     results = []  # 用于存储每个主题的游走结果
#
#     for start_topic in topics:  # 遍历所有主题
#         for _ in range(1):  # 对每个主题进行三次游走
#             for steps in range(3, 11):  # 随机游走步数从3到10
#                 walk_results = random_walk(graph, start_topic, steps)  # 进行随机游走
#                 results.append((start_topic, steps, walk_results))  # 保存主题、步数及其游走路径
#
#     return results
#
# # 主程序
# file_path = 'D:\\PythonProjects\\AstroCalcBoost\\main\\KnowledgeGraph\\edges_with_id_without_1E-05_with_nodetype.csv'  # 替换为您的CSV文件路径
# G = load_graph_from_csv(file_path)  # 从CSV加载图
# walk_results = sample_topics_and_kps(G)  # 遍历所有主题
#
# # 输出采样结果
# for start_topic, steps, walk_sequence in walk_results:
#     print(f"Starting Topic: {start_topic}, Steps: {steps}, Walk Result: {walk_sequence}")
#
# # 输出遍历的主题总数
# total_topics = len(walk_results)
# print(f"Total number of topics traversed: {total_topics}")
#
# # 输出所有节点的数量
# total_nodes = len(G.nodes())
# print(f"Total number of nodes in the graph: {total_nodes}")

##############################################################################################################################
#   按照步数保存到csv文件
##############################################################################################################################
import pandas as pd
import random
import numpy as np
import networkx as nx
import csv


def load_graph_from_csv(file_path):
    """从CSV文件加载知识图谱到图中"""
    data = pd.read_csv(file_path)
    G = nx.Graph()

    # 添加边和权重到图中
    for index, row in data.iterrows():
        source = row['Source']
        target = row['Target']
        edge_type = row['Edge Type']
        weight = row['Weight']
        G.add_edge(source, target, weight=weight, edge_type=edge_type)
        G.nodes[source]['type'] = row['Source Node Type']
        G.nodes[target]['type'] = row['Target Node Type']

    return G


def fco(u, v, graph):
    """示例函数，用于计算u与v之间的相似度"""
    return graph[u][v]['weight'] if graph.has_edge(u, v) else 0


def random_walk(graph, start_node, steps):
    """在图中进行随机游走"""
    current_node = start_node
    walk_sequence = [current_node]  # 记录游走的节点
    for _ in range(steps):
        neighbors = list(graph.neighbors(current_node))
        if not neighbors:
            break  # 如果没有邻居，停止游走
        # 计算概率分布
        probs = [np.exp(fco(current_node, neighbor, graph)) for neighbor in neighbors]
        probs_sum = sum(probs)
        probs = [p / probs_sum for p in probs]  # 归一化概率
        current_node = random.choices(neighbors, weights=probs)[0]  # 随机选择下一个节点
        walk_sequence.append(current_node)  # 记录游走路径
    return walk_sequence


def sample_topics_and_kps(graph):
    """从图中遍历所有主题并记录游走结果"""
    topics = [node for node in graph.nodes() if graph.nodes[node]['type'] == 'Topic']
    results = []  # 用于存储每个主题的游走结果

    for start_topic in topics:  # 遍历所有主题
        for _ in range(1):  # 对每个主题进行一次游走
            for steps in range(3, 11):  # 随机游走步数从3到10
                walk_results = random_walk(graph, start_topic, steps)  # 进行随机游走
                results.append((start_topic, steps, walk_results))  # 保存主题、步数及其游走路径

    return results


# 主程序
file_path = 'D:\\PythonProjects\\AstroCalcBoost\\main\\KnowledgeGraph\\edges_with_id_without_1E-05_with_nodetype.csv'  # 替换为您的CSV文件路径
G = load_graph_from_csv(file_path)  # 从CSV加载图
walk_results = sample_topics_and_kps(G)  # 遍历所有主题

# 将游走结果按步数分开存储到不同的CSV文件中
for _, steps, walk_sequence in walk_results:
    # 设定文件名，保留步数
    file_name = f'walk_result_steps_{steps}.csv'

    # 以追加模式打开CSV文件，写入游走结果
    with open(file_name, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(walk_sequence)  # 写入游走结果，每个结果占一行

# 输出采样结果
for start_topic, steps, walk_sequence in walk_results:
    print(f"Starting Topic: {start_topic}, Steps: {steps}, Walk Result: {walk_sequence}")

# 输出遍历的主题总数
total_topics = len(walk_results)
print(f"Total number of topics traversed: {total_topics}")

# 输出所有节点的数量
total_nodes = len(G.nodes())
print(f"Total number of nodes in the graph: {total_nodes}")