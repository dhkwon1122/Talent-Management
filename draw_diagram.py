"""
Talent Management 시스템 아키텍처 + 워크플로우 다이어그램 생성
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe
from matplotlib import font_manager

# 한글 폰트 등록
_FONT_PATH = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
font_manager.fontManager.addfont(_FONT_PATH)
_PROP = font_manager.FontProperties(fname=_FONT_PATH)
_KO = _PROP.get_name()
matplotlib.rcParams["font.family"] = _KO

fig = plt.figure(figsize=(22, 16), facecolor="#0f1117")
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 22)
ax.set_ylim(0, 16)
ax.axis("off")
ax.set_facecolor("#0f1117")

# ── 색상 팔레트 ──────────────────────────────────────────────
C = {
    "data":    "#1e3a5f",   # 데이터층 (딥블루)
    "proc":    "#1a4a2e",   # 처리층 (딥그린)
    "score":   "#3d2b00",   # 스코어링 (딥오렌지)
    "grade":   "#3b1f4e",   # 등급 (딥퍼플)
    "ui":      "#1f2d3d",   # UI (슬레이트)
    "page":    "#1a2a1a",   # 페이지 (다크그린)
    "cfg":     "#2a1a1a",   # 설정 (다크레드)
    "border_data":  "#4a9eff",
    "border_proc":  "#4adf7f",
    "border_score": "#ff9f4a",
    "border_grade": "#bf7fff",
    "border_ui":    "#7fbfff",
    "border_page":  "#6fcf97",
    "border_cfg":   "#ff7f7f",
    "arrow":   "#888888",
    "arrow_main": "#ffffff",
    "text":    "#ffffff",
    "subtext": "#aaaaaa",
    "highlight": "#ffd700",
}

def box(ax, x, y, w, h, bg, border, radius=0.25, lw=1.5, alpha=0.92):
    fancy = FancyBboxPatch((x, y), w, h,
        boxstyle=f"round,pad=0.0,rounding_size={radius}",
        facecolor=bg, edgecolor=border, linewidth=lw, alpha=alpha, zorder=3)
    ax.add_patch(fancy)

def label(ax, x, y, text, size=9, color="#ffffff", bold=False, ha="center", va="center", zorder=5):
    weight = "bold" if bold else "normal"
    ax.text(x, y, text, fontsize=size, color=color, ha=ha, va=va,
            fontweight=weight, zorder=zorder,
            fontfamily=_KO)

def arrow(ax, x1, y1, x2, y2, color="#888888", lw=1.5, style="->", zorder=2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle=style, color=color, lw=lw,
                        connectionstyle="arc3,rad=0.0"),
        zorder=zorder)

def arrow_curve(ax, x1, y1, x2, y2, color="#888888", lw=1.5, rad=0.2, zorder=2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle="->", color=color, lw=lw,
                        connectionstyle=f"arc3,rad={rad}"),
        zorder=zorder)

def section_label(ax, x, y, text, color):
    ax.text(x, y, text, fontsize=8, color=color, ha="left", va="center",
            fontweight="bold", zorder=6, style="italic")

# ═══════════════════════════════════════════════════════════════
# 제목
# ═══════════════════════════════════════════════════════════════
label(ax, 11, 15.4, "Talent Management System", size=18, bold=True, color="#ffffff")
label(ax, 11, 14.95, "코드 아키텍처 & 데이터 워크플로우", size=11, color="#aaaaaa")

# ═══════════════════════════════════════════════════════════════
# 층 구분 배경
# ═══════════════════════════════════════════════════════════════
layer_alpha = 0.18

# Layer 1 - Raw Data
bg1 = FancyBboxPatch((0.3, 11.4), 4.4, 3.0, boxstyle="round,pad=0",
    facecolor=C["border_data"], edgecolor="none", alpha=0.08, zorder=1)
ax.add_patch(bg1)

# Layer 2 - Processing
bg2 = FancyBboxPatch((5.0, 9.8), 5.2, 4.6, boxstyle="round,pad=0",
    facecolor=C["border_proc"], edgecolor="none", alpha=0.08, zorder=1)
ax.add_patch(bg2)

# Layer 3 - Scoring
bg3 = FancyBboxPatch((10.5, 9.8), 5.2, 4.6, boxstyle="round,pad=0",
    facecolor=C["border_score"], edgecolor="none", alpha=0.08, zorder=1)
ax.add_patch(bg3)

# Layer 4 - UI
bg4 = FancyBboxPatch((16.1, 9.8), 5.6, 4.6, boxstyle="round,pad=0",
    facecolor=C["border_ui"], edgecolor="none", alpha=0.08, zorder=1)
ax.add_patch(bg4)

# ═══════════════════════════════════════════════════════════════
# 층 라벨
# ═══════════════════════════════════════════════════════════════
section_label(ax, 0.35, 14.6,  "① RAW DATA", C["border_data"])
section_label(ax, 5.05, 14.6,  "② DATA PROCESSING", C["border_proc"])
section_label(ax, 10.55, 14.6, "③ SCORING ENGINE", C["border_score"])
section_label(ax, 16.15, 14.6, "④ VISUALIZATION / UI", C["border_ui"])

# ═══════════════════════════════════════════════════════════════
# ① RAW DATA 층  (x: 0.3~4.7, y: 11.5~14.4)
# ═══════════════════════════════════════════════════════════════
csv_files = [
    ("researchers.csv", "👤 연구원 기본정보"),
    ("papers.csv",      "📄 논문 데이터"),
    ("patents.csv",     "💡 특허 데이터"),
    ("projects.csv",    "📁 과제 데이터"),
    ("evaluations.csv", "⭐ 평가 등급·지표"),
    ("comments.csv",    "💬 동료/리더십 코멘트"),
]
for i, (fname, desc) in enumerate(csv_files):
    yi = 14.1 - i * 0.45
    box(ax, 0.45, yi - 0.18, 4.0, 0.38, C["data"], C["border_data"], radius=0.12, lw=1.2)
    label(ax, 2.45, yi + 0.01, f"{fname}", size=8, bold=True, color=C["border_data"])
    label(ax, 2.45, yi - 0.13, desc, size=7, color=C["subtext"])

# generator.py 박스
box(ax, 0.45, 11.45, 4.0, 0.52, "#1a1a2e", C["border_data"], radius=0.15, lw=1.5)
label(ax, 2.45, 11.77, "generator.py", size=9, bold=True, color=C["border_data"])
label(ax, 2.45, 11.57, "가상 데이터 자동 생성 (seed=42)", size=7.5, color=C["subtext"])

# ═══════════════════════════════════════════════════════════════
# ② DATA PROCESSING 층  (x: 5.0~10.2)
# ═══════════════════════════════════════════════════════════════

# loader.py 메인
box(ax, 5.15, 12.7, 4.9, 1.65, C["proc"], C["border_proc"], radius=0.2, lw=2.0)
label(ax, 7.60, 14.12, "loader.py", size=10, bold=True, color=C["border_proc"])

# 내부 함수들
funcs_loader = [
    ("load_raw()", "CSV 파일 로드"),
    ("build_feature_table()", "집계 피처 테이블 생성"),
    ("_calc_grade_score()", "등급→점수 가중 집계 ★"),
    ("_calc_growth_rate()", "KPI 성장률 계산"),
    ("_calc_h_index()", "h-index 계산"),
]
for i, (fn, desc) in enumerate(funcs_loader):
    yi = 13.82 - i * 0.30
    ax.plot([5.30, 9.90], [yi - 0.05, yi - 0.05], color="#2a6a3a", lw=0.5, alpha=0.4, zorder=4)
    label(ax, 5.45, yi + 0.04, f"• {fn}", size=7.5, bold=False, color="#7fffb0", ha="left")
    label(ax, 9.90, yi + 0.04, desc, size=7, color=C["subtext"], ha="right")

# Feature Table (중간 산출물)
box(ax, 5.15, 11.55, 4.9, 0.95, "#0d2b0d", C["border_proc"], radius=0.18, lw=1.5, alpha=0.9)
label(ax, 7.60, 12.28, "Feature Table (per researcher)", size=9, bold=True, color=C["border_proc"])
features_list = "논문수·피인용·h-index · 등록특허 · 주관과제수 · 예산 · KPI · grade_score · 영어점수 · 해외파견 · 협업건수 · 교육시간"
label(ax, 7.60, 12.02, features_list, size=6.5, color=C["subtext"])

# _ensure_raw_data
box(ax, 5.15, 11.0, 4.9, 0.42, "#0a1a0a", C["border_proc"], radius=0.12, lw=1.0)
label(ax, 7.60, 11.24, "_ensure_raw_data()  →  performance_grade 컬럼 확인 후 자동 재생성", size=7, color="#aaffaa")

# ═══════════════════════════════════════════════════════════════
# ③ SCORING ENGINE  (x: 10.5~15.7)
# ═══════════════════════════════════════════════════════════════

# calculator.py
box(ax, 10.65, 13.15, 4.7, 1.2, C["score"], C["border_score"], radius=0.2, lw=2.0)
label(ax, 13.00, 14.12, "calculator.py", size=10, bold=True, color=C["border_score"])
dims = ["전문성  (논문·특허)", "업무성과 (★등급50%+KPI25%+과제15%+예산10%)",
        "리더십  (동료평가·멘토링)", "글로벌역량 (영어·해외·국제논문)",
        "협업네트워크 (사내·외부협력)", "성장잠재력 (KPI증감·교육·효율)"]
for i, d in enumerate(dims):
    yi = 13.88 - i * 0.225
    col = C["highlight"] if "★" in d else "#ffcf7f"
    label(ax, 10.80, yi, f"• {d}", size=7, color=col, ha="left")

# normalizer.py
box(ax, 10.65, 12.05, 4.7, 0.85, C["score"], C["border_score"], radius=0.18, lw=1.8)
label(ax, 13.00, 12.68, "normalizer.py", size=9.5, bold=True, color=C["border_score"])
label(ax, 13.00, 12.42, "Min-Max + √변환  →  0~100점 정규화", size=7.5, color="#ffc070")
label(ax, 13.00, 12.20, "normalize( ) · _minmax_normalize( ) · _rank_normalize( )", size=7, color=C["subtext"])

# text_scorer.py
box(ax, 10.65, 11.0, 4.7, 0.82, C["grade"], "#bf7fff", radius=0.18, lw=1.8)
label(ax, 13.00, 11.63, "text_scorer.py", size=9.5, bold=True, color="#bf7fff")
label(ax, 13.00, 11.37, "Google Gemini API  /  키워드 폴백", size=7.5, color="#d0a0ff")
label(ax, 13.00, 11.15, "동료평가 코멘트 → 0~10점  (캐시: text_scores.json)", size=7, color=C["subtext"])

# config.py (중앙 공통)
box(ax, 10.65, 9.9, 4.7, 0.82, C["cfg"], C["border_cfg"], radius=0.18, lw=1.8)
label(ax, 13.00, 10.53, "config.py", size=9.5, bold=True, color=C["border_cfg"])
label(ax, 13.00, 10.27, "GRADE_SCORES {가:100 나:80 다:60 라:40 마:20}", size=7.5, color=C["highlight"])
label(ax, 13.00, 10.05, "SCORING_WEIGHTS · DIMENSIONS · DIMENSION_COLORS · MOCK_CONFIG", size=7, color=C["subtext"])

# ═══════════════════════════════════════════════════════════════
# ④ VISUALIZATION / UI  (x: 16.1~21.7)
# ═══════════════════════════════════════════════════════════════

# radar.py
box(ax, 16.25, 13.45, 5.1, 0.92, C["ui"], C["border_ui"], radius=0.18, lw=1.8)
label(ax, 18.80, 14.12, "radar.py", size=9.5, bold=True, color=C["border_ui"])
label(ax, 18.80, 13.85, "make_radar_single()  · make_radar_compare()", size=7.5, color="#a0cfff")
label(ax, 18.80, 13.63, "Plotly Scatterpolar  →  0~100 방사형 차트", size=7, color=C["subtext"])

# components.py
box(ax, 16.25, 12.35, 5.1, 0.92, C["ui"], C["border_ui"], radius=0.18, lw=1.8)
label(ax, 18.80, 13.02, "components.py", size=9.5, bold=True, color=C["border_ui"])
label(ax, 18.80, 12.75, "score_badge() · researcher_info_card()", size=7.5, color="#a0cfff")
label(ax, 18.80, 12.53, "overall_score_metric() · heatmap_table()", size=7, color=C["subtext"])

# Pages
pages = [
    ("pages/1_개인_프로필.py",  "레이더차트 · 차원점수 배지\n★ 연도별 평가등급 이력 표시"),
    ("pages/2_인재_비교.py",    "다중 선택 레이더 오버레이\n히트맵 비교 테이블"),
    ("pages/3_전체_현황.py",    "부서별 히트맵 · 종합점수 순위\n차원별 분포 박스플롯"),
]
for i, (pname, pdesc) in enumerate(pages):
    yi = 12.05 - i * 0.72
    box(ax, 16.25, yi - 0.36, 5.1, 0.62, C["page"], C["border_page"], radius=0.15, lw=1.5)
    short = pname.split("/")[1]
    label(ax, 16.45, yi - 0.02, short, size=8, bold=True, color=C["border_page"], ha="left")
    label(ax, 16.45, yi - 0.22, pdesc, size=6.8, color=C["subtext"], ha="left")

# ═══════════════════════════════════════════════════════════════
# 워크플로우 화살표 (메인 흐름)
# ═══════════════════════════════════════════════════════════════

# CSV → loader (여러 개의 화살표)
for i in range(6):
    yi = 13.925 - i * 0.45
    arrow(ax, 4.45, yi, 5.15, min(yi, 14.35), color=C["border_data"], lw=1.2)

# generator → CSV
arrow(ax, 2.45, 11.45, 2.45, 11.15, color="#6699ff", lw=1.5)
ax.text(2.47, 11.28, "자동생성", size=6.5, color="#6699ff", ha="left", va="center", zorder=6)

# loader → feature table
arrow(ax, 7.60, 12.70, 7.60, 12.50, color=C["border_proc"], lw=2.0)

# feature table → calculator
arrow(ax, 10.05, 12.02, 10.65, 13.30, color=C["border_proc"], lw=2.0)

# calculator → normalizer
arrow(ax, 13.00, 13.15, 13.00, 12.90, color=C["border_score"], lw=2.0)

# normalizer → radar/components
arrow(ax, 15.35, 12.62, 16.25, 13.75, color=C["border_score"], lw=2.0)
arrow(ax, 15.35, 12.40, 16.25, 12.65, color=C["border_score"], lw=2.0)

# text_scorer → calculator (점선 느낌)
ax.annotate("", xy=(10.65, 11.65), xytext=(10.65, 11.42),
    arrowprops=dict(arrowstyle="->", color="#bf7fff", lw=1.5,
                    connectionstyle="arc3,rad=0.0"), zorder=4)
ax.plot([13.00, 13.00], [11.82, 13.15], color="#bf7fff", lw=1.0, linestyle="--", alpha=0.6, zorder=2)

# config → calculator, normalizer, loader (점선)
ax.plot([13.00, 13.00], [10.72, 11.0], color="#ff7f7f", lw=1.0, linestyle=":", alpha=0.7, zorder=2)
ax.plot([11.0, 10.8], [10.35, 11.0], color="#ff7f7f", lw=1.0, linestyle=":", alpha=0.5, zorder=2)
label(ax, 11.6, 10.68, "weights·grades", size=6, color="#ff9999")

# components/radar → pages
arrow(ax, 18.80, 12.35, 18.80, 11.71, color=C["border_ui"], lw=1.8)
arrow(ax, 18.80, 11.3, 18.80, 11.0, color=C["border_ui"], lw=1.5)
arrow(ax, 18.80, 10.6, 18.80, 10.3, color=C["border_ui"], lw=1.5)

# ═══════════════════════════════════════════════════════════════
# 하단: 데이터 파이프라인 요약 플로우
# ═══════════════════════════════════════════════════════════════
box(ax, 0.4, 7.5, 21.2, 2.1, "#111111", "#333333", radius=0.3, lw=1.0, alpha=0.95)
label(ax, 11.0, 9.38, "데이터 파이프라인  (End-to-End)", size=10, bold=True, color="#ffffff")

pipe_steps = [
    ("Raw CSVs\n(7종)", "#4a9eff"),
    ("feature_table\n집계·병합", "#4adf7f"),
    ("grade_score\n등급→가중평균", "#bf7fff"),
    ("raw_scores\n6차원 가중합", "#ff9f4a"),
    ("normalized\n0~100 정규화", "#ff9f4a"),
    ("text_scores\nLLM 코멘트분석", "#bf7fff"),
    ("TalentScore\n최종 점수", "#ffd700"),
    ("Streamlit\n대시보드", "#7fbfff"),
]
n = len(pipe_steps)
xs = [1.2 + i * (19.8 / (n - 1)) for i in range(n)]
for i, (step, col) in enumerate(pipe_steps):
    x = xs[i]
    box(ax, x - 1.0, 7.7, 2.0, 1.55, "#1a1a1a", col, radius=0.2, lw=1.8)
    label(ax, x, 8.6, step, size=8, bold=True, color=col)
    if i < n - 1:
        ax.annotate("", xy=(xs[i+1] - 1.0, 8.48), xytext=(x + 1.0, 8.48),
            arrowprops=dict(arrowstyle="->", color="#666666", lw=1.8), zorder=5)

# ═══════════════════════════════════════════════════════════════
# 범례
# ═══════════════════════════════════════════════════════════════
legend_items = [
    ("#4a9eff", "데이터 레이어"),
    ("#4adf7f", "처리 레이어"),
    ("#ff9f4a", "스코어링 레이어"),
    ("#bf7fff", "LLM / 등급"),
    ("#7fbfff", "UI 레이어"),
    ("#ffd700", "★ 신규: 평가등급 점수화"),
]
for i, (col, lbl) in enumerate(legend_items):
    x = 0.6 + i * 3.65
    ax.add_patch(mpatches.Rectangle((x, 6.85), 0.35, 0.28,
        facecolor=col, edgecolor="none", alpha=0.85, zorder=5))
    label(ax, x + 0.52, 6.99, lbl, size=7.5, color="#cccccc", ha="left")

plt.tight_layout(pad=0)
plt.savefig("architecture_diagram.png", dpi=150, bbox_inches="tight",
            facecolor="#0f1117", edgecolor="none")
print("저장 완료: architecture_diagram.png")
