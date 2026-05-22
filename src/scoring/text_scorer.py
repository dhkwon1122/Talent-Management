"""
LLM 기반 정성 데이터 정량화 모듈.
피어리뷰 및 리더십 다면진단 코멘트를 LLM API로 분석해 0-10 점수로 변환한다.
결과는 data/processed/text_scores.json에 캐시되므로 API는 최초 1회만 호출된다.
캐시를 초기화하려면 해당 파일을 삭제하면 된다.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
사내 API 전환 시 수정이 필요한 위치는 [GEMINI] 주석으로 표시되어 있다.
각 항목 아래 '→ 사내 API:' 주석에 교체 방법이 설명되어 있다.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
import json
import os
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parents[2]

PROCESSED_DIR = ROOT / "data" / "processed"
CACHE_FILE = PROCESSED_DIR / "text_scores.json"


def _load_dotenv() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip())


_load_dotenv()

_COLLABORATION_PROMPT = """당신은 연구소 HR 전문가입니다. 다음 동료 평가 코멘트를 읽고 해당 연구원의 협업 능력을 평가해주세요.

평가 기준:
- 팀워크와 적극적인 협력 정신
- 원활한 소통 및 정보 공유
- 팀 기여도와 네트워크 구축 능력
- 갈등 해결 및 조율 능력

코멘트:
{comments}

위 기준에 따라 0-10점(소수점 첫째자리)으로 평가하세요.
반드시 다음 JSON 형식으로만 응답하세요 (다른 텍스트 없이):
{{"score": <숫자>, "reasoning": "<한 문장 근거>"}}"""

_LEADERSHIP_PROMPT = """당신은 연구소 HR 전문가입니다. 다음 리더십 다면진단 코멘트를 읽고 해당 연구원의 리더십을 평가해주세요.

평가 기준:
- 팀원 역량 개발 및 멘토링
- 명확한 방향 제시와 의사결정 능력
- 구성원 동기부여와 팀 분위기 조성
- 갈등 중재와 포용적 리더십

코멘트:
{comments}

위 기준에 따라 0-10점(소수점 첫째자리)으로 평가하세요.
반드시 다음 JSON 형식으로만 응답하세요 (다른 텍스트 없이):
{{"score": <숫자>, "reasoning": "<한 문장 근거>"}}"""


def score_all_comments(
    peer_df: pd.DataFrame | None,
    leadership_df: pd.DataFrame | None,
) -> dict:
    """
    Returns:
        {
            "peer_review_text_score": {"R001": 7.5, ...},
            "leadership_text_score": {"R001": 8.0, ...},
        }
    캐시 파일이 있으면 API 호출 없이 즉시 반환한다.
    """
    if CACHE_FILE.exists():
        with open(CACHE_FILE, encoding="utf-8") as f:
            return json.load(f)

    # ─────────────────────────────────────────────
    # [GEMINI] 환경변수: API 키 읽기
    # → 사내 API: 아래 변수명을 사내 환경변수명으로 교체
    #   예) api_key = os.environ.get("INTERNAL_LLM_API_KEY", "")
    #   .env 파일에도 동일하게 변경: INTERNAL_LLM_API_KEY=<발급받은 키>
    # ─────────────────────────────────────────────
    api_key = os.environ.get("GEMINI_API_KEY", "") or os.environ.get("GOOGLE_API_KEY", "")

    if not api_key:
        # [GEMINI] 미설정 안내 메시지 — 환경변수명 교체 시 함께 수정
        print("[text_scorer] API 키 미설정 — 키워드 기반 로컬 점수 사용 (테스트 모드)")
        scores = _local_scores(peer_df, leadership_df)
    else:
        try:
            # ─────────────────────────────────────────────
            # [GEMINI] 패키지 임포트 및 클라이언트 초기화
            # → 사내 API 유형에 따라 아래 중 하나로 교체:
            #
            #   [OpenAI 호환 REST 방식]
            #   import requests
            #   client = {"url": "http://사내서버주소/v1/chat/completions",
            #             "headers": {"Authorization": f"Bearer {api_key}",
            #                         "Content-Type": "application/json"}}
            #
            #   [OpenAI SDK + 커스텀 base_url 방식]
            #   from openai import OpenAI
            #   client = OpenAI(api_key=api_key, base_url="http://사내서버주소/v1")
            #
            #   [사내 전용 SDK 방식]
            #   from internal_llm_sdk import Client
            #   client = Client(api_key=api_key, endpoint="http://사내서버주소")
            # ─────────────────────────────────────────────
            from google import genai
            client = genai.Client(api_key=api_key)

            scores = {}
            if peer_df is not None and not peer_df.empty:
                print("[text_scorer] 협업네트워크 코멘트 분석 중...")
                scores["peer_review_text_score"] = _score_dimension(
                    client, peer_df, _COLLABORATION_PROMPT
                )
            if leadership_df is not None and not leadership_df.empty:
                print("[text_scorer] 리더십 코멘트 분석 중...")
                scores["leadership_text_score"] = _score_dimension(
                    client, leadership_df, _LEADERSHIP_PROMPT
                )
        except Exception as e:
            # [GEMINI] 오류 메시지 — 사내 API로 교체 시 문구 수정
            print(f"[text_scorer] API 오류, 로컬 키워드 점수로 전환: {type(e).__name__}")
            scores = _local_scores(peer_df, leadership_df)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(scores, f, ensure_ascii=False, indent=2)

    return scores


def _score_dimension(client, df: pd.DataFrame, prompt_template: str) -> dict:
    results = {}
    for researcher_id, group in df.groupby("researcher_id"):
        comments_text = "\n".join(f"• {c}" for c in group["comment"].tolist())
        prompt = prompt_template.format(comments=comments_text)
        # [GEMINI] _call_gemini → 사내 API: 아래 함수명도 함께 변경 권장 (예: _call_internal)
        results[str(researcher_id)] = _call_gemini(client, prompt)
    return results


def _call_gemini(client, prompt: str) -> float:
    """
    [GEMINI] 이 함수 전체가 교체 대상이다.
    사내 API 방식에 따른 교체 예시:

    [OpenAI 호환 REST 방식]
    ┌─────────────────────────────────────────────────────────────
    │ import requests
    │ def _call_internal(client: dict, prompt: str) -> float:
    │     body = {
    │         "model": "사내모델명",          # ← 사내 모델명으로 교체
    │         "messages": [{"role": "user", "content": prompt}],
    │         "max_tokens": 256,
    │     }
    │     resp = requests.post(client["url"], headers=client["headers"], json=body, timeout=30)
    │     resp.raise_for_status()
    │     raw = resp.json()["choices"][0]["message"]["content"].strip()
    │     # 이하 JSON 파싱 로직은 동일하게 유지
    └─────────────────────────────────────────────────────────────

    [OpenAI SDK + 커스텀 base_url 방식]
    ┌─────────────────────────────────────────────────────────────
    │ def _call_internal(client, prompt: str) -> float:
    │     resp = client.chat.completions.create(
    │         model="사내모델명",             # ← 사내 모델명으로 교체
    │         messages=[{"role": "user", "content": prompt}],
    │         max_tokens=256,
    │     )
    │     raw = resp.choices[0].message.content.strip()
    │     # 이하 JSON 파싱 로직은 동일하게 유지
    └─────────────────────────────────────────────────────────────
    """
    try:
        # [GEMINI] API 호출부 — 모델명·메서드·응답 구조가 모두 Gemini 전용
        # → 사내 API: 위 docstring의 예시 코드로 교체
        response = client.models.generate_content(
            model="gemini-2.0-flash",   # [GEMINI] 모델명 → 사내 모델명으로 교체
            contents=prompt,            # [GEMINI] 파라미터명 → 사내 API 스펙에 맞게 교체
        )
        # [GEMINI] 응답 접근 방식 → 사내 API: response 구조에 맞게 수정
        # 예) OpenAI 호환: raw = response.choices[0].message.content.strip()
        raw = response.text.strip()

        # JSON 코드블록 제거 (```json ... ``` 형식 대응) — 사내 API에서도 유지
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        # 이하 파싱 로직은 사내 API 교체 후에도 그대로 사용 가능
        try:
            data = json.loads(raw)
            return round(float(data["score"]), 1)
        except (KeyError, ValueError):
            m = re.search(r'"score"\s*:\s*(\d+(?:\.\d+)?)', raw)
            if m:
                return round(float(m.group(1)), 1)
            return 5.0
    except Exception as e:
        # 할당량 초과는 상위로 전파 → _local_scores 폴백 트리거
        if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
            raise
        print(f"[text_scorer] 호출 실패: {e}")
        return 5.0


# 긍정/부정/중립 키워드 — 가상 코멘트 템플릿에서 추출한 특징어
_HIGH_KW = ["훌륭", "탁월", "아낌없이", "능숙하게", "성공적으로", "경계 없이", "존경", "핵심 역할", "원활히"]
_LOW_KW  = ["소극적", "일방적", "억제", "경직", "부족합니다", "부족하다", "낮아", "어려움을 겪"]
_MID_KW  = ["아쉽", "개선이 필요", "경향이 있", "불균형", "다소", "약한 편"]


def _local_score_comment(comment: str) -> float:
    """단일 코멘트를 키워드로 채점해 0-10 점수를 반환한다."""
    high = sum(1 for kw in _HIGH_KW if kw in comment)
    low  = sum(1 for kw in _LOW_KW  if kw in comment)
    if high > 0 and low == 0:
        return min(10.0, 7.5 + high * 0.5)
    if low > 0 and high == 0:
        return max(1.0, 4.0 - low * 0.8)
    return 5.5  # 혼재 또는 중립


def _local_scores(peer_df, leadership_df) -> dict:
    """
    API 없이 코멘트 텍스트를 키워드로 분석해 테스트용 점수를 생성한다.
    실제 API 연동 후에는 사용되지 않는다 (캐시가 우선).
    """
    scores = {}
    for key, df in [("peer_review_text_score", peer_df), ("leadership_text_score", leadership_df)]:
        if df is None or df.empty:
            continue
        dim_scores = {}
        for rid, group in df.groupby("researcher_id"):
            comment_scores = [_local_score_comment(c) for c in group["comment"]]
            dim_scores[str(rid)] = round(sum(comment_scores) / len(comment_scores), 1)
        scores[key] = dim_scores
    return scores
