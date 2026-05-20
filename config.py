from dataclasses import dataclass, field
from typing import Dict

DIMENSIONS = [
    "전문성",
    "업무성과",
    "리더십",
    "글로벌역량",
    "협업네트워크",
    "성장잠재력",
]

# 업무성과 평가 등급 점수 (가=최고, 마=최저)
GRADE_SCORES: Dict[str, float] = {
    "가": 100.0,
    "나": 80.0,
    "다": 60.0,
    "라": 40.0,
    "마": 20.0,
}

# 각 차원별 세부 지표 가중치 (합계 = 1.0)
SCORING_WEIGHTS: Dict[str, Dict[str, float]] = {
    "전문성": {
        "total_papers": 0.30,
        "total_citations": 0.30,
        "h_index": 0.20,
        "registered_patents": 0.20,
    },
    "업무성과": {
        "grade_score": 0.50,           # 연도별 평가 등급 가중 평균
        "avg_kpi_achievement": 0.25,
        "lead_project_count": 0.15,
        "total_budget_managed": 0.10,
    },
    "리더십": {
        "leadership_peer_score": 0.20,
        "leadership_text_score": 0.30,
        "mentoring_count": 0.25,
        "lead_project_count": 0.25,
    },
    "글로벌역량": {
        "english_score_norm": 0.30,
        "overseas_months": 0.30,
        "international_papers": 0.40,
    },
    "협업네트워크": {
        "intra_collab_count": 0.25,
        "external_collab_count": 0.25,
        "peer_review_score": 0.10,
        "peer_review_text_score": 0.40,
    },
    "성장잠재력": {
        "performance_growth_rate": 0.50,
        "annual_training_hours": 0.30,
        "achievement_efficiency": 0.20,
    },
}

# 차원별 레이더 차트 색상
DIMENSION_COLORS = {
    "전문성": "#4C72B0",
    "업무성과": "#DD8452",
    "리더십": "#55A868",
    "글로벌역량": "#C44E52",
    "협업네트워크": "#8172B3",
    "성장잠재력": "#937860",
}

# 비교 차트용 팔레트
COMPARISON_PALETTE = [
    "#4C72B0", "#DD8452", "#55A868", "#C44E52",
    "#8172B3", "#937860", "#DA8BC3", "#8C8C8C",
]

# 직급 정의 (리더 후보 대상)
POSITIONS = ["책임연구원", "선임연구원", "수석연구원"]
DEPARTMENTS = ["AI연구팀", "소재연구팀", "시스템공학팀", "바이오팀", "에너지연구팀"]

# 가상 데이터 생성 설정
MOCK_CONFIG = {
    "n_researchers": 20,
    "year_range": (2018, 2025),
    "seed": 42,
}
