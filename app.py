import streamlit as st
import pandas as pd
import json
import os
import re
import io

# ──────────────────────────────────────────────
# 페이지 설정
# ──────────────────────────────────────────────
st.set_page_config(page_title="키워드 분석 도구", page_icon="🔍", layout="wide")
st.markdown(
    "<style>"
    "section.main .block-container{max-width:95%;padding-top:1rem;}"
    "#MainMenu,footer,header{visibility:hidden;}"
    "</style>",
    unsafe_allow_html=True,
)

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
# 엑셀 로딩 (자동 헤더 감지)
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
    raw = pd.read_excel(uploaded, header=None, nrows=10)
    n_rows, n_cols = raw.shape
    header_row_count = 1
    for r in range(min(n_rows, 5)):
        row_vals = raw.iloc[r]
        header_like = sum(1 for v in row_vals if is_header_text(v))
        if header_like >= max(1, n_cols * 0.3):
            header_row_count = r + 1

    header_parts = []
    for r in range(header_row_count):
        header_parts.append(raw.iloc[r])

    col_names = []
    for c in range(n_cols):
        parts = []
        for r in range(header_row_count):
            v = header_parts[r].iloc[c]
            if is_header_text(v):
                parts.append(str(v).strip())
        name = "_".join(parts) if parts else f"col_{c}"
        col_names.append(name)

    # 유니크 보장
    seen = {}
    unique_names = []
    for nm in col_names:
        if nm in seen:
            seen[nm] += 1
            unique_names.append(f"{nm}_{seen[nm]}")
        else:
            seen[nm] = 0
            unique_names.append(nm)

    df = pd.read_excel(uploaded, header=None, skiprows=header_row_count)
    df.columns = unique_names[: len(df.columns)]

    for col in df.columns:
        converted = pd.to_numeric(df[col], errors="coerce")
        if converted.notna().sum() > len(df) * 0.3:
            df[col] = converted

    return df


# ──────────────────────────────────────────────
# 컬럼 매핑
# ──────────────────────────────────────────────
COLUMN_PATTERNS = {
    "브랜드키워드": ["브랜드", "brand"],
    "쇼핑성키워드": ["쇼핑성", "shopping"],
    "작년검색량": ["작년", "검색량"],
    "작년최대검색월": ["작년", "최대", "검색월"],
    "작년최대검색월검색량": ["작년", "최대", "검색월", "검색량"],
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

    # ① 키워드 컬럼: 인덱스 1번 우선, 정확한 이름 있으면 덮어씀
    if len(col_list) > 1:
        cmap["키워드"] = col_list[1]
    for real_col in col_list:
        if real_col.strip() == "키워드":
            cmap["키워드"] = real_col
            break

    used = set(cmap.values())

    # ② 패턴 매칭
    for std_key, keywords in COLUMN_PATTERNS.items():
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
    """표시용 DataFrame – 숫자는 숫자 타입 그대로 유지 (정렬 지원)"""
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

    # 브랜드키워드
    val = filters.get("브랜드키워드", "전체")
    if val != "전체" and "브랜드키워드" in cmap:
        col = cmap["브랜드키워드"]
        if col in out.columns:
            target = "O" if val == "O" else "X"
            out = out[out[col].astype(str).str.strip().str.upper() == target]
            applied.append(f"브랜드키워드={target}")

    # 쇼핑성키워드
    val = filters.get("쇼핑성키워드", "전체")
    if val != "전체" and "쇼핑성키워드" in cmap:
        col = cmap["쇼핑성키워드"]
        if col in out.columns:
            target = "O" if val == "O" else "X"
            out = out[out[col].astype(str).str.strip().str.upper() == target]
            applied.append(f"쇼핑성키워드={target}")

    # 계절성
    val = filters.get("계절성", "전체")
    if val != "전체" and "계절성" in cmap:
        col = cmap["계절성"]
        if col in out.columns:
            if val == "O":
                out = out[out[col].astype(str).str.strip().isin(["있음", "O", "TRUE", "1"])]
            else:
                out = out[out[col].astype(str).str.strip().isin(["없음", "X", "FALSE", "0"])]
            applied.append(f"계절성={val}")

    # 숫자 범위 필터
    def numeric_range(key, lo_key, hi_key, divisor=1):
        lo = safe_float(filters.get(lo_key, 0))
        hi = safe_float(filters.get(hi_key, 0))
        if (lo > 0 or hi > 0) and key in cmap:
            col = cmap[key]
            if col in out.columns:
                series = pd.to_numeric(out[col], errors="coerce")
                if divisor != 1:
                    lo_real = lo / divisor
                    hi_real = hi / divisor if hi > 0 else None
                else:
                    lo_real = lo
                    hi_real = hi if hi > 0 else None
                mask = pd.Series(True, index=out.index)
                if lo_real > 0:
                    mask = mask & (series >= lo_real)
                if hi_real is not None and hi_real > 0:
                    mask = mask & (series <= hi_real)
                nonlocal applied
                out_before = len(out)
                filtered = out[mask.reindex(out.index, fill_value=False)]
                label = key
                if divisor != 1:
                    applied.append(f"{label} {lo}%~{hi}%")
                else:
                    applied.append(f"{label} {lo:,}~{hi:,}")
                return filtered
        return out

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

    # 작년최대검색월
    months = filters.get("작년최대검색월", [])
    if months and "작년최대검색월" in cmap:
        col = cmap["작년최대검색월"]
        if col in out.columns:
            month_ints = [safe_int(m) for m in months]
            series = pd.to_numeric(out[col], errors="coerce")
            out = out[series.isin(month_ints)]
            applied.append(f"작년최대검색월={months}")

    # 쿠팡해외배송비율 기준 내림차순 정렬
    if "쿠팡해외배송비율" in cmap:
        col = cmap["쿠팡해외배송비율"]
        if col in out.columns:
            sort_series = pd.to_numeric(out[col], errors="coerce")
            out = out.iloc[sort_series.fillna(-1).values.argsort()[::-1]]

    # 키워드 중복 제거
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
# 세션 상태 초기화
# ──────────────────────────────────────────────
if "presets" not in st.session_state:
    st.session_state["presets"] = load_presets()
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
# UI: 파일 업로드
# ──────────────────────────────────────────────
st.title("🔍 키워드 분석 도구")
uploaded = st.file_uploader("엑셀/CSV 파일 업로드", type=["xlsx", "xls", "csv"])

if uploaded:
    if st.session_state["df_raw"] is None or st.session_state.get("_fname") != uploaded.name:
        with st.spinner("파일 로딩 중..."):
            if uploaded.name.endswith(".csv"):
                df = pd.read_csv(uploaded)
            else:
                df = load_excel(uploaded)
            st.session_state["df_raw"] = df
            st.session_state["cmap"] = build_col_map(df.columns)
            st.session_state["_fname"] = uploaded.name
        st.success(f"✅ {uploaded.name} 로드 완료 ({len(df):,}행, {len(df.columns)}열)")

# ──────────────────────────────────────────────
# UI: 프리셋 선택 바
# ──────────────────────────────────────────────
cols = st.columns([1, 1, 1, 0.5])
for i in range(3):
    with cols[i]:
        c1, c2 = st.columns([4, 1])
        with c1:
            label = get_preset_name(i)
            if st.button(label, key=f"btn_preset_{i}", use_container_width=True):
                st.session_state["active_preset"] = i
                st.session_state["show_settings"] = False
        with c2:
            if st.button("⚙️", key=f"btn_gear_{i}"):
                st.session_state["active_preset"] = i
                st.session_state["show_settings"] = not st.session_state["show_settings"]

active = st.session_state["active_preset"]
st.caption(f"현재 선택: **{get_preset_name(active)}**")

# ──────────────────────────────────────────────
# UI: 프리셋 설정
# ──────────────────────────────────────────────
if st.session_state["show_settings"]:
    with st.expander(f"⚙️ {get_preset_name(active)} 설정", expanded=True):
        f = get_preset_filters(active)

        new_name = st.text_input("프리셋 이름", value=get_preset_name(active), key="inp_name")

        c1, c2, c3 = st.columns(3)
        with c1:
            brand = st.radio("브랜드키워드", ["전체", "O", "X"], index=["전체", "O", "X"].index(f.get("브랜드키워드", "전체")), key="inp_brand", horizontal=True)
        with c2:
            shopping = st.radio("쇼핑성키워드", ["전체", "O", "X"], index=["전체", "O", "X"].index(f.get("쇼핑성키워드", "전체")), key="inp_shopping", horizontal=True)
        with c3:
            season = st.radio("계절성", ["전체", "O", "X"], index=["전체", "O", "X"].index(f.get("계절성", "전체")), key="inp_season", horizontal=True)

        c1, c2 = st.columns(2)
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

        c1, c2 = st.columns(2)
        with c1:
            p_lo = st.number_input("피크월검색량 (최소)", value=safe_int(f.get("피크월검색량_lo")), min_value=0, step=100, key="inp_peak_lo")
        with c2:
            p_hi = st.number_input("피크월검색량 (최대, 0=무제한)", value=safe_int(f.get("피크월검색량_hi")), min_value=0, step=100, key="inp_peak_hi")

        c1, c2 = st.columns(2)
        with c1:
            o_lo = st.number_input("쿠팡해외배송비율 % (최소)", value=safe_float(f.get("쿠팡해외배송비율_lo")), min_value=0.0, step=1.0, format="%.1f", key="inp_overseas_lo")
        with c2:
            o_hi = st.number_input("쿠팡해외배송비율 % (최대, 0=무제한)", value=safe_float(f.get("쿠팡해외배송비율_hi")), min_value=0.0, step=1.0, format="%.1f", key="inp_overseas_hi")

        c1, c2 = st.columns(2)
        with c1:
            a_lo = st.number_input("쿠팡평균가 (최소)", value=safe_int(f.get("쿠팡평균가_lo")), min_value=0, step=1000, key="inp_avg_lo")
        with c2:
            a_hi = st.number_input("쿠팡평균가 (최대, 0=무제한)", value=safe_int(f.get("쿠팡평균가_hi")), min_value=0, step=1000, key="inp_avg_hi")

        c1, c2 = st.columns(2)
        with c1:
            r_lo = st.number_input("쿠팡총리뷰수 (최소)", value=safe_int(f.get("쿠팡총리뷰수_lo")), min_value=0, step=10, key="inp_review_lo")
        with c2:
            r_hi = st.number_input("쿠팡총리뷰수 (최대, 0=무제한)", value=safe_int(f.get("쿠팡총리뷰수_hi")), min_value=0, step=10, key="inp_review_hi")

        bc1, bc2 = st.columns(2)
        with bc1:
            if st.button("💾 저장", key="btn_save", use_container_width=True):
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
                save_presets(st.session_state["presets"])
                st.success("저장 완료!")
        with bc2:
            if st.button("❌ 닫기", key="btn_close", use_container_width=True):
                st.session_state["show_settings"] = False
                st.rerun()

# ──────────────────────────────────────────────
# UI: 분석 실행
# ──────────────────────────────────────────────
if st.button("▶ 분석 실행", use_container_width=True, type="primary"):
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

    st.subheader(f"📊 분석 결과 ({len(display_df):,}건)")

    # ── column_config 생성 (숫자 타입 유지 → 헤더 클릭 정렬 정상 동작) ──
    col_config = {}
    for spec in DISPLAY_COLUMNS:
        label = spec.get("label", spec["key"])
        fmt = spec.get("format")
        if label not in display_df.columns:
            continue
        if fmt == "int":
            col_config[label] = st.column_config.NumberColumn(
                label, format="%d"
            )
        elif fmt == "pct":
            col_config[label] = st.column_config.NumberColumn(
                label, format="%.1f%%"
            )

    st.dataframe(
        display_df,
        column_config=col_config,
        hide_index=True,
        use_container_width=True,
    )

    # ── 다운로드 (Excel에는 사람이 보기 좋은 포맷 적용) ──
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

    # 적용된 필터
    with st.expander("🔎 적용된 필터 상세"):
        if st.session_state["applied_info"]:
            for a in st.session_state["applied_info"]:
                st.write(f"• {a}")
        else:
            st.write("적용된 필터 없음")

# ──────────────────────────────────────────────
# 디버그
# ──────────────────────────────────────────────
if st.session_state["df_raw"] is not None:
    with st.expander("🛠 컬럼 매핑 확인 (디버그)"):
        cmap = st.session_state["cmap"]
        st.write("**매핑된 키:**")
        for k, v in cmap.items():
            st.write(f"  `{k}` → `{v}`")
        all_keys = set(COLUMN_PATTERNS.keys()) | {"키워드"}
        unmapped = all_keys - set(cmap.keys())
        if unmapped:
            st.write("**미매핑 키:**", unmapped)
        st.write("**실제 컬럼 목록:**")
        st.write(list(st.session_state["df_raw"].columns))
