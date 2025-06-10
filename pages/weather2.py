import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

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

        # 날짜/시간 컬럼이 있는지 확인하고, 없으면 현재 시각으로 대체
        if 'dataTime' in df.columns:
            df['dataTime'] = pd.to_datetime(df['dataTime'], format='%Y-%m-%d %H:%M')  # 데이터에 시간 정보가 있을 경우
        else:
            df['dataTime'] = pd.to_datetime('now')  # 시간 정보가 없으면 현재 시각으로 대체

        # 측정소별 대기질 변화 시각화
        st.write(f"### {sido}의 실시간 대기질 변화")
        
        # 측정소별로 그래프 그리기
        fig, ax = plt.subplots(figsize=(10, 6))
        
        for station in df['stationName'].unique():
            station_data = df[df['stationName'] == station]
            ax.plot(station_data['dataTime'], station_data['pm10Value'], label=f"PM10 - {station}", marker='o')
            ax.plot(station_data['dataTime'], station_data['pm25Value'], label=f"PM2.5 - {station}", marker='o')
        
        ax.set_xlabel('시간')
        ax.set_ylabel('농도 (㎍/㎥)')
        ax.set_title(f'{sido} 지역의 PM10 및 PM2.5 시간대별 변화')
        ax.legend()

        # 시간 x축 포맷 조정
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
        plt.xticks(rotation=45)

        st.pyplot(fig)

        st.write(f"### {sido}의 실시간 대기질 정보")
        st.dataframe(df[["stationName", "pm10Value", "PM10 등급", "pm25Value", "PM2.5 등급"]])

    except ValueError:
        st.error("응답 데이터 형식에 오류가 발생했습니다.")
else:
    st.error(f"API 요청에 실패했습니다. 상태 코드: {res.status_code}")
