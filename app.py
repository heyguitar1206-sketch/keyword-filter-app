import streamlit as st
import pandas as pd
import json, io, os

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
    .preset-badge {
        display:inline-block; padding:2px 10px; border-radius:10px;
        font-size:0.75rem; font-weight:600; margin-left:6px;
    }
    .preset-badge.active {background:#4361ee; color:#fff;}
    .result-box {
        background:#f8f9fa; border:1px solid #dee2e6; border-radius:8px;
        padding:1rem; margin-top:0.5rem;
    }
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
PRESET_VERSION = 3  # 버전을 올려서 기존 파일 무시

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
            # 각 프리셋 검증
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

# ──────────────────────────────────────────────
# 엑셀 로딩 (3행 헤더 병합)
# ──────────────────────────────────────────────
def load_excel(uploaded_file):
    # 첫 3행을 헤더로 읽기
    header_df = pd.read_excel(uploaded_file, sheet_name=0, header=None, nrows=3)
    # 데이터 본체 읽기 (3행 스킵)
    uploaded_file.seek(0)
    data_df = pd.read_excel(uploaded_file, sheet_name=0, header=None, skiprows=3)

    # 3행을 합쳐 컬럼명 생성
    col_names = []
    for c in range(header_df.shape[1]):
        parts = []
        for r in range(3):
            val = header_df.iloc[r, c]
            if pd.notna(val):
                s = str(val).strip()
                if s and s not in parts:
                    parts.append(s)
        col_names.append("_".join(parts) if parts else f"col_{c}")

    # 중복 컬럼명 처리
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

    # 숫자 변환
    for col in data_df.columns:
        try:
            data_df[col] = pd.to_numeric(data_df[col])
        except (ValueError, TypeError):
            pass

    return data_df

# ──────────────────────────────────────────────
# 컬럼 매핑 (부분 문자열 매칭)
# ──────────────────────────────────────────────
COLUMN_PATTERNS = {
    "브랜드": ["브랜드_키워드", "브랜드"],
    "쇼핑성": ["쇼핑성_키워드", "쇼핑성"],
    "작년검색량": ["작년_검색량"],
    "작년최대검색월": ["작년_최대검색_월", "작년최대검색월", "작년_최대검색월"],
    "피크월검색량": ["작년최대_검색월_검색량", "작년최대검색월검색량", "작년_최대_검색월_검색량", "작년최대_검색량"],
    "계절성": ["계절성"],
    "쿠팡해외배송비율": ["쿠팡_해외배송비율"],
    "쿠팡평균가": ["쿠팡_평균가"],
    "쿠팡총리뷰수": ["쿠팡_총리뷰수"],
}

def build_col_map(columns):
    """실제 DataFrame 컬럼명과 표준 키를 매칭. 부분문자열 매칭 사용."""
    col_list = list(columns)
    cmap = {}

    for std_key, patterns in COLUMN_PATTERNS.items():
        # 1차: 정확 매칭
        for pat in patterns:
            for real_col in col_list:
                if real_col == pat:
                    cmap[std_key] = real_col
                    break
            if std_key in cmap:
                break

        if std_key in cmap:
            continue

        # 2차: 패턴의 각 부분이 모두 컬럼명에 포함되는지 확인
        for pat in patterns:
            parts = pat.replace("_", " ").split()
            for real_col in col_list:
                normalized = real_col.replace("_", " ").replace("\n", " ")
                if all(p in normalized for p in parts):
                    cmap[std_key] = real_col
                    break
            if std_key in cmap:
                break

        if std_key in cmap:
            continue

        # 3차: 더 관대한 매칭 — 키워드 포함 여부
        keyword_map = {
            "브랜드": "브랜드",
            "쇼핑성": "쇼핑성",
            "계절성": "계절성",
            "작년검색량": "작년",
            "쿠팡해외배송비율": "해외배송비율",
            "쿠팡평균가": "쿠팡",
            "쿠팡총리뷰수": "총리뷰수",
        }
        if std_key in keyword_map:
            kw = keyword_map[std_key]
            candidates = [c for c in col_list if kw in c and c not in cmap.values()]

            # 특별 처리: 쿠팡평균가 — "쿠팡"이 포함되고 "평균가"도 포함
            if std_key == "쿠팡평균가":
                candidates = [c for c in col_list if "쿠팡" in c and "평균가" in c and c not in cmap.values()]
            elif std_key == "작년검색량":
                candidates = [c for c in col_list if "작년" in c and "검색량" in c and "최대" not in c and "월" not in c and c not in cmap.values()]
            elif std_key == "피크월검색량":
                candidates = [c for c in col_list if "작년" in c and "최대" in c and "검색량" in c and "월" not in c.split("_")[-1] and c not in cmap.values()]
                if not candidates:
                    candidates = [c for c in col_list if "작년최대" in c and "검색량" in c and c not in cmap.values()]
            elif std_key == "작년최대검색월":
                candidates = [c for c in col_list if "작년" in c and "최대" in c and "월" in c and "검색량" not in c and c not in cmap.values()]
                if not candidates:
                    # "작년_최대검색_월" 또는 "작년최대검색월" 패턴
                    candidates = [c for c in col_list if "최대" in c and "월" in c.replace("검색량", "") and c not in cmap.values()]

            if len(candidates) == 1:
                cmap[std_key] = candidates[0]
            elif len(candidates) > 1:
                # 가장 짧은 이름 선택 (더 구체적)
                cmap[std_key] = min(candidates, key=len)

    return cmap

# ──────────────────────────────────────────────
# 필터 적용
# ──────────────────────────────────────────────
def apply_filters(df, filters, cmap):
    out = df.copy()
    applied = []

    # ─── O/X 필터: 브랜드 ───
    val = filters.get("브랜드_키워드", "전체")
    if val in ("O", "X") and "브랜드" in cmap:
        col = cmap["브랜드"]
        before = len(out)
        out = out[out[col].astype(str).str.strip().str.upper() == val]
        applied.append(f"브랜드={val} ({before}→{len(out)})")

    # ─── O/X 필터: 쇼핑성 ───
    val = filters.get("쇼핑성_키워드", "전체")
    if val in ("O", "X") and "쇼핑성" in cmap:
        col = cmap["쇼핑성"]
        before = len(out)
        out = out[out[col].astype(str).str.strip().str.upper() == val]
        applied.append(f"쇼핑성={val} ({before}→{len(out)})")

    # ─── O/X 필터: 계절성 ───
    val = filters.get("계절성", "전체")
    if val in ("O", "X") and "계절성" in cmap:
        col = cmap["계절성"]
        before = len(out)
        if val == "O":
            out = out[out[col].astype(str).str.strip() == "있음"]
        else:
            out = out[out[col].astype(str).str.strip() == "없음"]
        applied.append(f"계절성={val} ({before}→{len(out)})")

    # ─── 숫자 범위 필터 함수 ───
    def numeric_range(std_key, min_key, max_key, label, divisor=1.0):
        nonlocal out
        lo = safe_float(filters.get(min_key))
        hi = safe_float(filters.get(max_key))
        if (lo <= 0 and hi <= 0) or std_key not in cmap:
            return
        col = cmap[std_key]
        s = pd.to_numeric(out[col], errors="coerce")
        before = len(out)
        if lo > 0:
            real_lo = lo / divisor
            out = out.loc[s[s >= real_lo].index.intersection(out.index)]
        # s를 다시 계산 (out이 줄었으므로)
        s = pd.to_numeric(out[col], errors="coerce")
        if hi > 0:
            real_hi = hi / divisor
            out = out.loc[s[s <= real_hi].index.intersection(out.index)]
        applied.append(f"{label}: {lo}~{hi} ({before}→{len(out)})")

    # 작년 검색량
    numeric_range("작년검색량", "작년_검색량_min", "작년_검색량_max", "작년검색량")

    # 피크월 검색량
    numeric_range("피크월검색량", "피크월검색량_min", "피크월검색량_max", "피크월검색량")

    # 쿠팡 해외배송비율 (UI는 %, 데이터는 0~1)
    numeric_range("쿠팡해외배송비율", "쿠팡_해외배송비율_min_pct", "쿠팡_해외배송비율_max_pct",
                  "쿠팡해외배송비율(%)", divisor=100.0)

    # 쿠팡 평균가
    numeric_range("쿠팡평균가", "쿠팡_평균가_min", "쿠팡_평균가_max", "쿠팡평균가")

    # 쿠팡 총리뷰수
    numeric_range("쿠팡총리뷰수", "쿠팡_총리뷰수_min", "쿠팡_총리뷰수_max", "쿠팡총리뷰수")

    # ─── 작년최대검색월 (복수 선택) ───
    months = filters.get("작년최대검색월", [])
    if months and "작년최대검색월" in cmap:
        col = cmap["작년최대검색월"]
        before = len(out)
        month_ints = [int(m) for m in months]
        s = pd.to_numeric(out[col], errors="coerce")
        out = out.loc[s[s.isin(month_ints)].index.intersection(out.index)]
        applied.append(f"작년최대검색월={months} ({before}→{len(out)})")

    # ─── 결과를 쿠팡 해외배송비율 내림차순 정렬 ───
    if "쿠팡해외배송비율" in cmap:
        col = cmap["쿠팡해외배송비율"]
        out[col] = pd.to_numeric(out[col], errors="coerce")
        out = out.sort_values(col, ascending=False, na_position="last")

    return out, applied

# ──────────────────────────────────────────────
# 세션 상태 초기화
# ──────────────────────────────────────────────
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
if "col_map" not in st.session_state:
    st.session_state.col_map = {}
if "show_settings" not in st.session_state:
    st.session_state.show_settings = False
if "applied_info" not in st.session_state:
    st.session_state.applied_info = []

# ──────────────────────────────────────────────
# UI: 제목
# ──────────────────────────────────────────────
st.markdown('<div class="app-title">📊 <span>끝장캐리</span> 키워드 분석</div>', unsafe_allow_html=True)
st.markdown("---")

# ──────────────────────────────────────────────
# UI: 파일 업로드
# ──────────────────────────────────────────────
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
        st.success(f"✅ 로드 완료: {len(st.session_state.df):,}행 × {len(st.session_state.df.columns)}열")

# ──────────────────────────────────────────────
# UI: 프리셋 바
# ──────────────────────────────────────────────
st.markdown("#### 분석 프리셋")
preset_keys = ["프리셋 1", "프리셋 2", "프리셋 3", "프리셋 4", "프리셋 5"]

# 11열: 5*프리셋버튼 + 5*기어버튼 + 1*분석실행
cols = st.columns([2, 0.5, 2, 0.5, 2, 0.5, 2, 0.5, 2, 0.5, 2])

for i, pkey in enumerate(preset_keys):
    pname = get_preset_name(st.session_state.presets, pkey)
    btn_col = cols[i * 2]
    gear_col = cols[i * 2 + 1]

    with btn_col:
        if st.button(pname, key=f"btn_{pkey}", use_container_width=True):
            st.session_state.active_preset = pkey
            st.session_state.filtered_df = None

    with gear_col:
        if st.button("⚙", key=f"gear_{pkey}"):
            st.session_state.active_preset = pkey
            st.session_state.show_settings = True

with cols[10]:
    run_clicked = st.button("▶ 분석 실행", type="primary", use_container_width=True)

# 현재 활성 프리셋 표시
st.caption(f"현재 선택: **{get_preset_name(st.session_state.presets, st.session_state.active_preset)}**")

# ──────────────────────────────────────────────
# UI: 프리셋 설정 패널
# ──────────────────────────────────────────────
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

    # ─── 브랜드 여부 ───
    st.markdown("**브랜드 여부**")
    brand_val = cf.get("브랜드_키워드", "전체")
    bc1, bc2 = st.columns(2)
    with bc1:
        brand_o = st.checkbox("O", value=(brand_val == "O"), key="brand_o")
    with bc2:
        brand_x = st.checkbox("X", value=(brand_val == "X"), key="brand_x")
    if brand_o and not brand_x:
        new_brand = "O"
    elif brand_x and not brand_o:
        new_brand = "X"
    else:
        new_brand = "전체"

    # ─── 쇼핑성 여부 ───
    st.markdown("**쇼핑성 여부**")
    shop_val = cf.get("쇼핑성_키워드", "전체")
    sc1, sc2 = st.columns(2)
    with sc1:
        shop_o = st.checkbox("O", value=(shop_val == "O"), key="shop_o")
    with sc2:
        shop_x = st.checkbox("X", value=(shop_val == "X"), key="shop_x")
    if shop_o and not shop_x:
        new_shop = "O"
    elif shop_x and not shop_o:
        new_shop = "X"
    else:
        new_shop = "전체"

    # ─── 계절성 여부 ───
    st.markdown("**계절성 여부**")
    season_val = cf.get("계절성", "전체")
    sec1, sec2 = st.columns(2)
    with sec1:
        season_o = st.checkbox("O (있음)", value=(season_val == "O"), key="season_o")
    with sec2:
        season_x = st.checkbox("X (없음)", value=(season_val == "X"), key="season_x")
    if season_o and not season_x:
        new_season = "O"
    elif season_x and not season_o:
        new_season = "X"
    else:
        new_season = "전체"

    st.markdown("---")

    # ─── 작년 검색량 ───
    st.markdown("**작년 검색량**")
    r1, r2 = st.columns(2)
    with r1:
        v_search_min = st.number_input("최소", min_value=0, value=safe_int(cf.get("작년_검색량_min")), step=1000, key="search_min")
    with r2:
        v_search_max = st.number_input("최대 (0=무제한)", min_value=0, value=safe_int(cf.get("작년_검색량_max")), step=1000, key="search_max")

    # ─── 작년최대검색월 ───
    st.markdown("**작년최대검색월**")
    saved_months = cf.get("작년최대검색월", [])
    if not isinstance(saved_months, list):
        saved_months = []
    month_cols = st.columns(12)
    selected_months = []
    for mi in range(12):
        with month_cols[mi]:
            if st.checkbox(f"{mi+1}월", value=(mi+1 in saved_months or str(mi+1) in [str(x) for x in saved_months]), key=f"month_{mi+1}"):
                selected_months.append(mi + 1)

    # ─── 피크월 검색량 ───
    st.markdown("**피크월검색량**")
    p1, p2 = st.columns(2)
    with p1:
        v_peak_min = st.number_input("최소", min_value=0, value=safe_int(cf.get("피크월검색량_min")), step=1000, key="peak_min")
    with p2:
        v_peak_max = st.number_input("최대 (0=무제한)", min_value=0, value=safe_int(cf.get("피크월검색량_max")), step=1000, key="peak_max")

    # ─── 쿠팡 해외배송비율 (%) ───
    st.markdown("**쿠팡 해외배송비율 (%)**")
    c1, c2 = st.columns(2)
    with c1:
        v_overseas_min = st.number_input("최소 %", min_value=0, max_value=100, value=safe_int(cf.get("쿠팡_해외배송비율_min_pct")), step=5, key="overseas_min")
    with c2:
        v_overseas_max = st.number_input("최대 % (0=무제한)", min_value=0, max_value=100, value=safe_int(cf.get("쿠팡_해외배송비율_max_pct")), step=5, key="overseas_max")

    # ─── 쿠팡 평균가 ───
    st.markdown("**쿠팡 평균가**")
    a1, a2 = st.columns(2)
    with a1:
        v_price_min = st.number_input("최소", min_value=0, value=safe_int(cf.get("쿠팡_평균가_min")), step=1000, key="price_min")
    with a2:
        v_price_max = st.number_input("최대 (0=무제한)", min_value=0, value=safe_int(cf.get("쿠팡_평균가_max")), step=1000, key="price_max")

    # ─── 쿠팡 총리뷰수 ───
    st.markdown("**쿠팡 총리뷰수**")
    rv1, rv2 = st.columns(2)
    with rv1:
        v_review_min = st.number_input("최소", min_value=0, value=safe_int(cf.get("쿠팡_총리뷰수_min")), step=10, key="review_min")
    with rv2:
        v_review_max = st.number_input("최대 (0=무제한)", min_value=0, value=safe_int(cf.get("쿠팡_총리뷰수_max")), step=10, key="review_max")

    st.markdown("---")

    # 저장 / 닫기
    sv1, sv2 = st.columns(2)
    with sv1:
        if st.button("💾 저장", use_container_width=True):
            new_filters = {
                "브랜드_키워드": new_brand,
                "쇼핑성_키워드": new_shop,
                "계절성": new_season,
                "작년_검색량_min": v_search_min,
                "작년_검색량_max": v_search_max,
                "작년최대검색월": selected_months,
                "피크월검색량_min": v_peak_min,
                "피크월검색량_max": v_peak_max,
                "쿠팡_해외배송비율_min_pct": v_overseas_min,
                "쿠팡_해외배송비율_max_pct": v_overseas_max,
                "쿠팡_평균가_min": v_price_min,
                "쿠팡_평균가_max": v_price_max,
                "쿠팡_총리뷰수_min": v_review_min,
                "쿠팡_총리뷰수_max": v_review_max,
            }
            st.session_state.presets[pkey] = {"name": new_name, "filters": new_filters}
            save_presets(st.session_state.presets)
            st.success("저장 완료!")
            st.session_state.filtered_df = None

    with sv2:
        if st.button("닫기", use_container_width=True):
            st.session_state.show_settings = False
            st.rerun()

# ──────────────────────────────────────────────
# 분석 실행
# ──────────────────────────────────────────────
if run_clicked:
    if st.session_state.df is None:
        st.warning("먼저 파일을 업로드하세요.")
    else:
        pkey = st.session_state.active_preset
        filters = get_preset_filters(st.session_state.presets, pkey)
        cmap = st.session_state.col_map
        with st.spinner("필터링 중…"):
            result, info = apply_filters(st.session_state.df, filters, cmap)
            st.session_state.filtered_df = result
            st.session_state.applied_info = info

# ──────────────────────────────────────────────
# 결과 표시
# ──────────────────────────────────────────────
if st.session_state.filtered_df is not None:
    fdf = st.session_state.filtered_df
    st.markdown(f"### 분석 결과: {len(fdf):,}건")

    # Streamlit 기본 dataframe 도구 사용 (검색, 전체화면, 다운로드 아이콘 자동 제공)
    st.dataframe(fdf, use_container_width=True, height=600)

    # 엑셀 다운로드
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        fdf.to_excel(writer, index=False)
    st.download_button(
        label="📥 엑셀 다운로드",
        data=buffer.getvalue(),
        file_name="분석결과.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    # 적용된 필터 정보
    with st.expander("적용된 필터 상세"):
        if st.session_state.applied_info:
            for info_line in st.session_state.applied_info:
                st.write(f"• {info_line}")
        else:
            st.write("적용된 필터 없음 (모든 데이터 표시)")

# ──────────────────────────────────────────────
# 디버그: 컬럼 매핑 확인
# ──────────────────────────────────────────────
with st.expander("🔧 컬럼 매핑 확인 (디버그)"):
    if st.session_state.col_map:
        for std_key, real_col in st.session_state.col_map.items():
            st.write(f"**{std_key}** → `{real_col}`")
        st.markdown("---")
        st.write("**매핑되지 않은 표준 키:**")
        for std_key in COLUMN_PATTERNS:
            if std_key not in st.session_state.col_map:
                st.write(f"❌ {std_key}")
    else:
        st.write("파일을 먼저 업로드하세요.")

    if st.session_state.df is not None:
        st.markdown("---")
        st.write("**실제 컬럼명 목록:**")
        for i, c in enumerate(st.session_state.df.columns):
            st.write(f"{i}: `{c}`")
