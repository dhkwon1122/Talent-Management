"""전체 인재 히트맵 + 종합 순위 페이지."""
import streamlit as st
import plotly.express as px
import pandas as pd

from src.services.talent_scores import load_scores
from src.visualization.components import heatmap_table
from config import DIMENSIONS

st.set_page_config(page_title="전체 현황", layout="wide")
st.title("📊 전체 인재 역량 현황")


features, scores = load_scores()

name_map = dict(zip(features["researcher_id"], features["name"]))
dept_map = dict(zip(features["researcher_id"], features["department"]))
pos_map = dict(zip(features["researcher_id"], features["position"]))

# 필터
dept_filter = st.sidebar.multiselect("부서 필터", options=features["department"].unique().tolist())
pos_filter = st.sidebar.multiselect("직급 필터", options=features["position"].unique().tolist())

mask = pd.Series([True] * len(scores))
if dept_filter:
    mask &= scores["researcher_id"].map(dept_map).isin(dept_filter)
if pos_filter:
    mask &= scores["researcher_id"].map(pos_map).isin(pos_filter)

filtered_scores = scores[mask].reset_index(drop=True)
filtered_names = [name_map[rid] for rid in filtered_scores["researcher_id"]]
filtered_dept = [dept_map[rid] for rid in filtered_scores["researcher_id"]]
filtered_pos = [pos_map[rid] for rid in filtered_scores["researcher_id"]]

if filtered_scores.empty:
    st.warning("선택된 조건에 해당하는 인재가 없습니다.")
    st.stop()

# 종합 순위 테이블
st.subheader("역량 히트맵 (전 인재)")
heatmap_table(filtered_scores, filtered_names)

st.divider()

# 종합 점수 Bar 차트
st.subheader("종합 역량 순위")
rank_df = filtered_scores[["researcher_id"] + DIMENSIONS].copy()
rank_df["이름"] = filtered_names
rank_df["부서"] = filtered_dept
rank_df["직급"] = filtered_pos
rank_df["종합"] = rank_df[DIMENSIONS].mean(axis=1).round(1)
rank_df = rank_df.sort_values("종합", ascending=False).reset_index(drop=True)
rank_df.index = rank_df.index + 1

fig_bar = px.bar(
    rank_df,
    x="이름",
    y="종합",
    color="부서",
    hover_data=["직급"] + DIMENSIONS,
    labels={"종합": "종합 역량 점수"},
    title="인재별 종합 역량 점수",
    height=420,
)
fig_bar.update_layout(xaxis_tickangle=-30)
st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# 차원별 분포 박스플롯
st.subheader("차원별 점수 분포")
melt_df = filtered_scores[DIMENSIONS].copy()
melt_df["이름"] = filtered_names
melt_df = melt_df.melt(id_vars="이름", var_name="차원", value_name="점수")

fig_box = px.box(
    melt_df,
    x="차원",
    y="점수",
    color="차원",
    points="all",
    hover_data=["이름"],
    title="차원별 점수 분포 (전 인재)",
    height=420,
)
fig_box.update_layout(showlegend=False)
st.plotly_chart(fig_box, use_container_width=True)
