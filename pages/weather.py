import streamlit as st
import requests
import pandas as pd

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
KEY = st.secrets['API_KEY']
url = f"http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getCtprvnRltmMesureDnsty"
params = {
    "sidoName": sido,
    "returnType": "json",
    "numOfRows": "100",
    "pageNo": "1",
    "serviceKey": KEY,
    "ver": "1.0"
}
res = requests.get(url, params=params)
data = res.json()['response']['body']['items']

# 데이터프레임 변환
df = pd.DataFrame(data)
df["pm10Value"] = pd.to_numeric(df["pm10Value"], errors="coerce")
df["pm25Value"] = pd.to_numeric(df["pm25Value"], errors="coerce")
df["PM10 등급"] = df["pm10Value"].apply(lambda x: get_grade(x, 'pm10'))
df["PM2.5 등급"] = df["pm25Value"].apply(lambda x: get_grade(x, 'pm25'))

st.write(f"### {sido}의 실시간 대기질 정보")
st.dataframe(df[["stationName", "pm10Value", "PM10 등급", "pm25Value", "PM2.5 등급"]])
