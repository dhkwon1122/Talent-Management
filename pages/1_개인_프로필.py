"""개인 인재 프로필: 방사형 차트 + 차원별 점수 배지."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

import streamlit as st

from src.data.loader import get_feature_table, load_raw
from src.scoring.calculator import calculate_raw_scores
from src.scoring.normalizer import normalize
from src.visualization.radar import make_radar_single
from src.visualization.components import (
    researcher_info_card,
    score_badge,
    overall_score_metric,
)
from config import DIMENSIONS, DIMENSION_COLORS, GRADE_SCORES, DEPARTMENTS, MERIT_CORRECTION_BOUNDS

st.set_page_config(page_title="개인 프로필", layout="wide")
st.title("👤 개인 역량 프로필")


@st.cache_data
def load_scores():
    features = get_feature_table()
    raw = calculate_raw_scores(features)
    scores = normalize(raw)
    return features, scores


@st.cache_data
def load_grade_history():
    from config import GRADE_MERIT_RATES, MERIT_CORRECTION_BOUNDS
    raw = load_raw()
    evals = raw["evaluations"]
    if "performance_grade" not in evals.columns:
        return {}, {}

    has_merit = "merit_raise_rate" in evals.columns

    # 연도·등급별 평균 인상율 (보정 기준값)
    if has_merit:
        grade_year_avg = (
            evals.groupby(["year", "performance_grade"])["merit_raise_rate"]
            .mean()
        )

    lo, hi = MERIT_CORRECTION_BOUNDS
    grade_history = {}
    for rid, grp in evals.groupby("researcher_id"):
        grp = grp.sort_values("year").copy()
        rows = []
        for _, r in grp.iterrows():
            base = float(GRADE_SCORES.get(r["performance_grade"], 60.0))
            if has_merit:
                avg_rate = grade_year_avg.get(
                    (r["year"], r["performance_grade"]),
                    GRADE_MERIT_RATES.get(r["performance_grade"], 0.03),
                )
                indiv_rate = float(r["merit_raise_rate"])
                correction = float(min(hi, max(lo, indiv_rate / avg_rate if avg_rate > 0 else 1.0)))
                merit_pct   = round(indiv_rate * 100, 2)
                avg_pct     = round(avg_rate * 100, 2)
            else:
                correction  = 1.0
                merit_pct   = None
                avg_pct     = None

            rows.append({
                "연도":       int(r["year"]),
                "평가등급":   r["performance_grade"],
                "환산점수":   round(base, 1),
                "개인인상율": merit_pct,
                "등급평균인상율": avg_pct,
                "보정계수":   round(correction, 3),
                "보정점수":   round(base * correction, 1),
            })
        grade_history[rid] = rows
    return grade_history, has_merit


features, scores = load_scores()
grade_history, has_merit = load_grade_history()

name_map = dict(zip(features["researcher_id"], features["name"]))
dept_map  = dict(zip(features["researcher_id"], features["department"]))

# ── 사이드바: 조직 → 인재 순으로 선택 ────────────────────────
st.sidebar.header("필터")

# 다른 페이지에서 넘어온 경우 해당 인재의 부서를 기본값으로 설정
_target_id = st.session_state.pop("profile_target", None)
_default_dept = "전체"
if _target_id and _target_id in dept_map:
    _default_dept = dept_map[_target_id]

dept_options = ["전체"] + sorted(DEPARTMENTS)
_dept_idx = dept_options.index(_default_dept) if _default_dept in dept_options else 0
selected_dept = st.sidebar.selectbox("🏢 조직 선택", dept_options, index=_dept_idx)

# 선택 조직으로 인재 목록 필터
if selected_dept == "전체":
    pool = features
else:
    pool = features[features["department"] == selected_dept]

pool_opts = [f"{r} · {name_map[r]}" for r in pool["researcher_id"]]

# 기본 선택 인재 결정
_default_idx = 0
if _target_id:
    _match = [i for i, o in enumerate(pool_opts) if o.startswith(_target_id)]
    if _match:
        _default_idx = _match[0]

selected = st.sidebar.selectbox(
    "👤 인재 선택",
    pool_opts,
    index=_default_idx,
    key=f"profile_person_{selected_dept}",   # 조직 바뀌면 선택 초기화
)
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

# 연도별 업무성과 평가 등급 이력
with st.expander("📊 업무성과 평가 등급 이력"):
    hist_rows = grade_history.get(selected_id)
    if hist_rows:
        grade_colors = {"가": "#1a7f37", "나": "#2da44e", "다": "#f0883e", "라": "#d1242f", "마": "#8b1a1a"}

        # 연도별 카드
        cols_g = st.columns(len(hist_rows))
        for i, row in enumerate(hist_rows):
            grade = row["평가등급"]
            color = grade_colors.get(grade, "#666")
            correction = row["보정계수"]
            arrow = "▲" if correction > 1.0 else ("▼" if correction < 1.0 else "─")
            arr_color = "#1a7f37" if correction > 1.0 else ("#d1242f" if correction < 1.0 else "#888")
            cols_g[i].markdown(
                f"<div style='text-align:center;padding:4px'>"
                f"<div style='font-size:0.8rem;color:#666'>{row['연도']}</div>"
                f"<div style='font-size:2rem;font-weight:bold;color:{color}'>{grade}</div>"
                f"<div style='font-size:0.78rem;color:#888'>{row['보정점수']:.1f}점</div>"
                f"<div style='font-size:0.72rem;color:{arr_color}'>{arrow} ×{correction:.3f}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

        # 성과인상율 상세 테이블
        if has_merit:
            import pandas as pd
            st.markdown("**연도별 성과인상율 상세**")
            tbl = pd.DataFrame(hist_rows)[
                ["연도", "평가등급", "등급평균인상율", "개인인상율", "보정계수", "환산점수", "보정점수"]
            ].rename(columns={
                "등급평균인상율": "등급 평균인상율(%)",
                "개인인상율":     "개인 인상율(%)",
                "보정계수":       "보정 계수",
                "환산점수":       "등급 기준점수",
                "보정점수":       "보정 후 점수",
            })
            st.dataframe(tbl, use_container_width=True, hide_index=True)

        # 최근 연도 가중 평균
        n = len(hist_rows)
        weights = list(range(1, n + 1))
        w_sum = sum(weights)
        weighted_avg = sum(r["보정점수"] * weights[i] for i, r in enumerate(hist_rows)) / w_sum
        st.caption(
            f"최근 연도 가중 평균 보정점수: **{weighted_avg:.1f}점**  "
            f"(최근 연도 비중 높음 · 보정 계수 범위 {MERIT_CORRECTION_BOUNDS[0]}~{MERIT_CORRECTION_BOUNDS[1]})"
        )
    else:
        st.info("평가 등급 데이터가 없습니다.")

# 상세 피처 테이블
with st.expander("📋 원시 지표 상세 보기"):
    detail_cols = [
        "total_papers", "total_citations", "h_index", "registered_patents",
        "grade_score", "lead_project_count", "total_budget_managed", "avg_kpi_achievement",
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
        "grade_score": "업무성과 등급 점수 (가중 평균)",
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
