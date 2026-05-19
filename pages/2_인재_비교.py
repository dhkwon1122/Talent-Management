"""다중 인재 오버레이 레이더 차트 비교 페이지."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

import streamlit as st

from src.data.loader import get_feature_table
from src.scoring.calculator import calculate_raw_scores
from src.scoring.normalizer import normalize
from src.visualization.radar import make_radar_compare
from config import DIMENSIONS, COMPARISON_PALETTE

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
options = [f"{rid} · {name}" for rid, name in name_map.items()]

selected_list = st.sidebar.multiselect(
    "비교할 인재 선택 (2~5명)",
    options,
    default=options[:3],
    max_selections=5,
)

if len(selected_list) < 2:
    st.info("사이드바에서 최소 2명을 선택하세요.")
    st.stop()

selected_ids = [s.split(" · ")[0] for s in selected_list]
selected_names = [name_map[rid] for rid in selected_ids]

subset_scores = scores[scores["researcher_id"].isin(selected_ids)].reset_index(drop=True)

fig = make_radar_compare(subset_scores, selected_names)
st.plotly_chart(fig, use_container_width=True)

# 레전드 클릭 → 개인 프로필 이동
_btn_css = "".join(
    f"div[data-testid='column']:nth-child({i+1}) button[kind='secondary'] {{"
    f"border-left:4px solid {COMPARISON_PALETTE[i % len(COMPARISON_PALETTE)]} !important;"
    f"background:rgba(0,0,0,0.03) !important;}}"
    for i in range(len(selected_ids))
)
st.markdown(f"<style>{_btn_css}</style>", unsafe_allow_html=True)

_btn_cols = st.columns(len(selected_ids))
for _i, (_rid, _name) in enumerate(zip(selected_ids, selected_names)):
    with _btn_cols[_i]:
        if st.button(f"👤 {_name}", key=f"goto_profile_{_rid}", use_container_width=True, help="개인 프로필 보기"):
            st.session_state["profile_target"] = _rid
            st.switch_page("pages/1_개인_프로필.py")

st.divider()
st.subheader("차원별 점수 비교표")

compare_df = subset_scores[["researcher_id"] + DIMENSIONS].copy()
compare_df.insert(0, "이름", selected_names)
compare_df = compare_df.drop(columns=["researcher_id"])
compare_df["종합"] = compare_df[DIMENSIONS].mean(axis=1).round(1)

st.dataframe(
    compare_df.style.background_gradient(
        subset=DIMENSIONS + ["종합"], cmap="RdYlGn", vmin=0, vmax=100
    ).format("{:.1f}", subset=DIMENSIONS + ["종합"]),
    use_container_width=True,
)

# 차원별 1위 강조
st.subheader("차원별 최고 역량 인재")
cols = st.columns(len(DIMENSIONS))
for i, dim in enumerate(DIMENSIONS):
    top_idx = compare_df[dim].idxmax()
    top_name = compare_df.iloc[top_idx]["이름"]
    top_score = compare_df.iloc[top_idx][dim]
    cols[i].metric(dim, top_name, f"{top_score:.1f}점")
