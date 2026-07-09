import pandas as pd

# 读取 Excel 文件
# 假设第一个表格是 "table1.xlsx"，第二个表格是 "table2.xlsx"
df1 = pd.read_excel(r"D:\PythonProjects\AstroCalcBoost\main\AstroConcept\2.知识点提取\NASA知识图谱_主题知识点分离.xlsx")  # 第一个表格，包含ID、topic和knowledge_point
df2 = pd.read_excel(r"D:\PythonProjects\AstroCalcBoost\main\AstroConcept\4.概念组合\walk_result_steps_3~10\walk_result_steps_8.xlsx")  # 第二个表格，包含随机组合的topic和knowledge_point


# 数据清理函数：去除多余空格，填充空值为""
def clean_data(df):
    df = df.fillna("")  # 用空字符串填充NaN
    return df.applymap(lambda x: x.strip() if isinstance(x, str) else x)  # 去除字符串两边多余空格


# 清洗数据
df1 = clean_data(df1)
df2 = clean_data(df2)

# 存储已匹配的ID
matched_ids = set()


# 定义一个函数用于匹配来源，并打印匹配过程
def find_source(row, source_df):
    row_values = set(row.values)  # 获取当前行的所有值作为集合

    for _, source_row in source_df.iterrows():
        source_values = set(source_row[1:])  # 获取来源行的所有值（跳过ID）
        source_id = source_row["ID"]

        # 检查当前行的所有值是否在来源行的值中，并且该ID尚未匹配
        if row_values.issubset(source_values) and source_id not in matched_ids:
            print(f"Found match: Row {row.values} matches with source ID {source_row['ID']}")
            matched_ids.add(source_id)  # 添加到已匹配ID集合中
            return source_id  # 返回匹配的ID

    print(f"No match found for row: {row.values}")
    return None  # 如果未找到匹配来源，返回None


# 对第二个表格中的每一行，找到其来源
df2["source_ID"] = df2.apply(find_source, axis=1, source_df=df1)

# 保存结果到新的Excel文件
df2.to_excel("output_with_sources_8.xlsx", index=False)  # 保存到新的Excel文件中