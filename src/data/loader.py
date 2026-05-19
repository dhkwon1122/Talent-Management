"""
원시 CSV 데이터를 로드하고 분석에 필요한 집계 형태로 병합한다.
데이터가 없으면 generator를 자동 실행해 생성한다.
"""
import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT))

RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"


def load_raw() -> dict[str, pd.DataFrame]:
    _ensure_raw_data()
    return {
        "researchers": pd.read_csv(RAW_DIR / "researchers.csv"),
        "papers": pd.read_csv(RAW_DIR / "papers.csv"),
        "patents": pd.read_csv(RAW_DIR / "patents.csv"),
        "projects": pd.read_csv(RAW_DIR / "projects.csv"),
        "evaluations": pd.read_csv(RAW_DIR / "evaluations.csv"),
    }


def build_feature_table(raw: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """인재별 원시 집계 피처 테이블을 반환한다."""
    res = raw["researchers"].copy()
    papers = raw["papers"]
    patents = raw["patents"]
    projects = raw["projects"]
    evals = raw["evaluations"]

    # --- 논문 집계 ---
    paper_agg = papers.groupby("researcher_id").agg(
        total_papers=("citations", "count"),
        total_citations=("citations", "sum"),
        international_papers=("is_international", "sum"),
    ).reset_index()
    paper_agg["h_index"] = papers.groupby("researcher_id")["citations"].apply(
        _calc_h_index
    ).reset_index(drop=True)

    # h_index 재계산 (groupby apply 순서 맞추기)
    h_map = {rid: _calc_h_index(grp["citations"]) for rid, grp in papers.groupby("researcher_id")}
    paper_agg["h_index"] = paper_agg["researcher_id"].map(h_map)

    # --- 특허 집계 ---
    patent_agg = patents.groupby("researcher_id").agg(
        registered_patents=("status", lambda s: (s == "등록").sum()),
        tech_transfers=("is_tech_transfer", "sum"),
    ).reset_index()

    # --- 과제 집계 ---
    lead_proj = projects[projects["role"] == "주관"]
    project_agg = projects.groupby("researcher_id").agg(
        avg_kpi_achievement=("kpi_achievement", "mean"),
        total_budget_managed=("budget_million", "sum"),
    ).reset_index()
    lead_agg = lead_proj.groupby("researcher_id").agg(
        lead_project_count=("project_id", "count"),
    ).reset_index()
    project_agg = project_agg.merge(lead_agg, on="researcher_id", how="left")
    project_agg["lead_project_count"] = project_agg["lead_project_count"].fillna(0)

    # --- 성장 추이 (최근 3년 KPI 평균 증감률) ---
    growth_map = _calc_growth_rate(projects)
    project_agg["performance_growth_rate"] = project_agg["researcher_id"].map(growth_map).fillna(0)

    # --- 평가 집계 (전 기간 평균) ---
    eval_agg = evals.groupby("researcher_id").agg(
        english_score=("english_score", "mean"),
        overseas_months=("overseas_months", "sum"),
        peer_review_score=("peer_review_score", "mean"),
        leadership_peer_score=("leadership_score", "mean"),
        mentoring_count=("mentoring_count", "sum"),
        intra_collab_count=("intra_collab_count", "sum"),
        external_collab_count=("external_collab_count", "sum"),
        annual_training_hours=("training_hours", "mean"),
    ).reset_index()
    eval_agg["english_score_norm"] = eval_agg["english_score"] / 990.0

    # --- 국제 논문 (evaluations + papers 합산) ---
    intl_paper_agg = evals.groupby("researcher_id")["international_papers"].sum().reset_index()
    eval_agg = eval_agg.merge(intl_paper_agg, on="researcher_id", how="left")

    # --- 전체 병합 ---
    df = res.rename(columns={"id": "researcher_id"})
    for agg_df in [paper_agg, patent_agg, project_agg, eval_agg]:
        df = df.merge(agg_df, on="researcher_id", how="left")

    df["achievement_efficiency"] = (
        df["total_papers"].fillna(0) + df["lead_project_count"].fillna(0)
    ) / df["career_years"].clip(lower=1)

    df = df.fillna(0)

    # --- 정성 코멘트 텍스트 점수 통합 ---
    peer_path = RAW_DIR / "peer_review_comments.csv"
    leadership_path = RAW_DIR / "leadership_comments.csv"
    if peer_path.exists() or leadership_path.exists():
        try:
            from src.scoring.text_scorer import score_all_comments
            peer_df = pd.read_csv(peer_path) if peer_path.exists() else None
            leadership_df = pd.read_csv(leadership_path) if leadership_path.exists() else None
            text_scores = score_all_comments(peer_df, leadership_df)
            df["peer_review_text_score"] = (
                df["researcher_id"].map(text_scores.get("peer_review_text_score", {})).fillna(5.0)
            )
            df["leadership_text_score"] = (
                df["researcher_id"].map(text_scores.get("leadership_text_score", {})).fillna(5.0)
            )
        except Exception as e:
            print(f"[loader] 텍스트 점수 로드 실패, 기본값 사용: {e}")
            df["peer_review_text_score"] = 5.0
            df["leadership_text_score"] = 5.0
    else:
        df["peer_review_text_score"] = 5.0
        df["leadership_text_score"] = 5.0

    return df


def _calc_h_index(citations: pd.Series) -> int:
    sorted_cites = sorted(citations, reverse=True)
    h = 0
    for i, c in enumerate(sorted_cites):
        if c >= i + 1:
            h = i + 1
        else:
            break
    return h


def _calc_growth_rate(projects: pd.DataFrame) -> dict:
    """연구자별 최근 3년 대비 이전 3년 KPI 평균 증감률."""
    result = {}
    recent_years = projects["year"].max()
    for rid, grp in projects.groupby("researcher_id"):
        recent = grp[grp["year"] >= recent_years - 2]["kpi_achievement"].mean()
        prev = grp[grp["year"] < recent_years - 2]["kpi_achievement"].mean()
        if pd.isna(prev) or prev == 0:
            result[rid] = 0.0
        else:
            result[rid] = float((recent - prev) / prev)
    return result


def _ensure_raw_data() -> None:
    needed = ["researchers.csv", "peer_review_comments.csv", "leadership_comments.csv"]
    if any(not (RAW_DIR / f).exists() for f in needed):
        from src.data.generator import generate_all
        generate_all()


def get_feature_table() -> pd.DataFrame:
    return build_feature_table(load_raw())
