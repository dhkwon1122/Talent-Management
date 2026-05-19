"""
집단 내 원점수를 0~100 점수로 정규화한다.
Min-Max 정규화 후 분포 평탄화를 위해 루트 변환을 선택적으로 적용한다.
"""
import numpy as np
import pandas as pd

from config import DIMENSIONS


def normalize(raw_scores: pd.DataFrame, method: str = "minmax") -> pd.DataFrame:
    """
    raw_scores: researcher_id + 6개 차원 원점수 DataFrame
    method: 'minmax' | 'rank'
    반환: 0~100 정규화된 점수 DataFrame
    """
    normalized = raw_scores[["researcher_id"]].copy()
    for dim in DIMENSIONS:
        if dim not in raw_scores.columns:
            normalized[dim] = 0.0
            continue
        series = raw_scores[dim].astype(float)
        if method == "rank":
            normalized[dim] = _rank_normalize(series)
        else:
            normalized[dim] = _minmax_normalize(series)
    return normalized


def _minmax_normalize(series: pd.Series) -> pd.Series:
    lo, hi = series.min(), series.max()
    if hi == lo:
        return pd.Series(50.0, index=series.index)
    normed = (series - lo) / (hi - lo)
    # 루트 변환으로 하위 점수대 가독성 향상
    return (np.sqrt(normed) * 100).round(1)


def _rank_normalize(series: pd.Series) -> pd.Series:
    ranks = series.rank(method="average", pct=True)
    return (ranks * 100).round(1)
