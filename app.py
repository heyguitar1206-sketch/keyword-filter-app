import streamlit as st
import pandas as pd
import json
import os
import re
import io

# ──────────────────────────────────────────────
# 페이지 설정
# ──────────────────────────────────────────────
st.set_page_config(page_title="초코라떼 키워드서칭프로", page_icon="☕", layout="wide")

# ──────────────────────────────────────────────
# 커스텀 CSS
# ──────────────────────────────────────────────
st.markdown("""
<style>
/* ── 전역 ── */
#MainMenu, footer {visibility: hidden;}
section.main .block-container {
    max-width: 1100px;
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

/* ── 헤더 카드 ── */
.header-card {
    background: linear-gradient(135deg, #e8eeff 0%, #f4f1ff 100%);
    border-radius: 16px;
    padding: 28px 36px;
    margin-bottom: 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.header-card .title-area h1 {
    margin: 0;
    font-size: 28px;
    font-weight: 800;
    color: #1a1a2e;
}
.header-card .title-area p {
    margin: 4px 0 0 0;
    font-size: 14px;
    color: #6b7280;
}
.header-card .version-badge {
    background: #fff;
    border: 1.5px solid #4f6df5;
    color: #4f6df5;
    font-size: 12px;
    font-weight: 600;
    padding: 6px 14px;
    border-radius: 20px;
    white-space: nowrap;
}

/* ── 파일 업로드 영역 스타일 ── */
div[data-testid="stFileUploader"] {
    border: 2.5px dashed #a5b4fc;
    border-radius: 16px;
    padding: 20px;
    background: #fafaff;
    margin-bottom: 24px;
    transition: border-color 0.2s;
}
div[data-testid="stFileUploader"]:hover {
    border-color: #4f6df5;
}

/* ── 파일 로드 완료 배지 ── */
.file-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: #f0fdf4;
    border: 1px solid #86efac;
    color: #166534;
    font-size: 14px;
    font-weight: 500;
    padding: 8px 16px;
    border-radius: 10px;
    margin-bottom: 20px;
}

/* ── 프리셋 버튼 스타일 ── */
div[data-testid="stHorizontalBlock"] button[kind="secondary"] {
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 6px 20px !important;
    border: 1.5px solid #d1d5db !important;
    background: #fff !important;
    color: #374151 !important;
    transition: all 0.15s !important;
}
div[data-testid="stHorizontalBlock"] button[kind="secondary"]:hover {
    border-color: #4f6df5 !important;
    color: #4f6df5 !important;
    background: #eef2ff !important;
}

/* ── 분석실행 버튼 ── */
div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #4f6df5 0%, #6366f1 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 12px !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    padding: 12px 0 !important;
    box-shadow: 0 4px 14px rgba(79,109,245,0.3) !important;
    transition: transform 0.1s, box-shadow 0.1s !important;
}
div.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(79,109,245,0.4) !important;
}

/* ── 결과 카드 ── */
.result-header {
    font-size: 22px;
    font-weight: 800;
    color: #1a1a2e;
    margin-bottom: 12px;
}
.result-count {
    color: #4f6df5;
}

/* ── 데이터프레임 ── */
div[data-testid="stDataFrame"] {
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    overflow: visible;
}

/* ── 다운로드 버튼 ── */
div.stDownloadButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    border: 1.5px solid #4f6df5 !important;
    color: #4f6df5 !important;
    background: #fff !important;
}
div.stDownloadButton > button:hover {
    background: #eef2ff !important;
}

/* ── 설정 expander ── */
div[data-testid="stExpander"] {
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    overflow: hidden;
}

/* ── 메시지 영역 ── */
.empty-state {
    text-align: center;
    padding: 40px 20px;
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    color: #9ca3af;
    font-size: 15px;
    margin-top: 8px;
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# 프리셋 파일 관리
# ──────────────────────────────────────────────
PRESET_FILE = "presets.json"
PRESET_VERSION = 3

EMPTY_FILTERS = {
    "브랜드키워드": "전체",
    "쇼핑성키워드": "전체",
    "계절성": "전체",
    "작년검색량_lo": 0,
    "작년검색량_hi": 0,
    "작년최대검색월": [],
    "피크월검색량_lo": 0,
    "피크월검색량_hi": 0,
    "쿠팡해외배송비율_lo": 0.0,
    "쿠팡해외배송비율_hi": 0.0,
    "쿠팡평균가_lo": 0,
    "쿠팡평균가_hi": 0,
    "쿠팡총리뷰수_lo": 0,
    "쿠팡총리뷰수_hi": 0,
}

DEFAULT_PRESETS = {
    "version": PRESET_VERSION,
    "presets": [
        {"name": "프리셋 1", "filters": dict(EMPTY_FILTERS)},
        {"name": "프리셋 2", "filters": dict(EMPTY_FILTERS)},
        {"name": "프리셋 3", "filters": dict(EMPTY_FILTERS)},
        {"name": "프리셋 4", "filters": dict(EMPTY_FILTERS)},
        {"name": "프리셋 5", "filters": dict(EMPTY_FILTERS)},
    ],
}


def load_presets():
    if os.path.exists(PRESET_FILE):
        try:
            with open(PRESET_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data.get("version") == PRESET_VERSION:
                return data
        except Exception:
            pass
    return json.loads(json.dumps(DEFAULT_PRESETS))


def save_presets(data):
    with open(PRESET_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ──────────────────────────────────────────────
# 유틸 함수
# ──────────────────────────────────────────────
def safe_int(v, default=0):
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def safe_float(v, default=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def get_preset_name(idx):
    try:
        return st.session_state["presets"]["presets"][idx]["name"]
    except Exception:
        return f"프리셋 {idx+1}"


def get_preset_filters(idx):
    try:
        f = st.session_state["presets"]["presets"][idx]["filters"]
        merged = dict(EMPTY_FILTERS)
        merged.update(f)
        return merged
    except Exception:
        return dict(EMPTY_FILTERS)


# ──────────────────────────────────────────────
# 엑셀 로딩 (1회 읽기로 최적화)
# ──────────────────────────────────────────────
def is_header_text(val):
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return False
    s = str(val).strip()
    if s == "" or s.lower() in ("nan", "none"):
        return False
    if re.fullmatch(r"[\d.,\-+%]+", s):
        return False
    if s in ("O", "X"):
        return False
    return True


def load_excel(uploaded):
    raw = pd.read_excel(uploaded, header=None)
    n_rows, n_cols = raw.shape

    header_row_count = 1
    for r in range(min(n_rows, 5)):
        row_vals = raw.iloc[r]
        header_like = sum(1 for v in row_vals if is_header_text(v))
        if header_like >= max(1, n_cols * 0.3):
            header_row_count = r + 1

    col_names = []
    for c in range(n_cols):
        parts = []
        for r in range(header_row_count):
            v = raw.iloc[r, c]
            if is_header_text(v):
                parts.append(str(v).strip())
        name = "_".join(parts) if parts else f"col_{c}"
        col_names.append(name)

    seen = {}
    unique_names = []
    for nm in col_names:
        if nm in seen:
            seen[nm] += 1
            unique_names.append(f"{nm}_{seen[nm]}")
        else:
            seen[nm] = 0
            unique_names.append(nm)

    df = raw.iloc[header_row_count:].reset_index(drop=True)
    df.columns = unique_names[: len(df.columns)]

    for col in df.columns:
        converted = pd.to_numeric(df[col], errors="coerce")
        if converted.notna().sum() > len(df) * 0.3:
            df[col] = converted

    return df


# ──────────────────────────────────────────────
# 컬럼 매핑 (키워드 많은 패턴 우선 매칭
