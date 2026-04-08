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
    "presets": [{"name": f"프리셋 {i+1}", "filters": dict(EMPTY_FILTERS)} for i in range(5)],
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
    return DEFAULT_PRESETS

def save_presets(data):
    with open(PRESET_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ──────────────────────────────────────────────
# 유틸 함수
# ──────────────────────────────────────────────
def safe_int(v, default=0):
    try: return int(v)
    except (TypeError, ValueError): return default

def safe_float(v, default=0.0):
    try: return float(v)
    except (TypeError, ValueError): return default

def get_preset_name(idx):
    try: return st.session_state["presets"]["presets"][idx]["name"]
    except Exception: return f"프리셋 {idx+1}"

def get_preset_filters(idx):
    try:
        f = st.session_state["presets"]["presets"][idx]["filters"]
        merged = dict(EMPTY_FILTERS)
        merged.update(f)
        return merged
    except Exception:
        return dict(EMPTY_FILTERS)

# ──────────────────────────────────────────────
# 데이터 로딩 (CSV/Excel 통합 및 최적화)
# ──────────────────────────────────────────────
def is_header_text(val):
    if val is None or (isinstance(val, float) and pd.isna(val)): return False
    s = str(val).strip()
    if s == "" or s.lower() in ("nan", "none"): return False
    if re.fullmatch(r"[\d.,\-+%]+", s): return False
    if s in ("O", "X"): return False
    return True

def load_data(uploaded):
    """Excel과 CSV 모두를 위한 통합 로더"""
    if uploaded.name.endswith(".csv"):
        # CSV의 경우 인코딩 문제 대응 (cp949/utf-8)
        try:
            raw = pd.read_csv(uploaded, header=None, encoding="utf-8")
        except:
            uploaded.seek(0)
            raw = pd.read_csv(uploaded, header=None, encoding="cp949")
    else:
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
            if is_header_text(v): parts.append(str(v).strip())
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
    df.columns = unique_names[:len(df.columns)]

    # 숫자 자동 변환
    for col in df.columns:
        converted = pd.to_numeric(df[col], errors="coerce")
        if converted.notna().sum() > len(df) * 0.3:
            df[col] = converted
    return df

# ──────────────────────────────────────────────
# 컬럼 매핑 로직
# ──────────────────────────────────────────────
COLUMN_PATTERNS = {
    "브랜드키워드": ["브랜드", "brand"],
    "쇼핑성키워드": ["쇼핑성", "shopping"],
    "작년검색량": ["작년", "검색량"],
    "작년최대검색월검색량": ["작년", "최대", "검색월", "검색량"],
    "작년최대검색월": ["작년", "최대", "검색월"],
    "계절성": ["계절"],
    "쿠팡평균가": ["쿠팡", "평균가"],
    "쿠팡총리뷰수": ["쿠팡", "총리뷰"],
    "쿠팡최대리뷰수": ["쿠팡", "최대리뷰"],
    "쿠팡로켓배송비율": ["쿠팡", "로켓배송비율"],
    "쿠팡판매자로켓배송비율": ["쿠팡", "판매자", "로켓"],
    "쿠팡해외배송비율": ["쿠팡", "해외배송비율"],
    "쿠팡해외배송총리뷰수": ["쿠팡", "해외배송", "총리뷰"],
}

def build_col_map(columns):
    col_list = list(columns)
    cmap = {}
    if len(col_list) > 1: cmap["키워드"] = col_list[1]
    for real_col in col_list:
        if real_col.strip() == "키워드":
            cmap["키워드"] = real_col
            break

    used = set(cmap.values())
    sorted_patterns = sorted(COLUMN_PATTERNS.items(), key=lambda x: len(x[1]), reverse=True)

    for std_key, keywords in sorted_patterns:
        best, best_score = None, 0
        for real_col in col_list:
            if real_col in used: continue
            low = real_col.lower().replace(" ", "").replace("_", "")
            score = sum(1 for kw in keywords if kw in low)
            if score > best_score:
                best_score, best = score, real_col
        if best and best_score >= len(keywords) * 0.5:
            cmap[std_key] = best
            used.add(best)
    return cmap

# ──────────────────────────────────────────────
# 표시 데이터프레임 생성
# ──────────────────────────────────────────────
DISPLAY_COLUMNS = [
    {"key": "키워드"},
    {"key": "브랜드키워드", "label": "브랜드", "format": "ox"},
    {"key": "쇼핑성키워드", "label": "쇼핑성", "format": "ox"},
    {"key": "작년검색량", "format": "int"},
    {"key": "작년최대검색월"},
    {"key": "작년최대검색월검색량", "label": "피크월검색량", "format": "int"},
    {"key": "계절성", "format": "season_ox"},
    {"key": "쿠팡평균가", "format": "int"},
    {"key": "쿠팡총리뷰수", "format": "int"},
    {"key": "쿠팡최대리뷰수", "format": "int"},
    {"key": "쿠팡로켓배송비율", "format": "pct"},
    {"key": "쿠팡판매자로켓배송비율", "label": "로켓그로스비율", "format": "pct"},
    {"key": "쿠팡해외배송비율", "format": "pct"},
    {"key": "쿠팡해외배송총리뷰수", "format": "int"},
]

def build_display_df(df, cmap):
    rows = {}
    for spec in DISPLAY_COLUMNS:
        key, label, fmt = spec["key"], spec.get("label", spec["key"]), spec.get("format")
        if key not in cmap or cmap[key] not in df.columns: continue
        src = df[cmap[key]].copy()

        if fmt == "ox":
            rows[label] = [("O" if str(v).strip().upper() in ("O", "TRUE", "1", "Y", "YES") else "X" if str(v).strip().upper() in ("X", "FALSE", "0", "N", "NO") else str(v) if pd.notna(v) else "") for v in src]
        elif fmt == "season_ox":
            rows[label] = [("O" if str(v).strip() in ("있음", "O", "TRUE", "1") else "X" if str(v).strip() in ("없음", "X", "FALSE", "0") else str(v) if pd.notna(v) else "") for v in src]
        elif fmt == "int":
            rows[label] = pd.to_numeric(src, errors="coerce").fillna(0).astype(int).tolist()
        elif fmt == "pct":
            vals = pd.to_numeric(src, errors="coerce").fillna(0)
            if vals.max() <= 1.0: vals *= 100
            rows[label] = vals.round(1).tolist()
        else:
            rows[label] = src.tolist()
    return pd.DataFrame(rows, index=df.index)

# ──────────────────────────────────────────────
# 필터 적용 핵심 로직
# ──────────────────────────────────────────────
def apply_filters(df, filters, cmap):
    out = df.copy()
    applied = []

    def nr(key, lo_key, hi_key, divisor=1):
        nonlocal out, applied
        lo, hi = safe_float(filters.get(lo_key, 0)), safe_float(filters.get(hi_key, 0))
