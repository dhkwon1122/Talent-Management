"""다중 인재 오버레이 레이더 차트 비교 + 조직 현황 페이지."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

import plotly.graph_objects as go
import streamlit as st

from src.data.loader import get_feature_table
from src.scoring.calculator import calculate_raw_scores
from src.scoring.normalizer import normalize
from src.visualization.radar import make_radar_compare
from config import DIMENSIONS, COMPARISON_PALETTE, DEPARTMENTS, DIMENSION_COLORS

st.set_page_config(page_title="인재 비교", layout="wide")
st.title("⚖️ 인재 역량 비교")


@st.cache_data
def load_scores():
    features = get_feature_table()
    raw = calculate_raw_scores(features)
    scores = normalize(raw)
    return features, scores


features, scores = load_scores()

name_map = dict(zip(features["researcher_id"], features["name"]))
dept_map = dict(zip(features["researcher_id"], features["department"]))
pos_map  = dict(zip(features["researcher_id"], features["position"]))

# ── 사이드바 ──────────────────────────────────────────────────────────────────
st.sidebar.header("필터")
dept_options = ["전체"] + sorted(DEPARTMENTS)
selected_dept = st.sidebar.selectbox("🏢 조직 선택", dept_options)

if selected_dept == "전체":
    pool_ids = list(features["researcher_id"])
    dept_label = "전체 조직"
else:
    pool_ids = list(features[features["department"] == selected_dept]["researcher_id"])
    dept_label = selected_dept

pool_opts = [f"{rid} · {name_map[rid]}" for rid in pool_ids]

selected_list = st.sidebar.multiselect(
    "👤 비교할 인재 선택 (2~5명)",
    pool_opts,
    default=pool_opts[:min(3, len(pool_opts))],
    max_selections=5,
    key=f"cmp_{selected_dept}",  # 조직 바뀌면 선택 초기화
)

# ── 조직 현황 섹션 ─────────────────────────────────────────────────────────────
st.subheader(f"🏢 조직 현황 — {dept_label}")

dept_scores = scores[scores["researcher_id"].isin(pool_ids)].copy()
total_col = dept_scores[DIMENSIONS].mean(axis=1)
dept_avg  = dept_scores[DIMENSIONS].mean()

# 핵심 지표 4개
m1, m2, m3, m4 = st.columns(4)
m1.metric("구성원 수",      f"{len(dept_scores)}명")
m2.metric("평균 종합점수",  f"{total_col.mean():.1f}점")
m3.metric("최고 종합점수",  f"{total_col.max():.1f}점")
m4.metric("최저 종합점수",  f"{total_col.min():.1f}점")

# 구성원 히트맵 테이블
disp = dept_scores[["researcher_id"] + DIMENSIONS].copy()
disp.insert(0, "이름",  [name_map[r] for r in disp["researcher_id"]])
disp.insert(1, "부서",  [dept_map[r] for r in disp["researcher_id"]])
disp.insert(2, "직급",  [pos_map[r]  for r in disp["researcher_id"]])
disp = disp.drop(columns=["researcher_id"])
disp["종합"] = disp[DIMENSIONS].mean(axis=1).round(1)
disp = disp.sort_values("종합", ascending=False).reset_index(drop=True)

with st.expander("📋 구성원 전체 현황 (점수 히트맵)", expanded=True):
    tbl_h = min(40 * (len(disp) + 1) + 80, 520)
    fmt_cols = DIMENSIONS + ["종합"]
    st.dataframe(
        disp.style
            .background_gradient(subset=fmt_cols, cmap="RdYlGn", vmin=0, vmax=100)
            .format("{:.1f}", subset=fmt_cols),
        use_container_width=True,
        height=tbl_h,
    )

# 차원별 조직 평균 가로 바 차트
fig_bar = go.Figure()
fig_bar.add_trace(go.Bar(
    x=[dept_avg[d] for d in DIMENSIONS],
    y=DIMENSIONS,
    orientation="h",
    marker_color=[DIMENSION_COLORS[d] for d in DIMENSIONS],
    text=[f"{dept_avg[d]:.1f}" for d in DIMENSIONS],
    textposition="outside",
    hovertemplate="%{y}: %{x:.1f}점<extra></extra>",
))
fig_bar.update_layout(
    title=dict(text=f"{dept_label} 차원별 평균 점수", font=dict(size=14), x=0),
    xaxis=dict(range=[0, 115], showgrid=True, gridcolor="#eeeeee"),
    yaxis=dict(autorange="reversed"),
    height=270,
    margin=dict(t=40, b=20, l=10, r=60),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
)
st.plotly_chart(fig_bar, use_container_width=True)

# ── 개인 비교 섹션 ─────────────────────────────────────────────────────────────
st.divider()
st.subheader("🔍 개인 역량 비교")

if len(selected_list) < 2:
    st.info("사이드바에서 최소 2명을 선택하세요.")
    st.stop()

selected_ids   = [s.split(" · ")[0] for s in selected_list]
selected_names = [name_map[rid] for rid in selected_ids]

subset_scores = scores[scores["researcher_id"].isin(selected_ids)].reset_index(drop=True)

# 레이더 차트 (조직 평균 참조선 포함)
fig_radar = make_radar_compare(
    subset_scores, selected_names,
    reference=dept_avg, ref_name=f"{dept_label} 평균",
)
st.plotly_chart(fig_radar, use_container_width=True)

# 프로필 이동 버튼
_btn_css = "".join(
    f"div[data-testid='column']:nth-child({i+1}) button[kind='secondary'] {{"
    f"border-left:4px solid {COMPARISON_PALETTE[i % len(COMPARISON_PALETTE)]} !important;}}"
    for i in range(len(selected_ids))
)
st.markdown(f"<style>{_btn_css}</style>", unsafe_allow_html=True)

btn_cols = st.columns(len(selected_ids))
for i, (rid, name) in enumerate(zip(selected_ids, selected_names)):
    with btn_cols[i]:
        if st.button(f"👤 {name}", key=f"goto_{rid}", use_container_width=True, help="개인 프로필 보기"):
            st.session_state["profile_target"] = rid
            st.switch_page("pages/1_개인_프로필.py")

st.divider()

# 차원별 점수 비교표
st.subheader("차원별 점수 비교표")
compare_df = subset_scores[["researcher_id"] + DIMENSIONS].copy()
compare_df.insert(0, "이름", selected_names)
compare_df.insert(1, "부서", [dept_map[r] for r in compare_df["researcher_id"]])
compare_df = compare_df.drop(columns=["researcher_id"])
compare_df["종합"] = compare_df[DIMENSIONS].mean(axis=1).round(1)

# 조직 평균 행 추가
avg_row = {"이름": f"── {dept_label} 평균", "부서": ""}
for d in DIMENSIONS:
    avg_row[d] = round(float(dept_avg[d]), 1)
avg_row["종합"] = round(float(dept_avg[DIMENSIONS].mean()), 1)

import pandas as pd
compare_with_avg = pd.concat(
    [compare_df, pd.DataFrame([avg_row])], ignore_index=True
)

st.dataframe(
    compare_with_avg.style
        .background_gradient(subset=DIMENSIONS + ["종합"], cmap="RdYlGn", vmin=0, vmax=100)
        .format("{:.1f}", subset=DIMENSIONS + ["종합"]),
    use_container_width=True,
)

# 차원별 1위
st.subheader("차원별 최고 역량 인재")
dim_cols = st.columns(len(DIMENSIONS))
for i, dim in enumerate(DIMENSIONS):
    top_idx  = compare_df[dim].idxmax()
    top_name = compare_df.iloc[top_idx]["이름"]
    top_val  = compare_df.iloc[top_idx][dim]
    delta    = round(top_val - float(dept_avg[dim]), 1)
    dim_cols[i].metric(dim, top_name, f"조직 평균 대비 {delta:+.1f}점")
