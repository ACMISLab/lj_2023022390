import pandas as pd
from openai import OpenAI
client = OpenAI(
    base_url='https://api.openai-proxy.org/v1',
    api_key='sk-J2vxk7sWso4VvYQfDo20h9WY4Fd5Q4dnyDAgNLJSfiJE4vOl',
    # api_key='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'
)

# 读取 Excel 文件
input_file_path = r"D:\PythonProjects\AstroCalcBoost\main\AstroConcept\5.匹配例题\output_with_sources_8.xlsx"
df = pd.read_excel(input_file_path)

# 准备输出数据
output_data = []

subfield = "Planets"

# 从 DataFrame 中读取每一行
for i, row in df.iterrows():
    # 使用 iloc 方法按位置访问数据
    topics = row.iloc[0].strip() if pd.notna(row.iloc[0]) else ""  # 第1列为主题
    knowledge_points = [row.iloc[j].strip() if pd.notna(row.iloc[j]) else "" for j in range(1, 8)]  # 第2到6列为知识点
    question = str(row.iloc[10]).strip() if pd.notna(row.iloc[10]) else ""  # 第10列为问题
    # answer = row.iloc[7].strip() if pd.notna(row.iloc[7]) else ""    # 第11列为答案
    answer = str(row.iloc[11]).strip() if pd.notna(row.iloc[11]) else ""

    # 将知识点列表转换为字符串
    knowledge_points_str = ', '.join(knowledge_points)

    # 构建提示词
    prompt = (f'Act as a teacher for {subfield} in a subfield of astronomy and create a new question and its solution based on the provided topics and knowledge points. '
              f'\nEnsure that the created questions:'
              f'\n1. Adhere to the provided topics.'
              f'\n2. Necessitate the combined use of the associated knowledge points.'
              f'\nTopics: {topics} '
              f'\nKnowledge Points: {knowledge_points_str}'
              f'\nThis is an example of a question related to topics and knowledge points.【{question}{answer}】'
              f'\nStructure your response as, and the answer format should follow the structure in 【】: '
              f'\nQuestion:....'
              f'\nAnswer:'
              f'\n【Known conditions: Here, list the known information you obtain based on the content of the problem; '
              f'\nUsing formulas: Here, list the formulas you will use; '
              f'\nSolution steps: Fill in the calculation process here, dividing it into Step One, Step Two, Step Three... Step n (please try to simplify the content and number of steps); '
              f'\nFinal answer: "Here, fill in the final result to the problem, with the last result denoted using $\\boxed$"; please note that only one $\\boxed$ should appear."】')

    print(prompt)
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": str(prompt)}
            ],
            stream=False,
        )
        generated_response = response.choices[0].message.content
        print(generated_response)
    except Exception as e:
        print("无法生成响应")
        generated_response = "无法生成响应"
    print(f"第{i}行已生成完毕！")
    print('-' * 100)  # 分隔线

    # 将结果存储到输出数据列表中
    output_data.append([topics, knowledge_points_str, generated_response])
    # 将结果写入新的 Excel 文件
    output_file_path = r"D:\PythonProjects\AstroCalcBoost\main\AstroConcept\6.数据生成\output_walk_steps_8\Planets_output_walk_result_steps_8补充.xlsx"
    output_df = pd.DataFrame(output_data, columns=['Topics', 'Knowledge Points', 'Output'])
    output_df.to_excel(output_file_path, index=False)  # 保存到新的 Excel 文件中

