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
# 커스텀 CSS (모던 & 프리미엄 프로 디자인)
# ──────────────────────────────────────────────
st.markdown("""
<style>
/* ── 글로벌 폰트 (Pretendard 적용) ── */
@import url("https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.8/dist/web/static/pretendard.css");

* {
    font-family: "Pretendard", -apple-system, BlinkMacSystemFont, system-ui, Roboto, "Helvetica Neue", "Segoe UI", "Apple SD Gothic Neo", "Noto Sans KR", "Malgun Gothic", sans-serif !important;
}

/* ── 전역 숨김 ── */
#MainMenu, footer {visibility: hidden;}

/* 메인 화면 컨테이너를 가로 70%로 제한하고 중앙 정렬 (최우선 순위) */
[data-testid="stMainBlockContainer"] {
    max-width: 70% !important;
    min-width: 900px !important;
    margin: 0 auto !important;
    padding-top: 2.5rem !important;
}

/* ── 헤더 카드 (모던 다크 스타일) ── */
.header-card {
    background: linear-gradient(135deg, #111827 0%, #1e1b4b 100%);
    border-radius: 12px;
    padding: 32px 40px;
    margin-bottom: 28px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
}
.header-card .title-area h1 {
    margin: 0;
    font-size: 30px;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.5px;
}
.header-card .title-area p {
    margin: 8px 0 0 0;
    font-size: 15px;
    color: #9ca3af;
    letter-spacing: -0.3px;
}
.header-card .version-badge {
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: #e5e7eb;
    font-size: 13px;
    font-weight: 600;
    padding: 6px 16px;
    border-radius: 8px;
    letter-spacing: 0.5px;
}

/* ── 파일 업로드 영역 스타일 ── */
div[data-testid="stFileUploader"] {
    border: 2px dashed #cbd5e1;
    border-radius: 12px;
    padding: 24px;
    background: #f8fafc;
    margin-bottom: 28px;
    transition: all 0.2s ease;
}
div[data-testid="stFileUploader"]:hover {
    border-color: #6366f1;
    background: #f1f5f9;
}

/* ── 파일 로드 완료 배지 ── */
.file-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: #ecfdf5;
    border: 1px solid #a7f3d0;
    color: #065f46;
    font-size: 14.5px;
    font-weight: 600;
    padding: 10px 18px;
    border-radius: 8px;
    margin-bottom: 24px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

/* ── 프리셋 버튼 스타일 (세련된 아웃라인) ── */
div[data-testid="stHorizontalBlock"] button[kind="secondary"] {
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 14.5px !important;
    padding: 8px 20px !important;
    border: 1px solid #cbd5e1 !important;
    background: #ffffff !important;
    color: #475569 !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
}
div[data-testid="stHorizontalBlock"] button[kind="secondary"]:hover {
    border-color: #6366f1 !important;
    color: #6366f1 !important;
    background: #f8fafc !important;
    box-shadow: 0 4px 6px -1px rgba(99, 102, 241, 0.1) !important;
}

/* ── 분석실행 버튼 (모던 그라데이션) ── */
div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    padding: 12px 0 !important;
    box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.2), 0 2px 4px -1px rgba(79, 70, 229, 0.1) !important;
    transition: all 0.2s ease !important;
    letter-spacing: -0.3px !important;
}
div.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.3), 0 4px 6px -2px rgba(79, 70, 229, 0.1) !important;
}

/* ── 결과 카드 ── */
.result-header {
    font-size: 24px;
    font-weight: 800;
    color: #111827;
    margin-bottom: 16px;
    letter-spacing: -0.5px;
}
.result-count {
    color: #4f46e5;
}

/* ── 데이터프레임 ── */
div[data-testid="stDataFrame"] {
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    overflow: visible;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
}

/* ── 다운로드 버튼 ── */
div.stDownloadButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    border: 1px solid #6366f1 !important;
    color: #6366f1 !important;
    background: #ffffff !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
    transition: all 0.2s ease !important;
}
div.stDownloadButton > button:hover {
    background: #f8fafc !important;
    color: #4338ca !important;
    border-color: #4338ca !important;
}

/* ── 설정 expander ── */
div[data-testid="stExpander"] {
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

/* ── 메시지 영역 ── */
.empty-state {
    text-align: center;
    padding: 48px 20px;
    background: #f8fafc;
    border: 1px dashed #cbd5e1;
    border-radius: 12px;
    color: #64748b;
    font-size: 15.5px;
    margin-top: 16px;
    font-weight: 500;
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# 로그인 (비밀번호 인증)
# ──────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1.5, 1, 1.5]) 
    with c2:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 28px;">
            <h1 style="color: #111827; font-size: 28px; font-weight: 800; letter-spacing: -0.5px;">☕ 키워드서칭프로</h1>
            <p style="color: #64748b; font-size: 15px; line-height: 1.6; margin-top: 12px;">수강생 전용 분석 프로그램입니다.<br>부여받은 비밀번호를 입력해주세요.</p>
        </div>
        """, unsafe_allow_html=True)
        
        pwd_input = st.text_input("비밀번호", type="password", placeholder="비밀번호 입력", label_visibility="collapsed")
        st.markdown("<div style='margin-top: -8px;'></div>", unsafe_allow_html=True)
        if st.button("접속하기", use_container_width=True, type="primary"):
            if pwd_input == "chocolatte2":
                st.session_state["authenticated"] = True
                st.rerun()
            elif pwd_input != "":
                st.error("❌ 비밀번호가 올바르지 않습니다.")
    
    st.stop()


# ──────────────────────────────────────────────
# 프리셋 파일 관리
# ──────────────────────────────────────────────
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
# 통합 데이터 로딩 (CSV & Excel 스마트 헤더 인식)
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


def load_data(uploaded):
    # CSV와 Excel 모두 동일한 스마트 헤더 검색 적용
    if uploaded.name.endswith(".csv"):
        try:
            raw = pd.read_csv(uploaded, header=None, encoding="utf-8")
        except UnicodeDecodeError:
            uploaded.seek(0)
            raw = pd.read_csv(uploaded, header=None, encoding="cp949") # 윈도우 한글 CSV 깨짐 방지
    else:
        raw = pd.read_excel(uploaded, header=None)

    n_rows, n_cols = raw.shape
    header_row_count = 1
    
    # 상단 최대 5줄을 검색하여 가장 글자(컬럼명)가 많은 줄을 헤더로 인식
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
# 컬럼 매핑 (키워드 많은 패턴 우선 매칭)
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

    if len(col_list) > 1:
        cmap["키워드"] = col_list[1]
    for real_col in col_list:
        if real_col.strip() == "키워드":
            cmap["키워드"] = real_col
            break

    used = set(cmap.values())

    sorted_patterns = sorted(COLUMN_PATTERNS.items(), key=lambda x: len(x[1]), reverse=True)

    for std_key, keywords in sorted_patterns:
        best = None
        best_score = 0
        for real_col in col_list:
            if real_col in used:
                continue
            low = real_col.lower().replace(" ", "").replace("_", "")
            score = sum(1 for kw in keywords if kw in low)
            if score > best_score:
                best_score = score
                best = real_col
        if best and best_score >= len(keywords) * 0.5:
            cmap[std_key] = best
            used.add(best)

    return cmap


# ──────────────────────────────────────────────
# 표시 컬럼 정의
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
        key = spec["key"]
        label = spec.get("label", key)
        fmt = spec.get("format")

        if key not in cmap or cmap[key] not in df.columns:
            continue

        src = df[cmap[key]].copy()

        if fmt == "ox":
            mapped = []
            for v in src:
                sv = str(v).strip().upper()
                if sv in ("O", "TRUE", "1", "1.0", "Y", "YES"):
                    mapped.append("O")
                elif sv in ("X", "FALSE", "0", "0.0", "N", "NO"):
                    mapped.append("X")
                else:
                    mapped.append(str(v) if pd.notna(v) else "")
            rows[label] = mapped
        elif fmt == "season_ox":
            mapped = []
            for v in src:
                sv = str(v).strip()
                if sv in ("있음", "O", "TRUE", "1"):
                    mapped.append("O")
                elif sv in ("없음", "X", "FALSE", "0"):
                    mapped.append("X")
                else:
                    mapped.append(sv if pd.notna(v) else "")
            rows[label] = mapped
        elif fmt == "int":
            rows[label] = pd.to_numeric(src, errors="coerce").fillna(0).astype(int).tolist()
        elif fmt == "pct":
            numeric_vals = pd.to_numeric(src, errors="coerce").fillna(0)
            if numeric_vals.max() <= 1.0:
                numeric_vals = numeric_vals * 100
            rows[label] = numeric_vals.round(1).tolist()
        else:
            rows[label] = src.tolist()

    out = pd.DataFrame(rows, index=df.index)
    return out


# ──────────────────────────────────────────────
# 필터 적용
# ──────────────────────────────────────────────
def apply_filters(df, filters, cmap):
    out = df.copy()
    applied = []

    val = filters.get("브랜드키워드", "전체")
    if val != "전체" and "브랜드키워드" in cmap:
        col = cmap["브랜드키워드"]
        if col in out.columns:
            target = "O" if val == "O" else "X"
            out = out[out[col].astype(str).str.strip().str.upper() == target]
            applied.append(f"브랜드키워드={target}")

    val = filters.get("쇼핑성키워드", "전체")
    if val != "전체" and "쇼핑성키워드" in cmap:
        col = cmap["쇼핑성키워드"]
        if col in out.columns:
            target = "O" if val == "O" else "X"
            out = out[out[col].astype(str).str.strip().str.upper() == target]
            applied.append(f"쇼핑성키워드={target}")

    val = filters.get("계절성", "전체")
    if val != "전체" and "계절성" in cmap:
        col = cmap["계절성"]
        if col in out.columns:
            if val == "O":
                out = out[out[col].astype(str).str.strip().isin(["있음", "O", "TRUE", "1"])]
            else:
                out = out[out[col].astype(str).str.strip().isin(["없음", "X", "FALSE", "0"])]
            applied.append(f"계절성={val}")

    nonlocal_hack = {"out": out, "applied": applied}

    def nr(key, lo_key, hi_key, divisor=1):
        lo = safe_float(filters.get(lo_key, 0))
        hi = safe_float(filters.get(hi_key, 0))
        o = nonlocal_hack["out"]
        if (lo > 0 or hi > 0) and key in cmap:
            col = cmap[key]
            if col in o.columns:
                series = pd.to_numeric(o[col], errors="coerce")
                if divisor != 1:
                    lo_real = lo / divisor
                    hi_real = hi / divisor if hi > 0 else None
                else:
                    lo_real = lo
                    hi_real = hi if hi > 0 else None
                mask = pd.Series(True, index=o.index)
                if lo_real > 0:
                    mask = mask & (series >= lo_real)
                if hi_real is not None and hi_real > 0:
                    mask = mask & (series <= hi_real)
                o = o[mask.reindex(o.index, fill_value=False)]
                if divisor != 1:
                    nonlocal_hack["applied"].append(f"{key} {lo}%~{hi}%")
                else:
                    nonlocal_hack["applied"].append(f"{key} {lo:,}~{hi:,}")
        nonlocal_hack["out"] = o

    nr("작년검색량", "작년검색량_lo", "작년검색량_hi")
    nr("작년최대검색월검색량", "피크월검색량_lo", "피크월검색량_hi")
    nr("쿠팡해외배송비율", "쿠팡해외배송비율_lo", "쿠팡해외배송비율_hi", divisor=100)
    nr("쿠팡평균가", "쿠팡평균가_lo", "쿠팡평균가_hi")
    nr("쿠팡총리뷰수", "쿠팡총리뷰수_lo", "쿠팡총리뷰수_hi")

    out = nonlocal_hack["out"]
    applied = nonlocal_hack["applied"]

    months = filters.get("작년최대검색월", [])
    if months and "작년최대검색월" in cmap:
        col = cmap["작년최대검색월"]
        if col in out.columns:
            month_ints = [safe_int(m) for m in months]
            series = pd.to_numeric(out[col], errors="coerce")
            out = out[series.isin(month_ints)]
            applied.append(f"작년최대검색월={months}")

    if "쿠팡해외배송비율" in cmap:
        col = cmap["쿠팡해외배송비율"]
        if col in out.columns:
            sort_series = pd.to_numeric(out[col], errors="coerce")
            out = out.iloc[sort_series.fillna(-1).values.argsort()[::-1]]

    if "키워드" in cmap:
        col = cmap["키워드"]
        if col in out.columns:
            before = len(out)
            temp_col = "__키워드_정규화__"
            out[temp_col] = out[col].astype(str).str.strip().str.lower().str.replace(r"\s+", "", regex=True)
            out = out.drop_duplicates(subset=[temp_col], keep="first")
            del out[temp_col]
            if before != len(out):
                applied.append(f"키워드 중복제거 ({before:,}→{len(out):,})")

    return out, applied


# ──────────────────────────────────────────────
# 세션 상태 초기화 (매 접속 시 개별 초기화)
# ──────────────────────────────────────────────
if "presets" not in st.session_state:
    st.session_state["presets"] = json.loads(json.dumps(DEFAULT_PRESETS))
if "active_preset" not in st.session_state:
    st.session_state["active_preset"] = 0
if "df_raw" not in st.session_state:
    st.session_state["df_raw"] = None
if "df_filtered" not in st.session_state:
    st.session_state["df_filtered"] = None
if "cmap" not in st.session_state:
    st.session_state["cmap"] = {}
if "show_settings" not in st.session_state:
    st.session_state["show_settings"] = False
if "applied_info" not in st.session_state:
    st.session_state["applied_info"] = []

# ──────────────────────────────────────────────
# UI: 헤더
# ──────────────────────────────────────────────
st.markdown("""
<div class="header-card">
    <div class="title-area">
        <h1>☕ 초코라떼 키워드서칭프로</h1>
        <p>수강생 여러분의 효율적인 소싱을 돕는 전문 시장 분석 도구</p>
    </div>
    <div class="version-badge">ver. 2.28 Pro</div>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# UI: 파일 업로드
# ──────────────────────────────────────────────
uploaded = st.file_uploader(
    "📂 분석할 파일을 이곳에 올려주세요 (엑셀 .xlsx 또는 CSV)",
    type=["xlsx", "xls", "csv"],
)

if uploaded:
    if st.session_state["df_raw"] is None or st.session_state.get("_fname") != uploaded.name:
        with st.spinner("파일 로딩 중..."):
            # 통합 데이터 로더 사용 (CSV/Excel 스마트 헤더 및 인코딩 자동 처리)
            df = load_data(uploaded) 
            st.session_state["df_raw"] = df
            st.session_state["cmap"] = build_col_map(df.columns)
            st.session_state["_fname"] = uploaded.name
    st.markdown(
        f'<div class="file-badge">✅ {uploaded.name} 로드 완료 ({len(st.session_state["df_raw"]):,}행, {len(st.session_state["df_raw"].columns)}열)</div>',
        unsafe_allow_html=True,
    )

# ──────────────────────────────────────────────
# UI: 프리셋 바 + 분석 실행
# ──────────────────────────────────────────────
num_presets = len(st.session_state["presets"]["presets"])
preset_cols = st.columns([1] * num_presets + [0.4, 1.2])

for i in range(num_presets):
    with preset_cols[i]:
        label = get_preset_name(i)
        btn_type = "primary" if i == st.session_state["active_preset"] else "secondary"
        if st.button(label, key=f"btn_preset_{i}", use_container_width=True, type=btn_type):
            st.session_state["active_preset"] = i
            st.session_state["show_settings"] = False

with preset_cols[num_presets]:
    if st.button("⚙️", key="btn_gear"):
        st.session_state["show_settings"] = not st.session_state["show_settings"]

with preset_cols[num_presets + 1]:
    run_clicked = st.button("▶  분석 실행", key="btn_run", use_container_width=True, type="primary")

active = st.session_state["active_preset"]

# ──────────────────────────────────────────────
# UI: 프리셋 설정 (모든 필드 복구 및 디자인 유지)
# ──────────────────────────────────────────────
if st.session_state["show_settings"]:
    with st.expander(f"⚙️ {get_preset_name(active)} 세부 필터 설정", expanded=True):
        f = get_preset_filters(active)

        new_name = st.text_input("프리셋 이름", value=get_preset_name(active), key="inp_name")

        c1, c2, c3 = st.columns(3)
        with c1:
            brand = st.radio("브랜드키워드", ["전체", "O", "X"], index=["전체", "O", "X"].index(f.get("브랜드키워드", "전체")), key="inp_brand", horizontal=True)
        with c2:
            shopping = st.radio("쇼핑성키워드", ["전체", "O", "X"], index=["전체", "O", "X"].index(f.get("쇼핑성키워드", "전체")), key="inp_shopping", horizontal=True)
        with c3:
            season = st.radio("계절성", ["전체", "O", "X"], index=["전체", "O", "X"].index(f.get("계절성", "전체")), key="inp_season", horizontal=True)

        # 숫자 입력창을 콤팩트하게 유지하기 위한 3등분(1:1:1) 구조 사용
        c1, c2, empty = st.columns([1, 1, 1])
        with c1:
            s_lo = st.number_input("작년검색량 (최소)", value=safe_int(f.get("작년검색량_lo")), min_value=0, step=100, key="inp_search_lo")
        with c2:
            s_hi = st.number_input("작년검색량 (최대, 0=무제한)", value=safe_int(f.get("작년검색량_hi")), min_value=0, step=100, key="inp_search_hi")

        st.write("작년최대검색월 (복수 선택)")
        month_cols = st.columns(6)
        selected_months = []
        prev_months = f.get("작년최대검색월", [])
        for m in range(1, 13):
            with month_cols[(m - 1) % 6]:
                if st.checkbox(f"{m}월", value=(m in prev_months or str(m) in [str(x) for x in prev_months]), key=f"inp_month_{m}"):
                    selected_months.append(m)

        c1, c2, empty = st.columns([1, 1, 1])
        with c1:
            p_lo = st.number_input("피크월검색량 (최소)", value=safe_int(f.get("피크월검색량_lo")), min_value=0, step=100, key="inp_peak_lo")
        with c2:
            p_hi = st.number_input("피크월검색량 (최대, 0=무제한)", value=safe_int(f.get("피크월검색량_hi")), min_value=0, step=100, key="inp_peak_hi")

        c1, c2, empty = st.columns([1, 1, 1])
        with c1:
            o_lo = st.number_input("쿠팡해외배송비율 % (최소)", value=safe_float(f.get("쿠팡해외배송비율_lo")), min_value=0.0, step=1.0, format="%.1f", key="inp_overseas_lo")
        with c2:
            o_hi = st.number_input("쿠팡해외배송비율 % (최대, 0=무제한)", value=safe_float(f.get("쿠팡해외배송비율_hi")), min_value=0.0, step=1.0, format="%.1f", key="inp_overseas_hi")

        c1, c2, empty = st.columns([1, 1, 1])
        with c1:
            a_lo = st.number_input("쿠팡평균가 (최소)", value=safe_int(f.get("쿠팡평균가_lo")), min_value=0, step=1000, key="inp_avg_lo")
        with c2:
            a_hi = st.number_input("쿠팡평균가 (최대, 0=무제한)", value=safe_int(f.get("쿠팡평균가_hi")), min_value=0, step=1000, key="inp_avg_hi")

        c1, c2, empty = st.columns([1, 1, 1])
        with c1:
            r_lo = st.number_input("쿠팡총리뷰수 (최소)", value=safe_int(f.get("쿠팡총리뷰수_lo")), min_value=0, step=10, key="inp_review_lo")
        with c2:
            r_hi = st.number_input("쿠팡총리뷰수 (최대, 0=무제한)", value=safe_int(f.get("쿠팡총리뷰수_hi")), min_value=0, step=10, key="inp_review_hi")

        bc1, bc2 = st.columns(2)
        with bc1:
            if st.button("💾 임시 적용", key="btn_save", use_container_width=True):
                new_filters = {
                    "브랜드키워드": brand,
                    "쇼핑성키워드": shopping,
                    "계절성": season,
                    "작년검색량_lo": s_lo,
                    "작년검색량_hi": s_hi,
                    "작년최대검색월": selected_months,
                    "피크월검색량_lo": p_lo,
                    "피크월검색량_hi": p_hi,
                    "쿠팡해외배송비율_lo": o_lo,
                    "쿠팡해외배송비율_hi": o_hi,
                    "쿠팡평균가_lo": a_lo,
                    "쿠팡평균가_hi": a_hi,
                    "쿠팡총리뷰수_lo": r_lo,
                    "쿠팡총리뷰수_hi": r_hi,
                }
                st.session_state["presets"]["presets"][active]["name"] = new_name
                st.session_state["presets"]["presets"][active]["filters"] = new_filters
                st.success("현재 세션에 적용되었습니다! (새로고침 시 초기화)")
        with bc2:
            if st.button("❌ 닫기", key="btn_close", use_container_width=True):
                st.session_state["show_settings"] = False
                st.rerun()

# ──────────────────────────────────────────────
# UI: 분석 실행
# ──────────────────────────────────────────────
if run_clicked:
    if st.session_state["df_raw"] is None:
        st.warning("파일을 먼저 업로드하세요.")
    else:
        filters = get_preset_filters(active)
        cmap = st.session_state["cmap"]
        df_filtered, applied = apply_filters(st.session_state["df_raw"], filters, cmap)
        st.session_state["df_filtered"] = df_filtered
        st.session_state["applied_info"] = applied

# ──────────────────────────────────────────────
# UI: 결과 표시
# ──────────────────────────────────────────────
if st.session_state["df_filtered"] is not None:
    cmap = st.session_state["cmap"]
    df_f = st.session_state["df_filtered"]
    display_df = build_display_df(df_f, cmap)

    st.markdown(
        f'<div class="result-header">📊 분석 결과 (<span class="result-count">{len(display_df):,}건</span>)</div>',
        unsafe_allow_html=True,
    )

    col_config = {}
    for spec in DISPLAY_COLUMNS:
        label = spec.get("label", spec["key"])
        fmt = spec.get("format")
        if label not in display_df.columns:
            continue
        if fmt == "int":
            col_config[label] = st.column_config.NumberColumn(label, format="localized")
        elif fmt == "pct":
            col_config[label] = st.column_config.NumberColumn(label, format="%.1f%%")

    st.dataframe(
        display_df,
        column_config=col_config,
        hide_index=True,
        use_container_width=True,
    )

    download_df = display_df.copy()
    for spec in DISPLAY_COLUMNS:
        label = spec.get("label", spec["key"])
        fmt = spec.get("format")
        if label not in download_df.columns:
            continue
        if fmt == "int":
            download_df[label] = download_df[label].apply(
                lambda x: f"{int(x):,}" if pd.notna(x) else ""
            )
        elif fmt == "pct":
            download_df[label] = download_df[label].apply(
                lambda x: f"{x:.1f}%" if pd.notna(x) else ""
            )

    buf = io.BytesIO()
    download_df.to_excel(buf, index=False, engine="openpyxl")
    st.download_button(
        "📥 결과 다운로드 (Excel)",
        buf.getvalue(),
        file_name="분석결과.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    with st.expander("🔎 적용된 필터 상세"):
        if st.session_state["applied_info"]:
            for a in st.session_state["applied_info"]:
                st.write(f"• {a}")
        else:
            st.write("적용된 필터 없음")
else:
    st.markdown(
        '<div class="empty-state">파일을 업로드하고 분석 버튼을 눌러주세요.</div>',
        unsafe_allow_html=True,
    )
