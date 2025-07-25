import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

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

# 사용자 입력
st.title("🌫️ 지역별 대기질 등급 확인")
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

        # 시각화: 측정소별 대기질 막대 그래프
        st.write(f"### {sido}의 측정소별 대기질 현황")
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
        st.write(f"### {sido}의 실시간 대기질 정보")
        st.dataframe(df[["stationName", "pm10Value", "PM10 등급", "pm25Value", "PM2.5 등급"]])

    except ValueError:
        st.error("응답 데이터 형식에 오류가 발생했습니다.")
else:
    st.error(f"API 요청에 실패했습니다. 상태 코드: {res.status_code}")

