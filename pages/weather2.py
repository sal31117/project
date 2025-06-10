import matplotlib.pyplot as plt

# 데이터프레임에서 NaN 제거
df_clean = df.dropna(subset=["pm10Value", "pm25Value"])

# 그래프 크기 설정
plt.figure(figsize=(10, 5))
plt.plot(df_clean["stationName"], df_clean["pm10Value"], 'bo-', label='PM10')
plt.plot(df_clean["stationName"], df_clean["pm25Value"], 'yo-', label='PM2.5')

plt.xlabel("측정소")
plt.ylabel("농도 (㎍/㎥)")
plt.title(f"{sido} 지역 측정소별 PM10 & PM2.5 농도 비교")
plt.legend()
plt.xticks(rotation=45)
