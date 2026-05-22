"""개인 인재 프로필: 방사형 차트 + 차원별 점수 배지."""
import streamlit as st

from src.services.talent_scores import load_scores
from src.visualization.radar import make_radar_single
from src.visualization.components import (
    researcher_info_card,
    score_badge,
    overall_score_metric,
)
from config import DIMENSIONS

st.set_page_config(page_title="개인 프로필", layout="wide")
st.title("👤 개인 역량 프로필")


features, scores = load_scores()

name_map = dict(zip(features["researcher_id"], features["name"]))
options = [f"{rid} · {name}" for rid, name in name_map.items()]

_default_idx = 0
if "profile_target" in st.session_state:
    _target = st.session_state.pop("profile_target")
    _match = [i for i, opt in enumerate(options) if opt.startswith(_target)]
    if _match:
        _default_idx = _match[0]

selected = st.sidebar.selectbox("인재 선택", options, index=_default_idx)
selected_id = selected.split(" · ")[0]

feat_row = features[features["researcher_id"] == selected_id].iloc[0]
score_row = scores[scores["researcher_id"] == selected_id].iloc[0]

# 기본 정보
researcher_info_card(feat_row)
overall_score_metric(score_row)

st.divider()

col_chart, col_badges = st.columns([3, 2])

with col_chart:
    color = "#4C72B0"
    fig = make_radar_single(score_row, name=feat_row["name"], color=color)
    st.plotly_chart(fig, use_container_width=True)

with col_badges:
    st.subheader("차원별 점수")
    for dim in DIMENSIONS:
        score_badge(dim, float(score_row[dim]))

# 상세 피처 테이블
with st.expander("📋 원시 지표 상세 보기"):
    detail_cols = [
        "total_papers", "total_citations", "h_index", "registered_patents",
        "lead_project_count", "total_budget_managed", "avg_kpi_achievement",
        "leadership_peer_score", "mentoring_count",
        "english_score", "overseas_months", "international_papers",
        "intra_collab_count", "external_collab_count",
        "performance_growth_rate", "annual_training_hours",
    ]
    available = [c for c in detail_cols if c in feat_row.index]
    detail_df = feat_row[available].to_frame(name="값").rename(index={
        "total_papers": "논문 수",
        "total_citations": "총 피인용 수",
        "h_index": "h-index",
        "registered_patents": "등록 특허 수",
        "lead_project_count": "주관 과제 수",
        "total_budget_managed": "관리 예산 합계 (백만원)",
        "avg_kpi_achievement": "평균 KPI 달성률",
        "leadership_peer_score": "리더십 동료 평가",
        "mentoring_count": "멘토링 건수",
        "english_score": "영어 점수 (평균)",
        "overseas_months": "해외 파견 누적 (개월)",
        "international_papers": "국제 공동 논문 수",
        "intra_collab_count": "사내 협업 과제 수",
        "external_collab_count": "외부 협력 건수",
        "performance_growth_rate": "KPI 성장률",
        "annual_training_hours": "연평균 교육 시간 (h)",
    })
    detail_df["값"] = detail_df["값"].apply(lambda v: f"{v:.2f}" if isinstance(v, float) else v)
    st.dataframe(detail_df, use_container_width=True)
