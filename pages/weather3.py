import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
#import koreanize_matplotlib
import folium
from streamlit_folium import st_folium

# 등급 분류 함수
def get_grade(value, pm_type='pm10'):
    if pd.isna(value):
        return "정보 없음"
    if pm_type == 'pm10':
        if value <= 30:
            return "좋음"
        elif value <= 80:
            return "보통"
        else:
            return "나쁨"
    elif pm_type == 'pm25':
        if value <= 15:
            return "좋음"
        elif value <= 35:
            return "보통"
        else:
            return "나쁨"

# 색상 지정 함수 (folium 마커 색상용)
def get_color(grade):
    if grade == "좋음":
        return "green"
    elif grade == "보통":
        return "orange"
    elif grade == "나쁨":
        return "red"
    else:
        return "gray"

# 사용자 입력
st.title("🌫️ 지역별 대기질 등급 확인 및 지도 시각화")
sido = st.selectbox("시/도를 선택하세요", ["서울", "부산", "대구", "인천", "광주", "대전", "울산"])

# API 요청
API_key = st.secrets['API_key']
url = f"http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getCtprvnRltmMesureDnsty"
params = {
    "sidoName": sido,
    "returnType": "json",
    "numOfRows": "100",
    "pageNo": "1",
    "serviceKey": API_key,
    "ver": "1.0"
}

res = requests.get(url, params=params)

if res.status_code == 200:
    try:
        data = res.json()['response']['body']['items']

        # 데이터프레임 변환
        df = pd.DataFrame(data)
        df["pm10Value"] = pd.to_numeric(df["pm10Value"], errors="coerce")
        df["pm25Value"] = pd.to_numeric(df["pm25Value"], errors="coerce")
        df["PM10 등급"] = df["pm10Value"].apply(lambda x: get_grade(x, 'pm10'))
        df["PM2.5 등급"] = df["pm25Value"].apply(lambda x: get_grade(x, 'pm25'))

        # 지도 시각화
        st.write("### 📍 측정소 위치 지도 (임의 좌표 예시)")
        # 좌표 임시 설정 (실제 좌표는 AirKorea에서 제공하지 않으므로 수동 입력 필요)
        # 예시용: 모든 측정소를 중심 좌표에 가깝게 뿌림
        map_center = [36.5, 127.5]  # 대한민국 중심 좌표
        m = folium.Map(location=map_center, zoom_start=7)

        for idx, row in df.iterrows():
            popup_text = f"{row['stationName']}<br>PM10: {row['pm10Value']} ({row['PM10 등급']})<br>PM2.5: {row['pm25Value']} ({row['PM2.5 등급']})"
            folium.CircleMarker(
                location=[map_center[0] + (idx % 5) * 0.1, map_center[1] + (idx % 5) * 0.1],  # 임의 위치
                radius=7,
                color=get_color(row['PM10 등급']),
                fill=True,
                fill_opacity=0.7,
                popup=popup_text
            ).add_to(m)

        st_data = st_folium(m, width=700)

        # 막대그래프 시각화
        st.write(f"### 📊 {sido}의 측정소별 PM10 및 PM2.5 농도")
        fig, ax = plt.subplots(figsize=(12, 6))

        x = df["stationName"]
        bar_width = 0.35
        index = range(len(x))

        ax.bar(index, df["pm10Value"], bar_width, label="PM10", color='blue')
        ax.bar([i + bar_width for i in index], df["pm25Value"], bar_width, label="PM2.5", color='orange')

        ax.set_xlabel('측정소')
        ax.set_ylabel('농도 (㎍/㎥)')
        ax.set_title(f'{sido} 지역의 측정소별 PM10 및 PM2.5 농도')
        ax.set_xticks([i + bar_width / 2 for i in index])
        ax.set_xticklabels(x, rotation=90)
        ax.legend()

        st.pyplot(fig)

        # 테이블 표시
        st.write(f"### 📋 {sido}의 실시간 대기질 정보")
        st.dataframe(df[["stationName", "pm10Value", "PM10 등급", "pm25Value", "PM2.5 등급"]])

    except ValueError:
        st.error("응답 데이터 형식에 오류가 발생했습니다.")
else:
    st.error(f"API 요청에 실패했습니다. 상태 코드: {res.status_code}")
