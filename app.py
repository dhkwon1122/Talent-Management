"""
인재 역량 대시보드 메인 진입점.
사이드바에서 페이지를 선택하거나 Streamlit 멀티페이지 네비게이션을 사용한다.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

import streamlit as st

st.set_page_config(
    page_title="인재 역량 대시보드",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🔬 연구소 인재 역량 대시보드")
st.markdown(
    """
    리더급 후보 인재의 **6개 역량 차원**을 정량화하여 시각화합니다.

    | 차원 | 주요 지표 |
    |------|-----------|
    | 전문성 | 논문 수 · 피인용 수 · h-index · 등록 특허 수 |
    | 업무성과 | 주관 과제 수 · 관리 예산 · KPI 달성률 |
    | 리더십 | 동료 평가 · 멘토링 · 과제 리더 경험 |
    | 글로벌역량 | 어학 점수 · 해외 파견 · 국제 공동 연구 |
    | 협업네트워크 | 사내 협업 · 외부기관 협력 · 동료 평가 |
    | 성장잠재력 | KPI 성장 추이 · 교육 이수 · 성취 효율성 |

    ---
    왼쪽 사이드바에서 원하는 페이지를 선택하세요.
    """
)
