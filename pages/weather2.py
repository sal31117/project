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

# Streamlit 앱 제목
st.title("🌫️ 지역별 대기질 등급 확인")

# 사용자 입력 (시/도 선택)
sido = st.selectbox("시/도를 선택하세요", ["서울", "부산", "대구", "인천", "광주", "대전", "울산"])

# API 요청
API_key = st.secrets['API_key']  # .streamlit/secrets.toml에 API_key를 저장해두세요.
url = f"http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getCtprvnRltmMesureDnsty"
params = {
    "sidoName": sido,
    "returnType": "json",
    "numOfRows": "100",
    "pageNo": "1",
    "serviceKey": API_key,
    "ver": "1.0"
}

# API 요청 및 응답 상태 코드 체크
res = requests.get(url, params=params)

if res.status_code == 200:  # HTTP 요청 성공 시
    try:
        data = res.json()['response']['body']['items']
       
        # 데이터프레임 변환
        df = pd.DataFrame(data)
        df["pm10Value"] = pd.to_numeric(df["pm10Value"], errors="coerce")
        df["pm25Value"] = pd.to_numeric(df["pm25Value"], errors="coerce")
        df["PM10 등급"] = df["pm10Value"].apply(lambda x: get_grade(x, 'pm10'))
        df["PM2.5 등급"] = df["pm25Value"].apply(lambda x: get_grade(x, 'pm25'))

        # 측정소별 대기질 막대그래프 시각화
        st.write(f"### {sido}의 실시간 대기질 막대그래프")

        fig, ax = plt.subplots(figsize=(12, 6))
        bar_width = 0.35
        x = range(len(df['stationName']))
        ax.bar(x, df['pm10Value'], bar_width, label='PM10', color='skyblue')
        ax.bar([i + bar_width for i in x], df['pm25Value'], bar_width, label='PM2.5', color='salmon')
        ax.set_xticks([i + bar_width / 2 for i in x])
        ax.set_xticklabels(df['stationName'], rotation=45, ha='right')
        ax.set_ylabel('농도 (㎍/㎥)')
        ax.set_title(f'{sido} 지역의 실시간 대기질 (PM10 & PM2.5)')
        ax.legend()
        fig.tight_layout()

        st.pyplot(fig)

        # 데이터 테이블 출력
        st.write(f"### {sido}의 실시간 대기질 정보")
        st.dataframe(df[["stationName", "pm10Value", "PM10 등급", "pm25Value", "PM2.5 등급"]])

    except Exception as e:
        st.error(f"데이터 처리 중 오류가 발생했습니다: {e}")
else:
    st.error(f"API 요청에 실패했습니다. 상태 코드: {res.status_code}")
