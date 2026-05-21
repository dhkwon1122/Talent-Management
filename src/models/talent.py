from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Researcher:
    id: str
    name: str
    department: str
    position: str
    career_years: int
    birth_year: int
    education: str  # 학사/석사/박사


@dataclass
class PaperRecord:
    researcher_id: str
    year: int
    citations: int
    is_scie: bool
    is_international: bool


@dataclass
class PatentRecord:
    researcher_id: str
    year: int
    status: str       # 출원 / 등록
    is_tech_transfer: bool


@dataclass
class ProjectRecord:
    researcher_id: str
    year: int
    project_id: str
    role: str         # 주관 / 참여
    budget_million: float
    kpi_achievement: float  # 0.0 ~ 1.0


@dataclass
class EvaluationRecord:
    researcher_id: str
    year: int
    performance_grade: str      # 업무성과 평가 등급 (가/나/다/라/마)
    english_score: int          # TOEIC 기준 (0~990)
    overseas_months: int        # 누적 해외 파견 기간
    international_papers: int   # 국제 공동 연구 논문 수
    peer_review_score: float    # 동료 평가 (0~10)
    leadership_score: float     # 리더십 평가 (0~10)
    mentoring_count: int        # 멘토링한 후배 수 (누적)
    intra_collab_count: int     # 사내 타팀 협업 과제 수
    external_collab_count: int  # 외부기관 협력 건수
    training_hours: int         # 연간 교육 이수 시간


@dataclass
class TalentScore:
    researcher_id: str
    전문성: float
    업무성과: float
    리더십: float
    글로벌역량: float
    협업네트워크: float
    성장잠재력: float

    def to_dict(self) -> dict:
        return {
            "researcher_id": self.researcher_id,
            "전문성": self.전문성,
            "업무성과": self.업무성과,
            "리더십": self.리더십,
            "글로벌역량": self.글로벌역량,
            "협업네트워크": self.협업네트워크,
            "성장잠재력": self.성장잠재력,
        }
