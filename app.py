import streamlit as st
import pandas as pd
import json, io, os, re

# ──────────────────────────────────────────────
# 페이지 설정
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="끝장캐리 키워드 분석",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    section.main > div.block-container {
        max-width: 70vw !important;
        width: 70vw !important;
        margin-left: auto; margin-right: auto;
        padding-top: 1.5rem; padding-bottom: 2rem;
        padding-left: 2rem !important; padding-right: 2rem !important;
    }
    .app-title {font-size:1.8rem; font-weight:800; color:#1a1a2e; margin-bottom:0.2rem;}
    .app-title span {color:#4361ee;}
    .stButton > button {
        font-family: "Source Sans Pro", sans-serif;
        font-size: 0.82rem; font-weight: 500;
        white-space: nowrap !important;
    }
    #MainMenu {visibility:hidden;}
    footer {visibility:hidden;}
    header {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# 프리셋 관리
# ──────────────────────────────────────────────
PRESET_FILE = "presets.json"
PRESET_VERSION = 3

EMPTY_FILTERS = {
    "브랜드_키워드": "전체",
    "쇼핑성_키워드": "전체",
    "계절성": "전체",
    "작년_검색량_min": 0,
    "작년_검색량_max": 0,
    "작년최대검색월": [],
    "피크월검색량_min": 0,
    "피크월검색량_max": 0,
    "쿠팡_해외배송비율_min_pct": 0,
    "쿠팡_해외배송비율_max_pct": 0,
    "쿠팡_평균가_min": 0,
    "쿠팡_평균가_max": 0,
    "쿠팡_총리뷰수_min": 0,
    "쿠팡_총리뷰수_max": 0,
}

DEFAULT_PRESETS = {
    "_version": PRESET_VERSION,
    "프리셋 1": {"name": "프리셋 1", "filters": EMPTY_FILTERS.copy()},
    "프리셋 2": {"name": "프리셋 2", "filters": EMPTY_FILTERS.copy()},
    "프리셋 3": {"name": "프리셋 3", "filters": EMPTY_FILTERS.copy()},
    "프리셋 4": {"name": "프리셋 4", "filters": EMPTY_FILTERS.copy()},
    "프리셋 5": {"name": "프리셋 5", "filters": EMPTY_FILTERS.copy()},
}

def get_default_presets():
    import copy
    return copy.deepcopy(DEFAULT_PRESETS)

def load_presets():
    if os.path.exists(PRESET_FILE):
        try:
            with open(PRESET_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict) or data.get("_version") != PRESET_VERSION:
                return get_default_presets()
            for k, v in data.items():
                if k == "_version":
                    continue
                if not isinstance(v, dict):
                    return get_default_presets()
                if "filters" not in v or not isinstance(v["filters"], dict):
                    v["filters"] = EMPTY_FILTERS.copy()
                v.setdefault("name", k)
                for fk, fv in EMPTY_FILTERS.items():
                    v["filters"].setdefault(fk, fv)
            return data
        except Exception:
            return get_default_presets()
    return get_default_presets()

def save_presets(presets):
    try:
        with open(PRESET_FILE, "w", encoding="utf-8") as f:
            json.dump(presets, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

# ──────────────────────────────────────────────
# 헬퍼 함수
# ──────────────────────────────────────────────
def safe_int(val, default=0):
    if val is None:
        return default
    try:
        return int(val)
    except (ValueError, TypeError):
        return default

def safe_float(val, default=0.0):
    if val is None:
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default

def get_preset_name(presets, key):
    try:
        return presets[key]["name"]
    except Exception:
        return key

def get_preset_filters(presets, key):
    try:
        f = presets[key]["filters"]
        if isinstance(f, dict):
            result = EMPTY_FILTERS.copy()
            result.update(f)
            return result
    except Exception:
        pass
    return EMPTY_FILTERS.copy()

def is_header_text(val):
    if pd.isna(val):
        return False
    s = str(val).strip()
    if not s:
        return False
    if re.match(r'^-?[\d,]+\.?\d*$', s):
        return False
    if re.search(r'[가-힣]', s):
        return True
    if re.search(r'[a-zA-Z]', s) and len(s) >= 2:
        return True
    return False

# ──────────────────────────────────────────────
# 엑셀 로딩 (자동 헤더 행 감지)
# ──────────────────────────────────────────────
def load_excel(uploaded_file):
    preview = pd.read_excel(uploaded_file, sheet_name=0, header=None, nrows=10)
    uploaded_file.seek(0)

    header_row_count = 0
    for r in range(min(5, len(preview))):
        total = preview.shape[1]
        text_count = sum(1 for c in range(total) if is_header_text(preview.iloc[r, c]))
        if text_count / total >= 0.3:
            header_row_count = r + 1
        else:
            break

    if header_row_count == 0:
        header_row_count = 1

    header_df = pd.read_excel(uploaded_file, sheet_name=0, header=None, nrows=header_row_count)
    uploaded_file.seek(0)
    data_df = pd.read_excel(uploaded_file, sheet_name=0, header=None, skiprows=header_row_count)

    col_names = []
    for c in range(header_df.shape[1]):
        parts = []
        for r in range(header_row_count):
            val = header_df.iloc[r, c]
            if is_header_text(val):
                s = str(val).strip()
                if s not in parts:
                    parts.append(
