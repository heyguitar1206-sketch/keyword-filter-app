import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="수동끝판왕 키워드서칭머신 ver. 1.0", layout="wide")

# ───────────────────────── CSS ─────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif !important;
}

/* ── 전체 배경 ── */
.stApp { background: #dde2ef !important; }

/* ── 헤더/푸터 제거 ── */
header[data-testid="stHeader"] { display: none !important; }
footer { display: none !important; }
#MainMenu { display: none !important; }

/* ── 메인 패딩 ── */
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 1rem !important;
    max-width: 1400px !important;
}

/* ── 카드 스타일 ── */
[data-testid="stVerticalBlockBorderWrapper"] > div {
    background: #ffffff !important;
    border-radius: 14px !important;
    border: none !important;
    box-shadow: 0 2px 12px rgba(60,80,180,0.07) !important;
    padding: 1.2rem 1.5rem !important;
}

/* ── 타이틀 ── */
.app-title {
    font-size: 26px !important;
    font-weight: 900 !important;
    color: #1a2050 !important;
    letter-spacing: -0.5px !important;
    margin-bottom: 0 !important;
}

/* ── 파일 업로더 ── */
[data-testid="stFileUploader"] {
    background: #f4f6fb !important;
    border-radius: 10px !important;
    border: 1.5px dashed #b0bae8 !important;
    padding: 0.7rem 1rem !important;
}
[data-testid="stFileUploader"] label { display: none !important; }
[data-testid="stFileUploaderDropzone"] button {
    background: #3b5bff !important;
    color: #ffffff !important;
    border-radius: 8px !important;
    border: none !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    padding: 6px 20px !important;
}

/* ── 키워드필터 카드 제목 ── */
.card-title {
    font-size: 17px !important;
    font-weight: 800 !important;
    color: #1a2050 !important;
    margin-bottom: 0.3rem !important;
}

/* ═══════════════════════════════════════════════
   키워드설정 · 분석실행 버튼 – 배경 없애고 굵게
   ═══════════════════════════════════════════════ */
.btn-settings .stButton > button,
.btn-run     .stButton > button {
    all: unset !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-family: 'Noto Sans KR', sans-serif !important;
    font-size: 22px !important;
    font-weight: 900 !important;
    color: #1a2050 !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 4px 8px !important;
    min-height: 36px !important;
    width: 100% !important;
    cursor: pointer !important;
    text-decoration: none !important;
}
.btn-settings .stButton > button:hover,
.btn-run     .stButton > button:hover {
    color: #3b5bff !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
.btn-settings .stButton > button:focus,
.btn-run     .stButton > button:focus,
.btn-settings .stButton > button:active,
.btn-run     .stButton > button:active {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
}

/* ── 탭 스타일 ── */
[data-testid="stTabs"] [role="tablist"] {
    gap: 6px !important;
    border-bottom: 2px solid #dde2ef !important;
}
[data-testid="stTabs"] [role="tab"] {
    font-family: 'Noto Sans KR', sans-serif !important;
    font-size: 16px !important;
    font-weight: 800 !important;
    color: #7a84b3 !important;
    background: #f4f6fb !important;
    border-radius: 8px 8px 0 0 !important;
    padding: 6px 18px !important;
    border: none !important;
    min-width: 44px !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: #3b5bff !important;
    background: #eaedfc !important;
    border-bottom: 2px solid #3b5bff !important;
}

/* ── 필터 섹션 제목 ── */
.filter-section-title {
    font-size: 13px !important;
    font-weight: 700 !important;
    color: #3b5bff !important;
    margin: 0.7rem 0 0.2rem 0 !important;
}

/* ── 숫자 입력 width ── */
div[role="tabpanel"] [data-testid="stNumberInput"] {
    max-width: 200px !important;
}
div[role="tabpanel"] [data-testid="stNumberInput"] > div {
    max-width: 200px !important;
}

/* ── ± 버튼 크기 ── */
div[role="tabpanel"] [data-testid="stNumberInput"] button {
    background: #e8ecf8 !important;
    color: #3b5bff !important;
    border: 1px solid #c0c8de !important;
    border-radius: 5px !important;
    font-size: 13px !important;
    min-width: 22px !important;
    max-width: 22px !important;
    min-height: 22px !important;
    max-height: 22px !important;
    padding: 0 !important;
}
div[role="tabpanel"] [data-testid="stNumberInput"] button:hover {
    background: #d0d8f0 !important;
}

/* ── 저장 버튼 ── */
.stButton > button[kind="secondary"],
div[role="tabpanel"] .stButton > button {
    background: #3b5bff !important;
    color: #fff !important;
    border-radius: 8px !important;
    border: none !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    padding: 6px 22px !important;
    margin-top: 0.5rem !important;
}
div[role="tabpanel"] .stButton > button:hover {
    background: #2244dd !important;
}

/* ── 데이터프레임 ── */
[data-testid="stDataFrame"] {
    border-radius: 10px !important;
    overflow: hidden !important;
}
</style>
""", unsafe_allow_html=True)

# ───────────────── 상수 ─────────────────
DISPLAY_COLUMNS = [
    "키워드","경쟁률","작년검색량","작년최대검색월","피크월검색량",
    "계절성","계절성월","쿠팡해외배송비율(%)","쿠팡평균가","쿠팡총리뷰수",
    "쿠팡최대리뷰수","쿠팡해외배송총리뷰수","쿠팡해외배송최대리뷰수",
]
FORMAT_INT_COLUMNS = [
    "작년검색량","피크월검색량","쿠팡평균가","쿠팡총리뷰수",
    "쿠팡최대리뷰수","쿠팡해외배송총리뷰수","쿠팡해외배송최대리뷰수",
]

DEFAULT_PRESET = {
    "이름": "프리셋",
    "brand_keyword": "전체",
    "search_min": 0, "search_max": 9999999,
    "seasonality": "전체",
    "max_months": [],
    "peak_vol_min": 0, "peak_vol_max": 9999999,
    "coupang_price_min": 0, "coupang_price_max": 9999999,
    "coupang_review_min": 0, "coupang_review_max": 9999999,
    "coupang_overseas_min": 0.0, "coupang_overseas_max": 100.0,
}

def make_preset(name, **kw):
    p = DEFAULT_PRESET.copy()
    p["이름"] = name
    p.update(kw)
    return p

# ───────────────── 세션 초기화 ─────────────────
for key, val in {
    "presets": [make_preset(str(i+1)) for i in range(5)],
    "active_preset": 0,
    "df_result": None,
    "show_settings": False,
    "uploaded_file_bytes": None,
    "uploaded_file_name": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ───────────────── 유틸리티 ─────────────────
def load_excel(file_bytes):
    try:
        return pd.read_excel(io.BytesIO(file_bytes), engine="openpyxl")
    except Exception as e:
        st.error(f"엑셀 로드 실패: {e}")
        return None

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    # 1) 불필요 컬럼 삭제
    DROP_KEYWORDS = [
        "카테고리","최근1개월","최근 1개월","예상1개월","예상 1개월",
        "최근3개월","최근 3개월","예상3개월","예상 3개월","상승률","신규진입",
    ]
    drop_cols = [c for c in df.columns if any(kw in str(c) for kw in DROP_KEYWORDS)]
    df = df.drop(columns=drop_cols, errors="ignore")

    # 2) 중복 컬럼명 처리
    seen, new_cols = {}, []
    for c in df.columns:
        s = str(c).strip()
        if s in seen:
            seen[s] += 1
            new_cols.append(f"{s}_{seen[s]}")
        else:
            seen[s] = 0
            new_cols.append(s)
    df.columns = new_cols

    # 3) 컬럼 매핑
    rename, used = {}, set()
    for col in df.columns:
        c = str(col).strip()
        target = None

        # 키워드 컬럼 감지 (O/X·숫자 컬럼 제외)
        if "키워드" not in used:
            sample = df[col].dropna().astype(str).head(20)
            uniq = sample.str.strip().str.upper().unique()
            is_binary = all(v in {"O","X","TRUE","FALSE","1","0","Y","N",""} for v in uniq)
            is_numeric = pd.to_numeric(df[col].dropna().head(20), errors="coerce").notna().all()
            if (any(kw in c for kw in ["키워드","검색어","상품명","키워드명"])
                    and not is_binary and not is_numeric):
                target = "키워드"

        if not target:
            if "브랜드" in c and "브랜드키워드" not in used:
                target = "브랜드키워드"
            elif "쇼핑성" in c and "쇼핑성키워드" not in used:
                target = "쇼핑성키워드"
            elif "경쟁" in c and "경쟁률" not in used:
                target = "경쟁률"
            elif "작년" in c and "검색" in c and "작년검색량" not in used:
                target = "작년검색량"
            elif ("최대" in c or "최고" in c) and "월" in c and "작년최대검색월" not in used:
                target = "작년최대검색월"
            elif "피크" in c and "검색" in c and "피크월검색량" not in used:
                target = "피크월검색량"
            elif "계절성" in c and "월" not in c and "계절성" not in used:
                target = "계절성"
            elif "계절성" in c and "월" in c and "계절성월" not in used:
                target = "계절성월"
            elif "쿠팡" in c and "해외" in c and "배송" in c and "비율" in c and "쿠팡해외배송비율" not in used:
                target = "쿠팡해외배송비율"
            elif "쿠팡" in c and "가격" in c and "쿠팡평균가" not in used:
                target = "쿠팡평균가"
            elif "쿠팡" in c and "해외" not in c and "최대" in c and "리뷰" in c and "쿠팡최대리뷰수" not in used:
                target = "쿠팡최대리뷰수"
            elif "쿠팡" in c and "해외" not in c and "총" in c and "리뷰" in c and "쿠팡총리뷰수" not in used:
                target = "쿠팡총리뷰수"
            elif "쿠팡" in c and "해외" in c and "총" in c and "리뷰" in c and "쿠팡해외배송총리뷰수" not in used:
                target = "쿠팡해외배송총리뷰수"
            elif "쿠팡" in c and "해외" in c and "최대" in c and "리뷰" in c and "쿠팡해외배송최대리뷰수" not in used:
                target = "쿠팡해외배송최대리뷰수"

        if target:
            rename[col] = target
            used.add(target)

    df = df.rename(columns=rename)
    df = df.loc[:, ~df.columns.duplicated()]

    # 4) 해외배송비율 → % 변환
    if "쿠팡해외배송비율" in df.columns:
        raw = pd.to_numeric(df["쿠팡해외배송비율"], errors="coerce")
        # 0~1 범위면 ×100, 이미 0~100이면 그대로
        if raw.dropna().max() <= 1.0:
            raw = raw * 100
        df["쿠팡해외배송비율(%)"] = raw.round(1)
        df = df.drop(columns=["쿠팡해외배송비율"])

    # 5) DISPLAY_COLUMNS 순서로 정리
    final_cols = [c for c in DISPLAY_COLUMNS if c in df.columns]
    return df[final_cols]

def safe_numeric(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce").fillna(0)

def apply_preset(df: pd.DataFrame, preset: dict) -> pd.DataFrame:
    r = df.copy()

    # 브랜드키워드 필터
    if "브랜드키워드" in r.columns and preset["brand_keyword"] != "전체":
        want = preset["brand_keyword"] == "O"
        allowed = (["True","1","O","o","예","Y","y"] if want
                   else ["False","0","X","x","아니오","N","n"])
        r = r[r["브랜드키워드"].astype(str).str.strip().isin(allowed)]

    # 작년검색량
    if "작년검색량" in r.columns:
        v = safe_numeric(r["작년검색량"])
        r = r[(v >= preset["search_min"]) & (v <= preset["search_max"])]

    # 계절성
    if "계절성" in r.columns and preset["seasonality"] != "전체":
        r = r[r["계절성"].astype(str).str.strip() == preset["seasonality"]]

    # 작년최대검색월
    if "작년최대검색월" in r.columns and preset["max_months"]:
        r = r[r["작년최대검색월"].astype(str).str.strip().isin(
            [str(m) for m in preset["max_months"]])]

    # 피크월검색량
    if "피크월검색량" in r.columns:
        v = safe_numeric(r["피크월검색량"])
        r = r[(v >= preset["peak_vol_min"]) & (v <= preset["peak_vol_max"])]

    # 쿠팡평균가
    if "쿠팡평균가" in r.columns:
        v = safe_numeric(r["쿠팡평균가"])
        r = r[(v >= preset["coupang_price_min"]) & (v <= preset["coupang_price_max"])]

    # 쿠팡총리뷰수
    if "쿠팡총리뷰수" in r.columns:
        v = safe_numeric(r["쿠팡총리뷰수"])
        r = r[(v >= preset["coupang_review_min"]) & (v <= preset["coupang_review_max"])]

    # 쿠팡해외배송비율(%) – 0~100 기준
    if "쿠팡해외배송비율(%)" in r.columns:
        v = safe_numeric(r["쿠팡해외배송비율(%)"])
        r = r[(v >= preset["coupang_overseas_min"]) & (v <= preset["coupang_overseas_max"])]

    # 중복 키워드 제거
    if "키워드" in r.columns:
        r = r.drop_duplicates(subset=["키워드"], keep="first")

    # 쿠팡해외배송비율 내림차순
    if "쿠팡해외배송비율(%)" in r.columns:
        r = r.sort_values("쿠팡해외배송비율(%)", ascending=False)

    return r.reset_index(drop=True)

def format_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    for col in FORMAT_INT_COLUMNS:
        if col in d.columns:
            d[col] = (pd.to_numeric(d[col], errors="coerce")
                      .fillna(0).astype(int)
                      .apply(lambda x: f"{x:,}"))
    if "쿠팡해외배송비율(%)" in d.columns:
        d["쿠팡해외배송비율(%)"] = (
            pd.to_numeric(d["쿠팡해외배송비율(%)"], errors="coerce")
            .fillna(0).apply(lambda x: f"{x:.1f}%"))
    return d

# ───────────────── 설정 패널 ─────────────────
def render_settings_panel(idx: int):
    p = st.session_state.presets[idx]
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<p class="filter-section-title">(1) 브랜드 키워드</p>', unsafe_allow_html=True)
        brand = st.radio(
            "브랜드키워드", ["전체","O","X"],
            index=["전체","O","X"].index(p["brand_keyword"]),
            horizontal=True, key=f"brand_{idx}", label_visibility="collapsed"
        )

        st.markdown('<p class="filter-section-title">(2) 작년검색량</p>', unsafe_allow_html=True)
        s_min = st.number_input("최소", value=int(p["search_min"]), min_value=0, step=1000, key=f"smin_{idx}")
        s_max = st.number_input("최대", value=int(p["search_max"]), min_value=0, step=1000, key=f"smax_{idx}")

        st.markdown('<p class="filter-section-title">(3) 계절성</p>', unsafe_allow_html=True)
        seasonality = st.radio(
            "계절성", ["전체","Y","N"],
            index=["전체","Y","N"].index(p["seasonality"]),
            horizontal=True, key=f"season_{idx}", label_visibility="collapsed"
        )

        st.markdown('<p class="filter-section-title">(4) 작년최대검색월</p>', unsafe_allow_html=True)
        all_months = [str(i) for i in range(1, 13)]
        sel_months = st.multiselect(
            "월 선택", all_months,
            default=p["max_months"], key=f"months_{idx}", label_visibility="collapsed"
        )

        st.markdown('<p class="filter-section-title">(5) 피크월검색량</p>', unsafe_allow_html=True)
        peak_min = st.number_input("최소", value=int(p["peak_vol_min"]), min_value=0, step=1000, key=f"pkmin_{idx}")
        peak_max = st.number_input("최대", value=int(p["peak_vol_max"]), min_value=0, step=1000, key=f"pkmax_{idx}")

    with col_b:
        st.markdown('<p class="filter-section-title">(6) 쿠팡평균가</p>', unsafe_allow_html=True)
        cp_min = st.number_input("최소 (원)", value=int(p["coupang_price_min"]), min_value=0, step=1000, key=f"cpmin_{idx}")
        cp_max = st.number_input("최대 (원)", value=int(p["coupang_price_max"]), min_value=0, step=1000, key=f"cpmax_{idx}")

        st.markdown('<p class="filter-section-title">(7) 쿠팡총리뷰수</p>', unsafe_allow_html=True)
        cr_min = st.number_input("최소", value=int(p["coupang_review_min"]), min_value=0, step=100, key=f"crmin_{idx}")
        cr_max = st.number_input("최대", value=int(p["coupang_review_max"]), min_value=0, step=100, key=f"crmax_{idx}")

        st.markdown('<p class="filter-section-title">(8) 쿠팡해외배송비율 (%)</p>', unsafe_allow_html=True)
        co_min = st.number_input("최소 (%)", value=float(p["coupang_overseas_min"]),
                                  min_value=0.0, max_value=100.0, step=1.0, key=f"comin_{idx}")
        co_max = st.number_input("최대 (%)", value=float(p["coupang_overseas_max"]),
                                  min_value=0.0, max_value=100.0, step=1.0, key=f"comax_{idx}")

    if st.button("💾 저장", key=f"save_{idx}"):
        st.session_state.presets[idx].update({
            "brand_keyword": brand,
            "search_min": s_min, "search_max": s_max,
            "seasonality": seasonality,
            "max_months": sel_months,
            "peak_vol_min": peak_min, "peak_vol_max": peak_max,
            "coupang_price_min": cp_min, "coupang_price_max": cp_max,
            "coupang_review_min": cr_min, "coupang_review_max": cr_max,
            "coupang_overseas_min": co_min, "coupang_overseas_max": co_max,
        })
        st.success(f"✅ 프리셋 {idx+1} 저장 완료!")

# ───────────────── 메인 UI ─────────────────
with st.container(border=True):
    st.markdown('<p class="app-title">🚀 수동끝판왕 키워드서칭머신 ver. 1.0</p>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "네이버 쇼핑 키워드 엑셀 파일을 업로드하세요 (.xlsx)",
        type=["xlsx"], key="file_uploader", label_visibility="collapsed"
    )
    if uploaded_file:
        st.session_state.uploaded_file_bytes = uploaded_file.read()
        st.session_state.uploaded_file_name  = uploaded_file.name

    if st.session_state.uploaded_file_name:
        st.caption(f"📂 {st.session_state.uploaded_file_name}")

    # ── 버튼 행 (키워드설정 | 분석실행) ──
    _, col_set, col_run, _ = st.columns([3, 2, 2, 3])

    with col_set:
        st.markdown('<div class="btn-settings">', unsafe_allow_html=True)
        if st.button("⚙️ 키워드설정", key="toggle_settings"):
            st.session_state.show_settings = not st.session_state.show_settings
        st.markdown('</div>', unsafe_allow_html=True)

    with col_run:
        st.markdown('<div class="btn-run">', unsafe_allow_html=True)
        run_btn = st.button("🔍 분석실행", key="run_analysis")
        st.markdown('</div>', unsafe_allow_html=True)

# ── 설정 패널 ──
if st.session_state.show_settings:
    with st.container(border=True):
        st.markdown('<p class="card-title">⚙️ 키워드 필터 설정</p>', unsafe_allow_html=True)
        tab_labels = [str(i+1) for i in range(5)]
        tabs = st.tabs(tab_labels)
        for i, tab in enumerate(tabs):
            with tab:
                render_settings_panel(i)
        st.session_state.active_preset = 0   # 기본 프리셋 0번 사용

# ── 분석 실행 ──
if run_btn:
    if not st.session_state.uploaded_file_bytes:
        st.warning("⚠️ 먼저 엑셀 파일을 업로드하세요.")
    else:
        with st.spinner("⏳ 분석 중..."):
            df_raw = load_excel(st.session_state.uploaded_file_bytes)
            if df_raw is not None:
                df_norm = normalize_columns(df_raw)
                preset  = st.session_state.presets[st.session_state.active_preset]
                st.session_state.df_result = apply_preset(df_norm, preset)
        if st.session_state.df_result is not None:
            st.success(f"✅ 분석 완료: {len(st.session_state.df_result):,}개 키워드")

# ── 결과 테이블 ──
if st.session_state.df_result is not None:
    df      = st.session_state.df_result
    row_cnt = len(df)
    ROW_H, HEADER_H = 35, 38
    height  = min(1100, max(400, HEADER_H + row_cnt * ROW_H))
    with st.container(border=True):
        st.markdown(f'<p class="card-title">📊 분석 결과 ({row_cnt:,}개)</p>', unsafe_allow_html=True)
        st.dataframe(format_dataframe(df), use_container_width=True, height=height)
