"""
피처 테이블에서 6개 차원의 원점수를 계산한다.
정규화는 normalizer.py에서 수행한다.
"""
import pandas as pd

from config import DIMENSIONS, SCORING_WEIGHTS


def calculate_raw_scores(features: pd.DataFrame) -> pd.DataFrame:
    """각 차원별 가중합 원점수를 반환한다 (정규화 전)."""
    df = features.copy()

    scores = pd.DataFrame({"researcher_id": df["researcher_id"]})
    for dim in DIMENSIONS:
        scores[dim] = _weighted(df, dim)

    return scores


def _weighted(df: pd.DataFrame, dim: str) -> pd.Series:
    weights = SCORING_WEIGHTS[dim]
    result = pd.Series(0.0, index=df.index)
    for col, w in weights.items():
        if col in df.columns:
            result += df[col].fillna(0) * w
    return result
