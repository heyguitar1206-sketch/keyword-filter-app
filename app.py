import streamlit as st
import pandas as pd
import json, io, os, re

st.set_page_config(
    page_title="끝장캐리 키워드 분석",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    section.main > div.block-container {
        max-width: 70vw !important; width: 70vw !important;
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
    #MainMenu {visibility:hidden;} footer {visibility:hidden;} header {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# ── 프리셋 ──
PRESET_FILE = "presets.json"
PRESET_VERSION = 3
EMPTY_FILTERS = {
    "브랜드_키워드": "전체", "쇼핑성_키워드": "전체", "계절성": "전체",
    "작년_검색량_min": 0, "작년_검색량_max": 0, "작년최대검색월": [],
    "피크월검색량_min": 0, "피크월검색량_max": 0,
    "쿠팡_해외배송비율_min_pct": 0, "쿠팡_해외배송비율_max_pct": 0,
    "쿠팡_평균가_min": 0, "쿠팡_평균가_max": 0,
    "쿠팡_총리뷰수_min": 0, "쿠팡_총리뷰수_max": 0,
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

def save_presets(p):
    try:
        with open(PRESET_FILE, "w", encoding="utf-8") as f:
            json.dump(p, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

# ── 헬퍼 ──
def safe_int(v, d=0):
    if v is None: return d
    try: return int(v)
    except: return d

def safe_float(v, d=0.0):
    if v is None: return d
    try: return float(v)
    except: return d

def get_preset_name(p, k):
    try: return p[k]["name"]
    except: return k

def get_preset_filters(p, k):
    try:
        f = p[k]["filters"]
        if isinstance(f, dict):
            r = EMPTY_FILTERS.copy()
            r.update(f)
            return r
    except: pass
    return EMPTY_FILTERS.copy()

def is_header_text(val):
    if pd.isna(val): return False
    s = str(val).strip()
    if not s: return False
    if re.match(r'^-?[\d,]+\.?\d*$', s): return False
    if re.search(r'[가-힣]', s): return True
    if re.search(r'[a-zA-Z]', s) and len(s) >= 2: return True
    return False

# ── 엑셀 로딩 ──
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
                    parts.append(s)
        col_names.append("_".join(parts) if parts else f"col_{c}")
    seen = {}
    unique_names = []
    for name in col_names:
        if name in seen:
            seen[name] += 1
            unique_names.append(f"{name}_{seen[name]}")
        else:
            seen[name] = 0
            unique_names.append(name)
    data_df.columns = unique_names[:data_df.shape[1]]
    for col in data_df.columns:
        try: data_df[col] = pd.to_numeric(data_df[col])
        except: pass
    return data_df

# ── 컬럼 매핑 ──
COLUMN_PATTERNS = {
    "브랜드": ["브랜드_키워드"],
    "쇼핑성": ["쇼핑성_키워드"],
    "작년검색량": ["작년_검색량"],
    "작년최대검색월": ["작년_최대검색_월", "작년_최대검색월"],
    "피크월검색량": ["작년최대_검색월_검색량", "작년최대_검색량"],
    "계절성": ["계절성"],
    "계절성월": ["계절성_월"],
    "쿠팡평균가": ["쿠팡_평균가"],
    "쿠팡총리뷰수": ["쿠팡_총리뷰수"],
    "쿠팡최대리뷰수": ["쿠팡_최대리뷰수"],
    "쿠팡로켓배송비율": ["쿠팡_로켓배송비율"],
    "쿠팡판매자로켓배송비율": ["쿠팡_판매자로켓_배송비율", "쿠팡_판매자로켓배송비율"],
    "쿠팡해외배송비율": ["쿠팡_해외배송비율"],
    "쿠팡해외배송총리뷰수": ["쿠팡_해외배송_총리뷰수", "쿠팡_해외배송총리뷰수"],
}

def build_col_map(columns):
    col_list = list(columns)
    cmap = {}
    for real_col in col_list:
        if real_col.strip() == "키워드":
            cmap["키워드"] = real_col
            break
    if "키워드" not in cmap:
        for real_col in col_list:
            if real_col.replace("_", "").replace(" ", "") == "키워드":
                cmap["키워드"] = real_col
                break
    for std_key, patterns in COLUMN_PATTERNS.items():
        if std_key in cmap:
            continue
        for pat in patterns:
            for real_col in col_list:
                if real_col == pat and real_col not in cmap.values():
                    cmap[std_key] = real_col
                    break
            if std_key in cmap: break
        if std_key in cmap: continue
        for pat in patterns:
            parts = pat.replace("_", " ").split()
            for real_col in col_list:
                if real_col in cmap.values(): continue
                normalized = real_col.replace("_", " ").replace("\n", " ")
                if all(p in normalized for p in parts):
                    cmap[std_key] = real_col
                    break
            if std_key in cmap: break
        if std_key in cmap: continue
        kw_rules = {
            "브랜드": lambda c, cn: "브랜드" in cn and "키워드" in cn,
            "쇼핑성": lambda c, cn: "쇼핑성" in cn and "키워드" in cn,
            "작년검색량": lambda c, cn: "작년" in cn and "검색량" in cn and "최대" not in cn and "월" not in cn,
            "작년최대검색월": lambda c, cn: "작년" in cn and "최대" in cn and ("검색월" in cn or cn.endswith("월")),
            "피크월검색량": lambda c, cn: "작년" in cn and "최대" in cn and "검색량" in cn and "검색월" not in cn,
            "계절성": lambda c, cn: cn == "계절성" or (cn.startswith("계절성") and "월" not in cn),
            "계절성월": lambda c, cn: "계절성" in cn and "월" in cn,
            "쿠팡평균가": lambda c, cn: "쿠팡" in cn and "평균가" in cn and "해외" not in cn,
            "쿠팡총리뷰수": lambda c, cn: "쿠팡" in cn and "총리뷰수" in cn and "해외" not in cn,
            "쿠팡최대리뷰수": lambda c, cn: "쿠팡" in cn and "최대리뷰수" in cn and "해외" not in cn,
            "쿠팡로켓배송비율": lambda c, cn: "쿠팡" in cn and "로켓배송비율" in cn and "판매자" not in cn,
            "쿠팡판매자로켓배송비율": lambda c, cn: "쿠팡" in cn and "판매자" in cn and "로켓" in cn,
            "쿠팡해외배송비율": lambda c, cn: "쿠팡" in cn and "해외배송비율" in cn and "총리뷰" not in cn and "최대" not in cn and "평균" not in cn,
            "쿠팡해외배송총리뷰수": lambda c, cn: "쿠팡" in cn and "해외배송" in cn and "총리뷰수" in cn,
        }
        if std_key in kw_rules:
            rule = kw_rules[std_key]
            candidates = [c for c in col_list if c not in cmap.values() and rule(c, c.replace("_", "").replace(" ", ""))]
            if len(candidates) == 1:
                cmap[std_key] = candidates[0]
            elif len(candidates) > 1:
                cmap[std_key] = min(candidates, key=len)
    return cmap

# ── 출력 컬럼 ──
DISPLAY_COLUMNS = [
    {"key": "키워드", "label": "키워드", "format": None},
    {"key": "브랜드", "label": "브랜드키워드", "format": "ox"},
    {"key": "쇼핑성", "label": "쇼핑성키워드", "format": "ox"},
    {"key": "작년검색량", "label": "작년검색량", "format": "int"},
    {"key": "작년최대검색월", "label": "작년최대검색월", "format": "int"},
    {"key": "피크월검색량", "label": "피크월검색량", "format": "int"},
    {"key": "계절성", "label": "계절성", "format": "season_ox"},
    {"key": "쿠팡평균가", "label": "쿠팡평균가", "format": "int"},
    {"key": "쿠팡총리뷰수", "label": "쿠팡총리뷰수", "format": "int"},
    {"key": "쿠팡최대리뷰수", "label": "쿠팡최대리뷰수", "format": "int"},
    {"key": "쿠팡로켓배송비율", "label": "쿠팡로켓배송비율", "format": "pct"},
    {"key": "쿠팡판매자로켓배송비율", "label": "로켓그로스비율", "format": "pct"},
    {"key": "쿠팡해외배송비율", "label": "쿠팡해외배송비율", "format": "pct"},
    {"key": "쿠팡해외배송총리뷰수", "label": "쿠팡해외배송총리뷰수", "format": "int"},
]

def build_display_df(df, cmap):
    display_data = {}
    for dcol in DISPLAY_COLUMNS:
        key, label, fmt = dcol["key"], dcol["label"], dcol["format"]
        if key not in cmap:
            display_data[label] = [""] * len(df)
            continue
        series = df[cmap[key]].copy()
        if fmt == "ox":
            series = series.astype(str).str.strip().str.upper().replace({"NAN": "", "NONE": ""})
        elif fmt == "season_ox":
            series = series.astype(str).str.strip().map(lambda v: "O" if v == "있음" else ("X" if v == "없음" else v))
        elif fmt == "int":
            numeric = pd.to_numeric(series, errors="coerce")
            series = numeric.apply(lambda v: f"{int(v):,}" if pd.notna(v) else "")
        elif fmt == "pct":
            numeric = pd.to_numeric(series, errors="coerce")
            series = numeric.apply(lambda v: f"{v * 100:.1f}%" if pd.notna(v) else "")
        display_data[label] = series.values
    return pd.DataFrame(display_data)

# ── 필터 적용 ──
def apply_filters(df, filters, cmap):
    out = df.copy()
    applied = []

    val = filters.get("브랜드_키워드", "전체")
    if val in ("O", "X") and "브랜드" in cmap:
        col = cmap["브랜드"]
        before = len(out)
        out = out[out[col].astype(str).str.strip().str.upper() == val]
        applied.append(f"브랜드={val} ({before:,}→{len(out):,})")

    val = filters.get("쇼핑성_키워드", "전체")
    if val in ("O", "X") and "쇼핑성" in cmap:
        col = cmap["쇼핑성"]
        before = len(out)
        out = out[out[col].astype(str).str.strip().str.upper() == val]
        applied.append(f"쇼핑성={val} ({before:,}→{len(out):,})")

    val = filters.get("계절성", "전체")
    if val in ("O", "X") and "계절성" in cmap:
        col = cmap["계절성"]
        before = len(out)
        if val == "O":
            out = out[out[col].astype(str).str.strip() == "있음"]
        else:
            out = out[out[col].astype(str).str.strip() == "없음"]
        applied.append(f"계절성={val} ({before:,}→{len(out):,})")

    def numeric_range(std_key, min_key, max_key, label, divisor=1.0):
        nonlocal out
        lo = safe_float(filters.get(min_key))
        hi = safe_float(filters.get(max_key))
        if (lo <= 0 and hi <= 0) or std_key not in cmap:
            return
        col = cmap[std_key]
        before = len(out)
        if lo > 0:
            s = pd.to_numeric(out[col], errors="coerce")
            out = out.loc[s[s >= lo / divisor].index.intersection(out.index)]
        if hi > 0:
            s = pd.to_numeric(out[col], errors="coerce")
            out = out.loc[s[s <= hi / divisor].index.intersection(out.index)]
        applied.append(f"{label}: {lo}~{hi} ({before:,}→{len(out):,})")

    numeric_range("작년검색량", "작년_검색량_min", "작년_검색량_max", "작년검색량")
    numeric_range("피크월검색량", "피크월검색량_min", "피크월검색량_max", "피크월검색량")
    numeric_range("쿠팡해외배송비율", "쿠팡_해외배송비율_min_pct", "쿠팡_해외배송비율_max_pct", "쿠팡해외배송비율(%)", divisor=100.0)
    numeric_range("쿠팡평균가", "쿠팡_평균가_min", "쿠팡_평균가_max", "쿠팡평균가")
    numeric_range("쿠팡총리뷰수", "쿠팡_총리뷰수_min", "쿠팡_총리뷰수_max", "쿠팡총리뷰수")

    months = filters.get("작년최대검색월", [])
    if months and "작년최대검색월" in cmap:
        col = cmap["작년최대검색월"]
        before = len(out)
        month_ints = [int(m) for m in months]
        s = pd.to_numeric(out[col], errors="coerce")
        out = out.loc[s[s.isin(month_ints)].index.intersection(out.index)]
        applied.append(f"작년최대검색월={months} ({before:,}→{len(out):,})")

    if "쿠팡해외배송비율" in cmap:
        col = cmap["쿠팡해외배송비율"]
        out[col] = pd.to_numeric(out[col], errors="coerce")
        out = out.sort_values(col, ascending=False, na_position="last")

    if "키워드" in cmap:
        col = cmap["키워드"]
        before = len(out)
        temp_col = "__kw_norm__"
        out[temp_col] = out[col].astype(str).str.strip().str.lower().str.replace(r'\s+', '', regex=True)
        out = out.drop_duplicates(subset=[temp_col], keep="first")
        out = out.drop(columns=[temp_col])
        if before != len(out):
            applied.append(f"키워드 중복제거 ({before:,}→{len(out):,})")

    return out, applied

# ── 세션 상태 ──
if "presets" not in st.session_state or not isinstance(st.session_state.presets, dict):
    st.session_state.presets = load_presets()
if st.session_state.presets.get("_version") != PRESET_VERSION:
    st.session_state.presets = get_default_presets()
if "active_preset" not in st.session_state:
    st.session_state.active_preset = "프리셋 1"
if "df" not in st.session_state:
    st.session_state.df = None
if "filtered_df" not in st.session_state:
    st.session_state.filtered_df = None
if "display_df" not in st.session_state:
    st.session_state.display_df = None
if "col_map" not in st.session_state:
    st.session_state.col_map = {}
if "show_settings" not in st.session_state:
    st.session_state.show_settings = False
if "applied_info" not in st.session_state:
    st.session_state.applied_info = []

# ── UI: 제목 ──
st.markdown('<div class="app-title">📊 <span>끝장캐리</span> 키워드 분석</div>', unsafe_allow_html=True)
st.markdown("---")

# ── UI: 파일 업로드 ──
uploaded = st.file_uploader("엑셀 파일 업로드 (.xlsx / .csv)", type=["xlsx", "csv"])
if uploaded is not None:
    if st.session_state.df is None or st.session_state.get("_uploaded_name") != uploaded.name:
        with st.spinner("파일 로딩 중…"):
            if uploaded.name.endswith(".csv"):
                st.session_state.df = pd.read_csv(uploaded)
            else:
                st.session_state.df = load_excel(uploaded)
            st.session_state.col_map = build_col_map(st.session_state.df.columns)
            st.session_state._uploaded_name = uploaded.name
            st.session_state.filtered_df = None
            st.session_state.display_df = None
        st.success(f"✅ 로드 완료: {len(st.session_state.df):,}행 × {len(st.session_state.df.columns)}열")

# ── UI: 프리셋 바 ──
st.markdown("#### 분석 프리셋")
preset_keys = ["프리셋 1", "프리셋 2", "프리셋 3", "프리셋 4", "프리셋 5"]
cols = st.columns([2, 0.5, 2, 0.5, 2, 0.5, 2, 0.5, 2, 0.5, 2])
for i, pkey in enumerate(preset_keys):
    pname = get_preset_name(st.session_state.presets, pkey)
    with cols[i * 2]:
        if st.button(pname, key=f"btn_{pkey}", use_container_width=True):
            st.session_state.active_preset = pkey
            st.session_state.filtered_df = None
            st.session_state.display_df = None
    with cols[i * 2 + 1]:
        if st.button("⚙", key=f"gear_{pkey}"):
            st.session_state.active_preset = pkey
            st.session_state.show_settings = True
with cols[10]:
    run_clicked = st.button("▶ 분석 실행", type="primary", use_container_width=True)
st.caption(f"현재 선택: **{get_preset_name(st.session_state.presets, st.session_state.active_preset)}**")

# ── UI: 프리셋 설정 ──
if st.session_state.show_settings:
    pkey = st.session_state.active_preset
    preset_data = st.session_state.presets.get(pkey, {"name": pkey, "filters": EMPTY_FILTERS.copy()})
    if not isinstance(preset_data, dict):
        preset_data = {"name": pkey, "filters": EMPTY_FILTERS.copy()}
    cf = preset_data.get("filters", EMPTY_FILTERS.copy())
    if not isinstance(cf, dict):
        cf = EMPTY_FILTERS.copy()

    st.markdown(f"### ⚙ {pkey} 설정")
    new_name = st.text_input("프리셋 이름", value=preset_data.get("name", pkey), key="setting_name")
    st.markdown("---")

    st.markdown("**브랜드 여부**")
    brand_val = cf.get("브랜드_키워드", "전체")
    bc1, bc2 = st.columns(2)
    with bc1: brand_o = st.checkbox("O", value=(brand_val == "O"), key="brand_o")
    with bc2: brand_x = st.checkbox("X", value=(brand_val == "X"), key="brand_x")
    new_brand = "O" if (brand_o and not brand_x) else ("X" if (brand_x and not brand_o) else "전체")

    st.markdown("**쇼핑성 여부**")
    shop_val = cf.get("쇼핑성_키워드", "전체")
    sc1, sc2 = st.columns(2)
    with sc1: shop_o = st.checkbox("O", value=(shop_val == "O"), key="shop_o")
    with sc2: shop_x = st.checkbox("X", value=(shop_val == "X"), key="shop_x")
    new_shop = "O" if (shop_o and not shop_x) else ("X" if (shop_x and not shop_o) else "전체")

    st.markdown("**계절성 여부**")
    season_val = cf.get("계절성", "전체")
    sec1, sec2 = st.columns(2)
    with sec1: season_o = st.checkbox("O (있음)", value=(season_val == "O"), key="season_o")
    with sec2: season_x = st.checkbox("X (없음)", value=(season_val == "X"), key="season_x")
    new_season = "O" if (season_o and not season_x) else ("X" if (season_x and not season_o) else "전체")

    st.markdown("---")

    st.markdown("**작년 검색량**")
    r1, r2 = st.columns(2)
    with r1: v_search_min = st.number_input("최소", min_value=0, value=safe_int(cf.get("작년_검색량_min")), step=1000, key="search_min")
    with r2: v_search_max = st.number_input("최대 (0=무제한)", min_value=0, value=safe_int(cf.get("작년_검색량_max")), step=1000, key="search_max")

    st.markdown("**작년최대검색월**")
