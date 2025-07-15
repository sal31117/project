import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
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

# 색상 지정 함수 (folium 마커용)
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
st.title("🌫️ 지역별 대기질 확인 및 지도 시각화")
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
        df = pd.DataFrame(data)
        df["pm10Value"] = pd.to_numeric(df["pm10Value"], errors="coerce")
        df["pm25Value"] = pd.to_numeric(df["pm25Value"], errors="coerce")
        df["PM10 등급"] = df["pm10Value"].apply(lambda x: get_grade(x, 'pm10'))
        df["PM2.5 등급"] = df["pm25Value"].apply(lambda x: get_grade(x, 'pm25'))

        # folium 지도 생성 (측정소 위치는 임의 위치 사용)
        st.write("### 측정소 위치 지도 (예시 위치)")
        center = [36.5, 127.5]  # 한국 중심
        m = folium.Map(location=center, zoom_start=7)

        for i, row in df.iterrows():
            # 임의로 위치 흩뿌리기 (실제 좌표 아님)
            lat = center[0] + (i % 5) * 0.1
            lon = center[1] + (i % 5) * 0.1
            popup = f"{row['stationName']}<br>PM10: {row['pm10Value']} ({row['PM10 등급']})<br>PM2.5: {row['pm25Value']} ({row['PM2.5 등급']})"
            folium.CircleMarker(
                location=[lat, lon],
                radius=7,
                color=get_color(row['PM10 등급']),
                fill=True,
                fill_opacity=0.7,
                popup=popup
            ).add_to(m)

        st_folium(m, width=700)

        # 막대그래프 (matplotlib, 한글 깨질 수 있음)
        st.write(f"### {sido} 측정소별 PM10 및 PM2.5 농도")
        fig, ax = plt.subplots(figsize=(12, 6))

        index = range(len(df["stationName"]))
        bar_width = 0.35

        ax.bar(index, df["pm10Value"], bar_width, label="PM10", color="blue")
        ax.bar([i + bar_width for i in index], df["pm25Value"], bar_width, label="PM2.5", color="orange")

        ax.set_xlabel("측정소")
        ax.set_ylabel("농도 (㎍/㎥)")
        ax.set_title(f"{sido} 지역 PM10 / PM2.5")
        ax.set_xticks([i + bar_width / 2 for i in index])
        ax.set_xticklabels(df["stationName"], rotation=90)
        ax.legend()

        st.pyplot(fig)

        # 테이블 출력
        st.write("### 실시간 대기질 정보")
        st.dataframe(df[["stationName", "pm10Value", "PM10 등급", "pm25Value", "PM2.5 등급"]])

    except Exception as e:
        st.error(f"데이터 처리 중 오류 발생: {e}")
else:
    st.error(f"API 요청 실패: 상태 코드 {res.status_code}")
