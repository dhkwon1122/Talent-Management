"""
Plotly 방사형(레이더) 차트 생성 모듈.
단일 인재 차트와 다중 인재 오버레이 차트를 지원한다.
"""
import plotly.graph_objects as go
import pandas as pd

from config import DIMENSIONS, COMPARISON_PALETTE


def make_radar_single(row: pd.Series, name: str, color: str = "#4C72B0") -> go.Figure:
    """단일 인재 레이더 차트."""
    values = [float(row[dim]) for dim in DIMENSIONS]
    return _build_figure(
        categories=DIMENSIONS,
        traces=[{"name": name, "values": values, "color": color}],
        title=f"{name} 역량 프로파일",
    )


def make_radar_compare(scores_df: pd.DataFrame, names: list[str]) -> go.Figure:
    """다수 인재 오버레이 레이더 차트."""
    traces = []
    for i, (_, row) in enumerate(scores_df.iterrows()):
        values = [float(row[dim]) for dim in DIMENSIONS]
        traces.append({
            "name": names[i],
            "values": values,
            "color": COMPARISON_PALETTE[i % len(COMPARISON_PALETTE)],
        })
    return _build_figure(
        categories=DIMENSIONS,
        traces=traces,
        title="인재 역량 비교",
    )


def _build_figure(categories: list, traces: list[dict], title: str) -> go.Figure:
    fig = go.Figure()
    closed_cats = categories + [categories[0]]

    for t in traces:
        closed_vals = t["values"] + [t["values"][0]]
        fig.add_trace(go.Scatterpolar(
            r=closed_vals,
            theta=closed_cats,
            fill="toself",
            name=t["name"],
            line=dict(color=t["color"], width=2),
            fillcolor=_hex_to_rgba(t["color"], alpha=0.15),
            hovertemplate="%{theta}: %{r:.1f}<extra>" + t["name"] + "</extra>",
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=10),
                tickvals=[20, 40, 60, 80, 100],
            ),
            angularaxis=dict(tickfont=dict(size=13)),
        ),
        showlegend=True,
        title=dict(text=title, font=dict(size=16), x=0.5),
        margin=dict(t=80, b=40, l=60, r=60),
        height=500,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def _hex_to_rgba(hex_color: str, alpha: float = 0.2) -> str:
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"
