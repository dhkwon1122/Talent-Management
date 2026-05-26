"""
원시 CSV 데이터를 로드하고 분석에 필요한 집계 형태로 병합한다.
데이터가 없으면 generator를 자동 실행해 생성한다.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT))

RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"


def load_raw() -> dict[str, pd.DataFrame]:
    _ensure_raw_data()
    data = {
        "researchers": pd.read_csv(RAW_DIR / "researchers.csv"),
        "papers":      pd.read_csv(RAW_DIR / "papers.csv"),
        "patents":     pd.read_csv(RAW_DIR / "patents.csv"),
        "projects":    pd.read_csv(RAW_DIR / "projects.csv"),
        "evaluations": pd.read_csv(RAW_DIR / "evaluations.csv"),
    }
    merit_path = RAW_DIR / "merit_standards.csv"
    if merit_path.exists():
        data["merit_standards"] = pd.read_csv(merit_path)
    return data


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

    # --- 업무성과 평가 등급 점수 (최근 연도 가중 평균 + 인상율 보정) ---
    pos_lookup = res.set_index("id")["position"].to_dict()
    evals_ext  = evals.copy()
    evals_ext["position"] = evals_ext["researcher_id"].map(pos_lookup)
    grade_map = _calc_grade_score(evals_ext, raw.get("merit_standards"))
    eval_agg["grade_score"] = eval_agg["researcher_id"].map(grade_map).fillna(60.0)

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


def _calc_grade_score(
    evals: pd.DataFrame,
    standards: pd.DataFrame | None = None,
) -> dict:
    """연도별 평가 등급을 최근 연도 선형 가중 평균 점수(0~100)로 변환.

    성과인상율 보정:
        (연도 × 직급 × 등급) 기준 인상율 대비 개인 인상율 비율로 등급 점수를 조정한다.
        기준율 조회 우선순위: ① merit_standards CSV  ② config 기본값
        보정 계수는 MERIT_CORRECTION_BOUNDS 범위로 클램프한다.
    """
    from config import GRADE_SCORES, GRADE_MERIT_RATES, MERIT_CORRECTION_BOUNDS

    result = {}
    if "performance_grade" not in evals.columns:
        return result

    has_merit  = "merit_raise_rate" in evals.columns
    has_pos    = "position" in evals.columns

    # ① merit_standards CSV → (year, position, grade) 3-key 테이블
    std_lookup: dict = {}
    if standards is not None and not standards.empty:
        for _, r in standards.iterrows():
            std_lookup[(int(r["year"]), r["position"], r["grade"])] = float(r["base_rate"])

    lo, hi = MERIT_CORRECTION_BOUNDS

    for rid, grp in evals.groupby("researcher_id"):
        grp = grp.sort_values("year").reset_index(drop=True)
        n = len(grp)
        weights = np.arange(1, n + 1, dtype=float)
        weights /= weights.sum()

        adjusted = []
        for _, row in grp.iterrows():
            base  = float(GRADE_SCORES.get(row["performance_grade"], 60.0))

            if has_merit:
                year       = int(row["year"])
                grade      = row["performance_grade"]
                pos        = row["position"] if has_pos else None
                indiv_rate = float(row["merit_raise_rate"])

                # 기준율: ① standards CSV(연도·직급·등급) ② config 기본값
                std_rate = (
                    std_lookup.get((year, pos, grade))
                    if pos else None
                ) or GRADE_MERIT_RATES.get(grade, 0.03)

                correction = float(np.clip(
                    indiv_rate / std_rate if std_rate > 0 else 1.0, lo, hi
                ))
            else:
                correction = 1.0

            adjusted.append(base * correction)

        result[rid] = float(np.dot(adjusted, weights))
    return result


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
        return
    # 필수 컬럼 또는 merit_standards.csv 없으면 데이터 재생성
    regen = False
    eval_path = RAW_DIR / "evaluations.csv"
    if eval_path.exists():
        header = pd.read_csv(eval_path, nrows=0)
        if not {"performance_grade", "merit_raise_rate"}.issubset(header.columns):
            regen = True
    if not (RAW_DIR / "merit_standards.csv").exists():
        regen = True
    if regen:
        from src.data.generator import generate_all
        generate_all()


def get_feature_table() -> pd.DataFrame:
    return build_feature_table(load_raw())
