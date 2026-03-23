import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="끝장캐리 키워드 분석", layout="wide")

# ────────────────────────────────────────────────────────────────
# CSS
# ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800;900&display=swap');

*, *::before, *::after { font-family: 'Noto Sans KR', sans-serif !important; box-sizing: border-box; }
[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"], footer { display: none !important; }
.stApp, body { background: #dde2ef !important; }
.block-container { max-width: 60% !important; margin: 0 auto !important; padding: 32px 0 60px !important; }

/* Card */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff !important;
    border: 2px solid #b8c0d8 !important;
    border-radius: 16px !important;
    box-shadow: 0 4px 18px rgba(60,80,180,0.13) !important;
    padding: 20px 24px !important;
    margin-bottom: 16px !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: #f5f7ff !important;
    border: 2px dashed #a0aad4 !important;
    border-radius: 12px !important;
    padding: 0 !important;
    overflow: hidden !important;
    min-height: 90px !important;
}
[data-testid="stFileUploaderDropzone"] {
    background: transparent !important;
    border: none !important;
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    justify-content: space-between !important;
    gap: 16px !important;
    padding: 20px 24px !important;
    min-height: 90px !important;
    width: 100% !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] {
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    gap: 12px !important;
    flex: 1 !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] span {
    font-size: 13px !important;
    color: #6672a0 !important;
}
[data-testid="stFileUploaderDropzone"] button {
    background: #3b5bff !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    padding: 9px 24px !important;
    min-height: 40px !important;
    min-width: 120px !important;
    cursor: pointer !important;
    flex-shrink: 0 !important;
    margin: 0 !important;
    white-space: nowrap !important;
}
[data-testid="stFileUploaderDropzone"] button:hover { background: #2a47e0 !important; }

/* Top three buttons – text only */
.btn-settings .stButton > button,
.btn-run .stButton > button,
.btn-download .stButton > button,
.btn-download [data-testid="stDownloadButton"] > button {
    all: unset !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-family: 'Noto Sans KR', sans-serif !important;
    font-size: 14px !important;
    font-weight: 800 !important;
    color: #3a3f5c !important;
    background: transparent !important;
    border: none !important;
    padding: 4px 8px !important;
    min-height: 36px !important;
    width: 100% !important;
    cursor: pointer !important;
}
.btn-settings .stButton > button:hover { color: #3b5bff !important; }
.btn-run .stButton > button { color: #3b5bff !important; }
.btn-run .stButton > button:hover { color: #1a3bcc !important; }
.btn-download .stButton > button:hover,
.btn-download [data-testid="stDownloadButton"] > button:hover { color: #3b5bff !important; }
.btn-download .stButton > button:disabled { color: #b0b8d0 !important; cursor: default !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 6px !important; border-bottom: 2px solid #e0e4f0 !important; }
.stTabs [data-baseweb="tab"] {
    font-size: 15px !important;
    font-weight: 800 !important;
    color: #6672a0 !important;
    border-radius: 10px 10px 0 0 !important;
    padding: 8px 20px !important;
    background: transparent !important;
}
.stTabs [aria-selected="true"] {
    color: #3b5bff !important;
    border-bottom: 3px solid #3b5bff !important;
    background: #f0f3ff !important;
}
div[role="tabpanel"] {
    background: #ffffff !important;
    border-radius: 0 12px 12px 12px !important;
    padding: 16px 8px !important;
}

/* Filter section titles */
.filter-section-title {
    font-size: 14px !important;
    font-weight: 800 !important;
    color: #3a3f5c !important;
    margin: 14px 0 6px 0 !important;
    padding-bottom: 4px !important;
    border-bottom: 1.5px solid #e8ecf4 !important;
}

/* Widget font size inside tabs */
div[role="tabpanel"] label,
div[role="tabpanel"] .stRadio label,
div[role="tabpanel"] .stCheckbox label,
div[role="tabpanel"] .stNumberInput label,
div[role="tabpanel"] .stSelectbox label,
div[role="tabpanel"] .stMultiSelect label {
    font-size: 11px !important;
    color: #6672a0 !important;
}

/* Number input styling */
div[role="tabpanel"] [data-testid="stNumberInput"] input {
    background: #ffffff !important;
    border: 1.5px solid #c0c8de !important;
    border-radius: 10px !important;
    font-size: 12px !important;
    padding: 6px 10px !important;
}
div[role="tabpanel"] [data-testid="stNumberInput"] button {
    background: #3b5bff !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    min-width: 28px !important;
    min-height: 28px !important;
    cursor: pointer !important;
}
div[role="tabpanel"] [data-testid="stNumberInput"] button:hover { background: #2a47e0 !important; }
div[role="tabpanel"] [data-testid="stNumberInput"] button:focus { outline: 2px solid #3b5bff !important; box-shadow: 0 0 0 3px rgba(59,91,255,0.18) !important; }
</style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────────────────────
# 삭제할 컬럼 키워드 목록 (이 키워드가 포함된 컬럼은 무조건 삭제)
# ────────────────────────────────────────────────────────────────
DROP_COL_KEYWORDS = [
    "카테고리",
    "최근1개월", "최근 1개월",
    "예상1개월", "예상 1개월",
    "최근3개월", "최근 3개월",
    "예상3개월", "예상 3개월",
    "상승률",
]

def should_drop(col_name: str) -> bool:
    return any(kw in str(col_name) for kw in DROP_COL_KEYWORDS)

# ────────────────────────────────────────────────────────────────
# 기본 프리셋
# ────────────────────────────────────────────────────────────────
DEFAULT_PRESET = {
    "이름": "프리셋",
    "brand_keyword": "전체",
    "search_min": 0,
    "search_max": 9999999,
    "seasonality": "전체",
    "max_months": [],
    "peak_vol_min": 0,
    "peak_vol_max": 9999999,
    "coupang_price_min": 0,
    "coupang_price_max": 9999999,
    "coupang_review_min": 0,
    "coupang_review_max": 9999999,
    "coupang_overseas_min": 0,
    "coupang_overseas_max": 100,
}

def make_preset(name, **kw):
    p = DEFAULT_PRESET.copy()
    p["이름"] = name
    p.update(kw)
    return p

# ────────────────────────────────────────────────────────────────
# 세션 상태 초기화
# ────────────────────────────────────────────────────────────────
if "presets" not in st.session_state:
    st.session_state.presets = [make_preset(str(i + 1)) for i in range(5)]
if "active_preset" not in st.session_state:
    st.session_state.active_preset = 0
if "df_result" not in st.session_state:
    st.session_state.df_result = None
if "show_settings" not in st.session_state:
    st.session_state.show_settings = False
if "uploaded_file_bytes" not in st.session_state:
    st.session_state.uploaded_file_bytes = None
if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None

# ────────────────────────────────────────────────────────────────
# 유틸리티 함수
# ────────────────────────────────────────────────────────────────
def load_excel(file_bytes):
    try:
        return pd.read_excel(io.BytesIO(file_bytes), engine="openpyxl")
    except Exception as e:
        st.error(f"엑셀 로드 실패: {e}")
        return None


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    컬럼명을 표준화하고, 요청된 불필요한 컬럼을 삭제한다.
    중복 컬럼명이 있으면 suffix(_1, _2, …)를 붙여 처리.
    """
    # 1) 중복 컬럼 처리
    seen = {}
    new_cols = []
    for c in df.columns:
        c_str = str(c)
        if c_str in seen:
            seen[c_str] += 1
            new_cols.append(f"{c_str}_{seen[c_str]}")
        else:
            seen[c_str] = 0
            new_cols.append(c_str)
    df.columns = new_cols

    # 2) 불필요한 컬럼 먼저 삭제
    cols_to_drop = [c for c in df.columns if should_drop(c)]
    df = df.drop(columns=cols_to_drop, errors="ignore")

    # 3) 표준 컬럼명 매핑
    #    우선순위: 정확한 매칭 → 포함 매칭
    #    "키워드" 컬럼은 반드시 순수 텍스트 키워드 컬럼만 매핑 (브랜드·쇼핑성·계절성 등 제외)
    rename = {}
    used_targets = set()

    KEYWORD_EXCLUDE = ["브랜드", "쇼핑성", "계절", "쿠팡", "검색", "리뷰", "가격", "배송", "비율", "순위", "월"]

    for col in df.columns:
        c = str(col).strip()
        target = None

        # 키워드 (순수 텍스트 키워드 컬럼)
        if "키워드" in c and "키워드" not in used_targets:
            if not any(ex in c for ex in KEYWORD_EXCLUDE):
                target = "키워드"

        # 브랜드키워드
        elif "브랜드" in c and "브랜드키워드" not in used_targets:
            target = "브랜드키워드"

        # 작년검색량 (연간검색량)
        elif "작년검색량" not in used_targets and (
            ("작년" in c and "검색량" in c) or
            ("연간" in c and "검색량" in c) or
            (c == "검색량합계") or
            ("검색량" in c and "합" in c)
        ):
            target = "작년검색량"

        # 계절성
        elif "계절성" not in used_targets and ("계절성" in c or ("계절" in c and "성" in c)):
            target = "계절성"

        # 작년최대검색월
        elif "작년최대검색월" not in used_targets and (
            ("최대" in c and "월" in c) or
            ("작년" in c and "최대" in c and "월" in c)
        ):
            target = "작년최대검색월"

        # 피크월검색량 (작년최대검색월검색량)
        elif "피크월검색량" not in used_targets and (
            ("최대" in c and "검색량" in c) or
            ("피크" in c and "검색량" in c) or
            ("작년" in c and "최대" in c and "검색량" in c)
        ):
            target = "피크월검색량"

        # 쿠팡평균가
        elif "쿠팡평균가" not in used_targets and (
            ("쿠팡" in c and "가격" in c) or
            ("쿠팡" in c and "평균" in c) or
            ("쿠팡" in c and "가" in c and "평균" in c)
        ):
            target = "쿠팡평균가"

        # 쿠팡총리뷰수
        elif "쿠팡총리뷰수" not in used_targets and (
            ("쿠팡" in c and "리뷰" in c) or
            ("리뷰" in c and "수" in c)
        ):
            target = "쿠팡총리뷰수"

        # 쿠팡해외배송비율
        elif "쿠팡해외배송비율" not in used_targets and (
            ("쿠팡" in c and "해외" in c) or
            ("해외" in c and "배송" in c)
        ):
            target = "쿠팡해외배송비율"

        if target and col not in rename:
            rename[col] = target
            used_targets.add(target)

    df = df.rename(columns=rename)
    df = df.loc[:, ~df.columns.duplicated()]
    return df


def safe_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(0)


def apply_preset(df: pd.DataFrame, preset: dict) -> pd.DataFrame:
    r = df.copy()

    # 브랜드키워드
    if "브랜드키워드" in r.columns and preset["brand_keyword"] != "전체":
        want = True if preset["brand_keyword"] == "O" else False
        r = r[r["브랜드키워드"].astype(str).str.strip().isin(
            ["True", "1", "O", "o", "예", "Y", "y"] if want else
            ["False", "0", "X", "x", "아니오", "N", "n"]
        )]

    # 작년검색량
    if "작년검색량" in r.columns:
        col = safe_numeric(r["작년검색량"])
        r = r[(col >= preset["search_min"]) & (col <= preset["search_max"])]

    # 계절성
    if "계절성" in r.columns and preset["seasonality"] != "전체":
        want = True if preset["seasonality"] == "있음" else False
        r = r[r["계절성"].astype(str).str.strip().isin(
            ["True", "1", "O", "o", "있음", "Y", "y"] if want else
            ["False", "0", "X", "x", "없음", "N", "n"]
        )]

    # 작년최대검색월
    if "작년최대검색월" in r.columns and preset["max_months"]:
        month_nums = [int(m.replace("월", "")) for m in preset["max_months"]]
        r = r[safe_numeric(r["작년최대검색월"]).isin(month_nums)]

    # 피크월검색량
    if "피크월검색량" in r.columns:
        col = safe_numeric(r["피크월검색량"])
        r = r[(col >= preset["peak_vol_min"]) & (col <= preset["peak_vol_max"])]

    # 쿠팡평균가
    if "쿠팡평균가" in r.columns:
        col = safe_numeric(r["쿠팡평균가"])
        r = r[(col >= preset["coupang_price_min"]) & (col <= preset["coupang_price_max"])]

    # 쿠팡총리뷰수
    if "쿠팡총리뷰수" in r.columns:
        col = safe_numeric(r["쿠팡총리뷰수"])
        r = r[(col >= preset["coupang_review_min"]) & (col <= preset["coupang_review_max"])]

    # 쿠팡해외배송비율 (0~100% 단위로 저장, 비교 시 /100)
    if "쿠팡해외배송비율" in r.columns:
        col = safe_numeric(r["쿠팡해외배송비율"])
        o_min = preset["coupang_overseas_min"] / 100.0
        o_max = preset["coupang_overseas_max"] / 100.0
        r = r[(col >= o_min) & (col <= o_max)]

    r = r.reset_index(drop=True)
    return r


# ────────────────────────────────────────────────────────────────
# 설정 패널 렌더링
# ────────────────────────────────────────────────────────────────
def render_settings_panel(idx: int):
    p = st.session_state.presets[idx]

    col_a, col_b = st.columns(2)

    with col_a:
        # (1) 브랜드 키워드
        st.markdown('<p class="filter-section-title">(1) 브랜드 키워드</p>', unsafe_allow_html=True)
        brand = st.radio(
            "브랜드키워드", ["전체", "O", "X"],
            index=["전체", "O", "X"].index(p["brand_keyword"]),
            horizontal=True, key=f"brand_{idx}", label_visibility="collapsed"
        )

        # (2) 작년검색량
        st.markdown('<p class="filter-section-title">(2) 작년검색량</p>', unsafe_allow_html=True)
        s_min = st.number_input("최소", value=int(p["search_min"]), min_value=0, step=1000, key=f"smin_{idx}")
        s_max = st.number_input("최대", value=int(p["search_max"]), min_value=0, step=1000, key=f"smax_{idx}")

        # (3) 계절성
        st.markdown('<p class="filter-section-title">(3) 계절성</p>', unsafe_allow_html=True)
        seasonality = st.radio(
            "계절성", ["전체", "있음", "없음"],
            index=["전체", "있음", "없음"].index(p["seasonality"]),
            horizontal=True, key=f"seas_{idx}", label_visibility="collapsed"
        )

        # (4) 작년최대검색월
        st.markdown('<p class="filter-section-title">(4) 작년최대검색월</p>', unsafe_allow_html=True)
        months_labels = [f"{m}월" for m in range(1, 13)]
        month_rows = [months_labels[i:i+6] for i in range(0, 12, 6)]
        sel_months = list(p["max_months"])
        for row in month_rows:
            cols = st.columns(6)
            for j, m in enumerate(row):
                with cols[j]:
                    checked = st.checkbox(m, value=(m in sel_months), key=f"month_{idx}_{m}")
                    if checked and m not in sel_months:
                        sel_months.append(m)
                    elif not checked and m in sel_months:
                        sel_months.remove(m)

    with col_b:
        # (5) 피크월검색량
        st.markdown('<p class="filter-section-title">(5) 피크월검색량</p>', unsafe_allow_html=True)
        peak_min = st.number_input("최소", value=int(p["peak_vol_min"]), min_value=0, step=1000, key=f"pvmin_{idx}")
        peak_max = st.number_input("최대", value=int(p["peak_vol_max"]), min_value=0, step=1000, key=f"pvmax_{idx}")

        # (6) 쿠팡평균가
        st.markdown('<p class="filter-section-title">(6) 쿠팡평균가</p>', unsafe_allow_html=True)
        cp_min = st.number_input("최소 (원)", value=int(p["coupang_price_min"]), min_value=0, step=1000, key=f"cpmin_{idx}")
        cp_max = st.number_input("최대 (원)", value=int(p["coupang_price_max"]), min_value=0, step=1000, key=f"cpmax_{idx}")

        # (7) 쿠팡총리뷰수
        st.markdown('<p class="filter-section-title">(7) 쿠팡총리뷰수</p>', unsafe_allow_html=True)
        cr_min = st.number_input("최소", value=int(p["coupang_review_min"]), min_value=0, step=100, key=f"crmin_{idx}")
        cr_max = st.number_input("최대", value=int(p["coupang_review_max"]), min_value=0, step=100, key=f"crmax_{idx}")

        # (8) 쿠팡해외배송비율
        st.markdown('<p class="filter-section-title">(8) 쿠팡해외배송비율</p>', unsafe_allow_html=True)
        co_min = st.number_input("최소 (%)", value=int(p["coupang_overseas_min"]), min_value=0, max_value=100, step=1, key=f"comin_{idx}")
        co_max = st.number_input("최대 (%)", value=int(p["coupang_overseas_max"]), min_value=0, max_value=100, step=1, key=f"comax_{idx}")

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
        st.success(f"✅ 프리셋 {idx + 1} 저장 완료!")


# ────────────────────────────────────────────────────────────────
# 메인 UI
# ────────────────────────────────────────────────────────────────

# 헤더
with st.container(border=True):
    st.markdown(
        "<h2 style='margin:0;color:#1a2050;font-size:22px;font-weight:900;'>🚀 끝장캐리 키워드 분석</h2>"
        "<p style='margin:4px 0 0;color:#6672a0;font-size:13px;'>네이버 쇼핑 키워드 데이터를 분석합니다.</p>",
        unsafe_allow_html=True
    )

# 파일 업로더
with st.container(border=True):
    st.markdown("<p style='font-size:15px;font-weight:800;color:#1a2050;margin-bottom:8px;'>📂 엑셀 파일 업로드</p>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "네이버 쇼핑 키워드 엑셀 파일을 업로드하세요 (.xlsx)",
        type=["xlsx"],
        label_visibility="collapsed",
        key="file_uploader"
    )
    if uploaded_file is not None:
        st.session_state.uploaded_file_bytes = uploaded_file.read()
        st.session_state.uploaded_file_name = uploaded_file.name
    if st.session_state.uploaded_file_bytes:
        st.success(f"✅ 파일 로드됨: {st.session_state.uploaded_file_name}")

# 키워드 필터 카드 (버튼 + 설정 패널)
with st.container(border=True):
    col_label, col_sp, col_s, col_r, col_d = st.columns([3, 1, 2, 2, 2])

    with col_label:
        st.markdown(
            "<p style='font-size:15px;font-weight:800;color:#1a2050;margin:0;'>🔖 키워드 필터</p>",
            unsafe_allow_html=True
        )
    with col_s:
        st.markdown('<div class="btn-settings">', unsafe_allow_html=True)
        if st.button("⚙️ 키워드설정", key="btn_settings"):
            st.session_state.show_settings = not st.session_state.show_settings
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="btn-run">', unsafe_allow_html=True)
        run_btn = st.button("🔍 분석실행", key="btn_run")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_d:
        st.markdown('<div class="btn-download">', unsafe_allow_html=True)
        if st.session_state.df_result is not None:
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                st.session_state.df_result.to_excel(writer, index=False, sheet_name="결과")
            st.download_button(
                label="📥 엑셀다운로드",
                data=buf.getvalue(),
                file_name="키워드분석결과.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="btn_download_active"
            )
        else:
            st.button("📥 엑셀다운로드", disabled=True, key="btn_download_disabled")
        st.markdown('</div>', unsafe_allow_html=True)

    # 설정 패널 (토글)
    if st.session_state.show_settings:
        st.markdown("<hr style='margin:16px 0;border-color:#e0e4f0;'>", unsafe_allow_html=True)
        tabs = st.tabs(["1", "2", "3", "4", "5"])
        for i, tab in enumerate(tabs):
            with tab:
                render_settings_panel(i)

# ────────────────────────────────────────────────────────────────
# 분석 실행 (버튼 클릭 처리)
# ────────────────────────────────────────────────────────────────
if run_btn:
    if not st.session_state.uploaded_file_bytes:
        st.warning("⚠️ 먼저 엑셀 파일을 업로드하세요.")
    else:
        with st.spinner("⏳ 분석 중..."):
            df_raw = load_excel(st.session_state.uploaded_file_bytes)
            if df_raw is not None:
                df_norm = normalize_columns(df_raw)
                preset = st.session_state.presets[st.session_state.active_preset]
                st.session_state.df_result = apply_preset(df_norm, preset)
                st.success(f"✅ 분석 완료: {len(st.session_state.df_result):,}개 키워드 필터링됨")

# ────────────────────────────────────────────────────────────────
# 결과 테이블
# ────────────────────────────────────────────────────────────────
if st.session_state.df_result is not None:
    with st.container(border=True):
        st.markdown(
            f"<p style='font-size:14px;font-weight:700;color:#1a2050;'>📊 분석 결과 "
            f"<span style='color:#3b5bff;font-size:13px;'>({len(st.session_state.df_result):,}개)</span></p>",
            unsafe_allow_html=True
        )
        st.dataframe(
            st.session_state.df_result,
            use_container_width=True,
            height=480,
        )

