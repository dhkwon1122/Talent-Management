"""
피처 테이블에서 6개 차원의 원점수를 계산한다.
정규화는 normalizer.py에서 수행한다.
"""
import pandas as pd

from config import SCORING_WEIGHTS


def calculate_raw_scores(features: pd.DataFrame) -> pd.DataFrame:
    """각 차원별 가중합 원점수를 반환한다 (정규화 전)."""
    df = features.copy()

    scores = pd.DataFrame({"researcher_id": df["researcher_id"]})
    scores["전문성"] = _expertise(df)
    scores["업무성과"] = _performance(df)
    scores["리더십"] = _leadership(df)
    scores["글로벌역량"] = _global_competency(df)
    scores["협업네트워크"] = _network(df)
    scores["성장잠재력"] = _potential(df)

    return scores


def _weighted(df: pd.DataFrame, dim: str) -> pd.Series:
    weights = SCORING_WEIGHTS[dim]
    result = pd.Series(0.0, index=df.index)
    for col, w in weights.items():
        if col in df.columns:
            result += df[col].fillna(0) * w
    return result


def _expertise(df: pd.DataFrame) -> pd.Series:
    return _weighted(df, "전문성")


def _performance(df: pd.DataFrame) -> pd.Series:
    return _weighted(df, "업무성과")


def _leadership(df: pd.DataFrame) -> pd.Series:
    return _weighted(df, "리더십")


def _global_competency(df: pd.DataFrame) -> pd.Series:
    return _weighted(df, "글로벌역량")


def _network(df: pd.DataFrame) -> pd.Series:
    return _weighted(df, "협업네트워크")


def _potential(df: pd.DataFrame) -> pd.Series:
    return _weighted(df, "성장잠재력")
