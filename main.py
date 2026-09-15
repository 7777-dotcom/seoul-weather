import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="서울 100년 기온 변화", page_icon="🌡️", layout="wide")

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/seoul.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL, encoding="utf-8-sig")
    df["날짜"] = pd.to_datetime(df["날짜"])
    df["연도"] = df["날짜"].dt.year
    return df


st.title("🌡️ 서울, 100년의 기온 변화")
st.markdown("서울의 관측 데이터를 바탕으로 **연평균 기온**이 지난 100여 년간 어떻게 변해왔는지 살펴봅니다.")

df = load_data()

# 연도별 평균/최저/최고 기온 집계
yearly = (
    df.groupby("연도")[["평균기온", "최저기온", "최고기온"]]
    .mean()
    .reset_index()
)

min_year, max_year = int(yearly["연도"].min()), int(yearly["연도"].max())

# 사이드바: 기간 선택 및 옵션
st.sidebar.header("⚙️ 옵션")
year_range = st.sidebar.slider(
    "표시할 기간을 선택하세요",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),
)
show_trend = st.sidebar.checkbox("추세선(선형회귀) 표시", value=True)
show_minmax = st.sidebar.checkbox("최저·최고 기온도 함께 표시", value=False)

filtered = yearly[(yearly["연도"] >= year_range[0]) & (yearly["연도"] <= year_range[1])]

# 상단 요약 지표
col1, col2, col3 = st.columns(3)
first_val = filtered["평균기온"].iloc[0]
last_val = filtered["평균기온"].iloc[-1]
diff = last_val - first_val
col1.metric(f"{int(filtered['연도'].iloc[0])}년 연평균 기온", f"{first_val:.1f} °C")
col2.metric(f"{int(filtered['연도'].iloc[-1])}년 연평균 기온", f"{last_val:.1f} °C", f"{diff:+.1f} °C")
col3.metric("선택 기간", f"{year_range[1] - year_range[0] + 1}년간")

# 그래프
fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=filtered["연도"],
        y=filtered["평균기온"],
        mode="lines+markers",
        name="연평균 기온",
        line=dict(color="#e45756", width=2),
        marker=dict(size=4),
    )
)

if show_minmax:
    fig.add_trace(
        go.Scatter(
            x=filtered["연도"],
            y=filtered["최고기온"],
            mode="lines",
            name="연평균 최고기온",
            line=dict(color="#f2a35c", width=1, dash="dot"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=filtered["연도"],
            y=filtered["최저기온"],
            mode="lines",
            name="연평균 최저기온",
            line=dict(color="#4c78a8", width=1, dash="dot"),
        )
    )

if show_trend and len(filtered) > 1:
    coeffs = np.polyfit(filtered["연도"], filtered["평균기온"], 1)
    trend_line = np.polyval(coeffs, filtered["연도"])
    fig.add_trace(
        go.Scatter(
            x=filtered["연도"],
            y=trend_line,
            mode="lines",
            name="추세선",
            line=dict(color="gray", width=2, dash="dash"),
        )
    )
    decade_change = coeffs[0] * 10
    st.info(f"📈 선택 기간 동안 기온은 10년마다 약 **{decade_change:+.2f} °C** 변화하는 추세입니다.")

fig.update_layout(
    title="서울 연평균 기온 변화 추이",
    xaxis_title="연도",
    yaxis_title="기온 (°C)",
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    height=550,
)

st.plotly_chart(fig, use_container_width=True)

with st.expander("📋 연도별 데이터 표 보기"):
    st.dataframe(
        filtered.rename(
            columns={"평균기온": "연평균 기온(°C)", "최저기온": "연평균 최저기온(°C)", "최고기온": "연평균 최고기온(°C)"}
        ).set_index("연도"),
        use_container_width=True,
    )

st.caption("데이터 출처: greatsong/modudata (서울 기상 관측 자료)")
