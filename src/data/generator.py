"""
가상 인재 데이터 생성기.
실제 데이터 연동 전 프로토타이핑용으로 현실적인 분포의 샘플 데이터를 생성한다.
"""
import sys
import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT))

from config import MOCK_CONFIG, POSITIONS, DEPARTMENTS, GRADE_MERIT_RATES

RAW_DIR = Path(__file__).parents[2] / "data" / "raw"

_PEER_TEMPLATES = {
    "high": [
        "팀 프로젝트에서 항상 적극적으로 소통하고 팀원들의 의견을 잘 수렴하여 시너지를 만들어냅니다. 어떤 부서와도 원활히 협력하는 모습이 인상적입니다.",
        "다양한 전문 분야의 연구원들과 경계 없이 협업하며 공동 연구를 성공적으로 이끌어냅니다. 지식 공유에도 매우 적극적입니다.",
        "팀 내외부의 협업 네트워크를 능숙하게 구축하고 관리합니다. 갈등 상황에서도 중재 역할을 잘 수행합니다.",
        "자신의 연구 성과를 팀과 아낌없이 공유하며 공동 논문 작업에서 탁월한 기여를 보여줍니다.",
        "외부 기관과의 협력 과제에서 탁월한 네트워킹 능력을 발휘하여 프로젝트 성공에 핵심 역할을 담당합니다.",
    ],
    "mid": [
        "업무 능력은 뛰어나지만 팀 전체보다는 개인 연구에 집중하는 경향이 있어 협업 참여가 불균형한 편입니다.",
        "협업에 참여하긴 하지만 주도적으로 소통을 이끌어가는 부분이 아쉬우며, 적극적인 정보 공유가 필요합니다.",
        "기술적인 기여는 좋으나 다른 팀원들과의 소통 빈도가 낮아 협업 효율이 저하될 때가 있습니다.",
        "공동 연구에 참여 의지는 있으나 일정 조율이나 커뮤니케이션 면에서 개선이 필요합니다.",
    ],
    "low": [
        "개인 업무에는 충실하나 팀 협업 과제에서 참여도가 전반적으로 낮아 팀원들이 어려움을 겪는 경우가 있습니다.",
        "소통 방식이 다소 일방적이어서 협업 과정에서 갈등이 발생하는 경우가 종종 있습니다.",
        "공동 작업에 소극적인 태도를 보이며 지식 공유에 대한 적극성이 현저히 부족합니다.",
        "팀 미팅에서 의견 개진이 적고 다른 팀원의 연구에 관심을 기울이지 않아 협업 시너지가 낮습니다.",
    ],
}

_LEADERSHIP_TEMPLATES = {
    "high": [
        "팀원 개개인의 강점을 파악하고 역량을 최대한 발휘할 수 있도록 이끌어주는 훌륭한 리더입니다.",
        "어려운 결정 상황에서도 명확한 방향을 제시하고 팀을 안정적으로 이끌어가는 능력이 탁월합니다.",
        "팀원들의 의견에 귀 기울이고 합리적인 의사결정을 통해 팀 전체의 신뢰를 얻고 있습니다.",
        "주니어 연구원들의 성장을 위해 아낌없이 조언하고 멘토링해주는 모습이 존경스럽습니다.",
        "위기 상황에서도 팀원들을 독려하며 긍정적인 분위기를 유지하는 탁월한 리더십을 발휘합니다.",
    ],
    "mid": [
        "업무 지시는 명확하지만 팀원들의 개인적인 성장이나 역량 개발에는 다소 관심이 적은 편입니다.",
        "기술적 리더십은 강하나 감성적 지원이나 팀원 케어 측면에서 보완이 필요합니다.",
        "결과 지향적 관리 스타일로 성과를 내지만 과정에서 팀원들과의 유대감이 약한 편입니다.",
        "팀을 이끄는 의지는 있으나 구성원들의 다양한 의견을 포용하는 부분에서 개선이 필요합니다.",
    ],
    "low": [
        "지시와 통제 중심의 관리 방식으로 팀원들의 자율성이 억제되는 경향이 있습니다.",
        "비전 제시나 동기부여보다는 단기 성과에만 집중하는 모습이 아쉬우며 팀 사기에 영향을 줍니다.",
        "팀원들의 의견이 잘 반영되지 않아 소통에 어려움을 느끼는 경우가 많습니다.",
        "갈등 상황에서 중재보다는 일방적 결정을 내리는 경우가 많아 팀 분위기가 경직되기도 합니다.",
    ],
}


def generate_all(seed: int = MOCK_CONFIG["seed"]) -> None:
    rng = np.random.default_rng(seed)
    n = MOCK_CONFIG["n_researchers"]
    years = list(range(MOCK_CONFIG["year_range"][0], MOCK_CONFIG["year_range"][1] + 1))

    researchers = _gen_researchers(rng, n)
    papers = _gen_papers(rng, researchers, years)
    patents = _gen_patents(rng, researchers, years)
    projects = _gen_projects(rng, researchers, years)
    evaluations = _gen_evaluations(rng, researchers, years)

    peer_comments = _gen_peer_review_comments(rng, researchers)
    leadership_comments = _gen_leadership_comments(rng, researchers)

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    researchers.to_csv(RAW_DIR / "researchers.csv", index=False, encoding="utf-8-sig")
    papers.to_csv(RAW_DIR / "papers.csv", index=False, encoding="utf-8-sig")
    patents.to_csv(RAW_DIR / "patents.csv", index=False, encoding="utf-8-sig")
    projects.to_csv(RAW_DIR / "projects.csv", index=False, encoding="utf-8-sig")
    evaluations.to_csv(RAW_DIR / "evaluations.csv", index=False, encoding="utf-8-sig")
    peer_comments.to_csv(RAW_DIR / "peer_review_comments.csv", index=False, encoding="utf-8-sig")
    leadership_comments.to_csv(RAW_DIR / "leadership_comments.csv", index=False, encoding="utf-8-sig")


def _gen_researchers(rng: np.random.Generator, n: int) -> pd.DataFrame:
    korean_surnames = ["김", "이", "박", "최", "정", "강", "조", "윤", "장", "임"]
    korean_given = [
        "지훈", "민준", "서연", "지은", "현우", "수빈", "태양", "지혜",
        "성민", "예린", "동현", "나은", "재원", "하늘", "승호", "미래",
        "준혁", "다은", "영우", "소현",
    ]
    names = [
        korean_surnames[i % len(korean_surnames)] + korean_given[i % len(korean_given)]
        for i in range(n)
    ]

    rows = []
    for i in range(n):
        career = int(rng.integers(8, 25))
        birth_year = 2025 - career - int(rng.integers(26, 34))
        edu_weights = [0.05, 0.30, 0.65]  # 학사/석사/박사
        education = rng.choice(["학사", "석사", "박사"], p=edu_weights)
        position = rng.choice(POSITIONS, p=[0.40, 0.35, 0.25])
        department = rng.choice(DEPARTMENTS)
        rows.append({
            "id": f"R{i+1:03d}",
            "name": names[i],
            "department": department,
            "position": position,
            "career_years": career,
            "birth_year": birth_year,
            "education": education,
        })
    return pd.DataFrame(rows)


def _gen_papers(rng: np.random.Generator, researchers: pd.DataFrame, years: list) -> pd.DataFrame:
    rows = []
    for _, r in researchers.iterrows():
        # 경력·직급에 비례한 논문 생산성
        seniority = {"책임연구원": 1.0, "선임연구원": 1.6, "수석연구원": 2.2}[r["position"]]
        base_papers = int(rng.integers(1, 4))
        for year in years:
            n_papers = max(0, int(rng.poisson(base_papers * seniority * 0.6)))
            for _ in range(n_papers):
                citations = int(rng.negative_binomial(3, 0.3))
                is_scie = bool(rng.random() < 0.55)
                is_international = bool(rng.random() < 0.35)
                rows.append({
                    "researcher_id": r["id"],
                    "year": year,
                    "citations": citations,
                    "is_scie": is_scie,
                    "is_international": is_international,
                })
    return pd.DataFrame(rows)


def _gen_patents(rng: np.random.Generator, researchers: pd.DataFrame, years: list) -> pd.DataFrame:
    rows = []
    for _, r in researchers.iterrows():
        seniority = {"책임연구원": 0.5, "선임연구원": 0.9, "수석연구원": 1.4}[r["position"]]
        for year in years:
            n_patents = max(0, int(rng.poisson(seniority * 0.7)))
            for _ in range(n_patents):
                status = rng.choice(["출원", "등록"], p=[0.45, 0.55])
                is_tech_transfer = bool(status == "등록" and rng.random() < 0.20)
                rows.append({
                    "researcher_id": r["id"],
                    "year": year,
                    "status": status,
                    "is_tech_transfer": is_tech_transfer,
                })
    return pd.DataFrame(rows)


def _gen_projects(rng: np.random.Generator, researchers: pd.DataFrame, years: list) -> pd.DataFrame:
    rows = []
    project_counter = 1
    for _, r in researchers.iterrows():
        seniority = {"책임연구원": 0.6, "선임연구원": 1.0, "수석연구원": 1.5}[r["position"]]
        for year in years:
            n_projects = max(0, int(rng.poisson(seniority * 1.2)))
            for _ in range(n_projects):
                role = rng.choice(["주관", "참여"], p=[0.35, 0.65])
                budget = float(rng.lognormal(mean=4.5, sigma=0.8))  # 단위: 백만원
                kpi = float(np.clip(rng.normal(0.82, 0.12), 0.3, 1.0))
                rows.append({
                    "researcher_id": r["id"],
                    "year": year,
                    "project_id": f"P{project_counter:04d}",
                    "role": role,
                    "budget_million": round(budget, 1),
                    "kpi_achievement": round(kpi, 3),
                })
                project_counter += 1
    return pd.DataFrame(rows)


def _grade_from_quality(quality: float) -> str:
    """개인 역량 수준(0~1)을 평가 등급(가~마)으로 변환."""
    if quality > 0.85:
        return "가"
    elif quality > 0.65:
        return "나"
    elif quality > 0.38:
        return "다"
    elif quality > 0.18:
        return "라"
    else:
        return "마"


def _gen_evaluations(rng: np.random.Generator, researchers: pd.DataFrame, years: list) -> pd.DataFrame:
    rows = []
    # 직급별 역량 평균 (수석 > 선임 > 책임)
    quality_means = {"책임연구원": 0.42, "선임연구원": 0.55, "수석연구원": 0.72}
    for _, r in researchers.iterrows():
        seniority = {"책임연구원": 0.7, "선임연구원": 1.0, "수석연구원": 1.3}[r["position"]]
        # 개인 고정 특성 (사람마다 다른 강점)
        eng_base = int(rng.integers(550, 920))
        leadership_base = float(rng.uniform(5.5, 9.5))
        # 연구자 개인 역량 베이스 (연도 간 연속성 유지)
        quality_base = float(np.clip(rng.normal(quality_means[r["position"]], 0.15), 0.0, 1.0))
        for year in years:
            # 연도별 소폭 변화
            english_score = int(np.clip(eng_base + rng.integers(-30, 50), 400, 990))
            overseas = int(rng.poisson(seniority * 1.5))
            intl_papers = int(rng.poisson(seniority * 0.8))
            peer_score = float(np.clip(rng.normal(7.0, 1.2), 3.0, 10.0))
            leadership = float(np.clip(leadership_base + rng.normal(0, 0.3), 3.0, 10.0))
            mentoring = int(rng.poisson(seniority * 0.8))
            intra_collab = int(rng.poisson(seniority * 2.0))
            external_collab = int(rng.poisson(seniority * 1.0))
            training = int(rng.integers(20, 120))
            # 연도별 평가 등급 (개인 역량 베이스 ± 연도 노이즈)
            year_quality = float(np.clip(quality_base + rng.normal(0, 0.08), 0.0, 1.0))
            grade = _grade_from_quality(year_quality)
            # 성과인상율: 등급별 기준율 ± 개인 편차 (표준편차 15 %)
            base_rate = GRADE_MERIT_RATES[grade]
            merit_raise_rate = float(np.clip(
                rng.normal(base_rate, base_rate * 0.15), 0.001, 0.15
            ))
            rows.append({
                "researcher_id": r["id"],
                "year": year,
                "performance_grade": grade,
                "merit_raise_rate": round(merit_raise_rate, 4),
                "english_score": english_score,
                "overseas_months": overseas,
                "international_papers": intl_papers,
                "peer_review_score": round(peer_score, 2),
                "leadership_score": round(leadership, 2),
                "mentoring_count": mentoring,
                "intra_collab_count": intra_collab,
                "external_collab_count": external_collab,
                "training_hours": training,
            })
    return pd.DataFrame(rows)


def _gen_peer_review_comments(rng: np.random.Generator, researchers: pd.DataFrame) -> pd.DataFrame:
    pos_quality = {"책임연구원": 0.35, "선임연구원": 0.55, "수석연구원": 0.75}
    rows = []
    for _, r in researchers.iterrows():
        base = pos_quality[r["position"]]
        quality = float(np.clip(base + rng.normal(0, 0.18), 0.0, 1.0))
        if quality >= 0.60:
            pool = _PEER_TEMPLATES["high"]
        elif quality >= 0.35:
            pool = _PEER_TEMPLATES["high"][:2] + _PEER_TEMPLATES["mid"]
        else:
            pool = _PEER_TEMPLATES["mid"][-1:] + _PEER_TEMPLATES["low"]
        n = int(rng.integers(3, 6))
        indices = rng.choice(len(pool), size=min(n, len(pool)), replace=False)
        for idx in indices:
            rows.append({"researcher_id": r["id"], "comment": pool[int(idx)]})
    return pd.DataFrame(rows)


def _gen_leadership_comments(rng: np.random.Generator, researchers: pd.DataFrame) -> pd.DataFrame:
    pos_quality = {"책임연구원": 0.30, "선임연구원": 0.50, "수석연구원": 0.70}
    rows = []
    for _, r in researchers.iterrows():
        base = pos_quality[r["position"]]
        quality = float(np.clip(base + rng.normal(0, 0.18), 0.0, 1.0))
        if quality >= 0.60:
            pool = _LEADERSHIP_TEMPLATES["high"]
        elif quality >= 0.35:
            pool = _LEADERSHIP_TEMPLATES["high"][:2] + _LEADERSHIP_TEMPLATES["mid"]
        else:
            pool = _LEADERSHIP_TEMPLATES["mid"][-1:] + _LEADERSHIP_TEMPLATES["low"]
        n = int(rng.integers(3, 6))
        indices = rng.choice(len(pool), size=min(n, len(pool)), replace=False)
        for idx in indices:
            rows.append({"researcher_id": r["id"], "comment": pool[int(idx)]})
    return pd.DataFrame(rows)


if __name__ == "__main__":
    generate_all()
    print("가상 데이터 생성 완료 → data/raw/")
