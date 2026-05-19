"""재사용 가능한 Streamlit UI 컴포넌트."""
import streamlit as st
import pandas as pd

from config import DIMENSIONS, DIMENSION_COLORS


def score_badge(dim: str, score: float) -> None:
    color = DIMENSION_COLORS.get(dim, "#888")
    grade, grade_color = _grade(score)
    st.markdown(
        f"""
        <div style="
            border-left: 5px solid {color};
            padding: 8px 14px;
            margin-bottom: 8px;
            background: #f8f9fa;
            border-radius: 4px;
        ">
            <span style="font-weight:600; font-size:14px;">{dim}</span>
            <span style="float:right; font-size:18px; font-weight:700; color:{color};">{score:.1f}</span>
            <span style="float:right; margin-right:10px; font-size:12px;
                background:{grade_color}; color:white; padding:2px 7px;
                border-radius:10px;">{grade}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def researcher_info_card(row: pd.Series) -> None:
    st.markdown(
        f"""
        <div style="background:#f0f4f8; border-radius:8px; padding:16px; margin-bottom:16px;">
            <h3 style="margin:0 0 6px 0;">{row['name']}</h3>
            <p style="margin:2px 0; color:#555;">{row['department']} · {row['position']}</p>
            <p style="margin:2px 0; color:#555;">경력 {row['career_years']}년 · {row['education']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def overall_score_metric(scores_row: pd.Series) -> None:
    total = scores_row[DIMENSIONS].mean()
    st.metric("종합 역량 점수", f"{total:.1f} / 100")


def heatmap_table(scores_df: pd.DataFrame, names: list[str]) -> None:
    display = scores_df[["researcher_id"] + DIMENSIONS].copy()
    display.insert(0, "이름", names)
    display = display.drop(columns=["researcher_id"])
    display["종합"] = display[DIMENSIONS].mean(axis=1).round(1)
    display = display.sort_values("종합", ascending=False).reset_index(drop=True)

    st.dataframe(
        display.style.background_gradient(subset=DIMENSIONS + ["종합"], cmap="RdYlGn", vmin=0, vmax=100),
        use_container_width=True,
        height=min(40 * (len(display) + 1) + 50, 600),
    )


def _grade(score: float) -> tuple[str, str]:
    if score >= 80:
        return "S", "#2E7D32"
    elif score >= 65:
        return "A", "#1565C0"
    elif score >= 50:
        return "B", "#F57F17"
    elif score >= 35:
        return "C", "#E65100"
    else:
        return "D", "#B71C1C"
