import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import seaborn as sns

# Подключение к базе данных
engine = create_engine('sqlite:///youtube.db')
connection = engine.connect()

# Извлечение данных
query = """
SELECT 
    user_profile.user_id, 
    user_profile.first_nm, 
    user_profile.last_nm, 
    COUNT(video.video_id) AS video_count, 
    AVG(video.view_cnt) AS avg_view_count
FROM user_profile
LEFT JOIN video ON user_profile.user_id = video.user_id
GROUP BY user_profile.user_id, user_profile.first_nm, user_profile.last_nm
"""
df = pd.read_sql(query, connection)

# Анализ данных
print(df.describe())

# Построение графиков
plt.figure(figsize=(10, 6))
sns.histplot(df['video_count'], bins=20, kde=True)
plt.title('Distribution of Video Count per User')
plt.xlabel('Video Count')
plt.ylabel('Frequency')
plt.show()

plt.figure(figsize=(10, 6))
sns.scatterplot(x='video_count', y='avg_view_count', data=df)
plt.title('Average View Count vs. Video Count per User')
plt.xlabel('Video Count')
plt.ylabel('Average View Count')
plt.show()
