import streamlit as st
import pandas as pd
import io
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode

st.set_page_config(page_title="끝장캐리 키워드 분석", layout="wide")

# ───────────────────────── CSS ─────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800;900&display=swap');

*, *::before, *::after {
    font-family: 'Noto Sans KR', sans-serif !important;
    box-sizing: border-box;
}

[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
footer { display: none !important; }

.stApp, body { background: #dde2ef !important; }

.block-container {
    max-width: 60% !important;
    margin: 0 auto !important;
    padding: 32px 0 60px !important;
}

/* ── 카드 공통 ── */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff !important;
    border: 2px solid #b8c0d8 !important;
    border-radius: 16px !important;
    box-shadow: 0 4px 18px rgba(60,80,180,0.13) !important;
    padding: 20px 24px !important;
    margin-bottom: 16px !important;
}

/* ── 파일 업로더 ── */
[data-testid="stFileUploader"] {
    background: #f5f7ff !important;
    border: 2px dashed #a0aad4 !important;
    border-radius: 12px !important;
    padding: 16px !important;
}
[data-testid="stFileUploaderDropzone"] {
    background: transparent !important;
    border: none !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    gap: 8px !important;
    padding: 8px 0 !important;
}
[data-testid="stFileUploaderDropzone"] > div > button,
[data-testid="stFileUploaderDropzone"] button {
    background: #3b5bff !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 22px !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    padding: 8px 24px !important;
    min-height: 38px !important;
    cursor: pointer !important;
    width: auto !important;
    display: inline-block !important;
    margin-top: 4px !important;
}

/* ── 탭 숫자 1 2 3 4 5 ── */
div[data-testid="stTabs"] div[role="tablist"] button[role="tab"] p,
div[data-testid="stTabs"] div[role="tablist"] button[role="tab"] {
    font-size: 22px !important;
    font-weight: 900 !important;
    color: #3a3f5c !important;
}
div[data-testid="stTabs"] div[role="tablist"] button[role="tab"][aria-selected="true"] p,
div[data-testid="stTabs"] div[role="tablist"] button[role="tab"][aria-selected="true"] {
    color: #3b5bff !important;
    border-bottom: 3px solid #3b5bff !important;
}

/* ── 탭 패널 흰 배경 ── */
div[data-testid="stTabs"] div[role="tabpanel"] {
    background: #ffffff !important;
    border-radius: 12px !important;
    border: 1.5px solid #c0c8de !important;
    padding: 20px !important;
    margin-top: 8px !important;
    box-shadow: 0 2px 10px rgba(60,80,180,0.08) !important;
}

/* ── 체크박스 월 선택 스타일 ── */
.month-checkbox-row {
    display: flex !important;
    flex-wrap: wrap !important;
    gap: 8px !important;
    margin-top: 6px !important;
}

/* ── 일반 버튼 공통 ── */
.stButton > button {
    font-family: 'Noto Sans KR', sans-serif !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    border-radius: 22px !important;
    padding: 8px 18px !important;
    min-height: 40px !important;
    width: 100% !important;
    cursor: pointer !important;
    transition: background 0.15s ease !important;
    transform: none !important;
    position: static !important;
}
.stButton > button:active,
.stButton > button:focus {
    transform: none !important;
    box-shadow: none !important;
    outline: none !important;
}

.btn-settings .stButton > button {
    background: #ffffff !important;
    color: #3b5bff !important;
    border: 1.5px solid #3b5bff !important;
}
.btn-settings .stButton > button:hover { background: #f0f3ff !important; }

.btn-run .stButton > button {
    background: #3b5bff !important;
    color: #ffffff !important;
    border: none !important;
}
.btn-run .stButton > button:hover { background: #2a47e0 !important; }

.btn-download .stButton > button,
.btn-download [data-testid="stDownloadButton"] > button {
    background: #ffffff !important;
    color: #3b5bff !important;
    border: 1.5px solid #3b5bff !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    border-radius: 22px !important;
    min-height: 40px !important;
    width: 100% !important;
    padding: 8px 18px !important;
}
.btn-download .stButton > button:hover,
.btn-download [data-testid="stDownloadButton"] > button:hover {
    background: #f0f3ff !important;
}

/* ── 필터 섹션 구분선 ── */
.filter-section-title {
    font-size: 12px;
    font-weight: 700;
    color: #6672a0;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin: 14px 0 6px 0;
    padding-bottom: 4px;
    border-bottom: 1px solid #e8ecf4;
}
</style>
""", unsafe_allow_html=True)


# ───────────────────────── 기본 프리셋 정의 ─────────────────────────
DEFAULT_PRESET = {
    "이름": "프리셋",
    # 1. 브랜드키워드
    "brand_keyword": "전체",          # "전체" | "O" | "X"
    # 2. 작년검색량
    "search_min": 0,
    "search_max": 999999,
    # 3. 계절성
    "seasonality": "전체",            # "전체" | "있음" | "없음"
    # 4. 작년최대검색월 (체크박스)
    "max_months": [],                 # 빈 리스트 = 전체
    # 5. 피크월검색량
    "peak_vol_min": 0,
    "peak_vol_max": 999999,
    # 6. 쿠팡평균가
    "coupang_price_min": 0,
    "coupang_price_max": 9999999,
    # 7. 쿠팡총리뷰수
    "coupang_review_min": 0,
    "coupang_review_max": 9999999,
    # 8. 쿠팡해외배송비율
    "coupang_overseas_min": 0.0,
    "coupang_overseas_max": 1.0,
}

def make_preset(name, **kwargs):
    p = DEFAULT_PRESET.copy()
    p["이름"] = name
    p.update(kwargs)
    return p

if "presets" not in st.session_state:
    st.session_state.presets = [make_preset(str(i + 1)) for i in range(5)]
if "active_preset" not in st.session_state:
    st.session_state.active_preset = 0
if "df_result" not in st.session_state:
    st.session_state.df_result = None
if "show_settings" not in st.session_state:
    st.session_state.show_settings = False


# ───────────────────────── 유틸 함수 ─────────────────────────
def load_excel(file):
    try:
        return pd.read_excel(file, engine="openpyxl")
    except Exception as e:
        st.error(f"엑셀 파일 로드 실패: {e}")
        return None

def normalize_columns(df):
    """컬럼명을 내부 표준명으로 매핑"""
    rename = {}
    for col in df.columns:
        c = col.strip()
        if "키워드" in c and "브랜드" not in c:
            rename[col] = "키워드"
        elif "브랜드" in c:
            rename[col] = "브랜드키워드"
        elif ("작년" in c or "연간" in c) and "검색량" in c and "최대" not in c and "피크" not in c:
            rename[col] = "작년검색량"
        elif "계절성" in c or "시즈널" in c:
            rename[col] = "계절성"
        elif ("최대" in c and "월" in c) and "검색량" not in c:
            rename[col] = "작년최대검색월"
        elif ("최대" in c and "검색량" in c) or ("피크" in c and "검색량" in c):
            rename[col] = "피크월검색량"
        elif "쿠팡" in c and ("가격" in c or "평균가" in c or "평균" in c):
            rename[col] = "쿠팡평균가"
        elif "쿠팡" in c and ("리뷰" in c or "후기" in c):
            rename[col] = "쿠팡총리뷰수"
        elif "쿠팡" in c and ("해외" in c or "직구" in c or "배송" in c):
            rename[col] = "쿠팡해외배송비율"
    return df.rename(columns=rename)

def apply_preset(df, preset):
    result = df.copy()

    # 1. 브랜드키워드
    if "브랜드키워드" in result.columns and preset["brand_keyword"] != "전체":
        val = preset["brand_keyword"] == "O"
        result = result[result["브랜드키워드"] == val]

    # 2. 작년검색량
    if "작년검색량" in result.columns:
        result = result[
            (result["작년검색량"] >= preset["search_min"]) &
            (result["작년검색량"] <= preset["search_max"])
        ]

    # 3. 계절성
    if "계절성" in result.columns and preset["seasonality"] != "전체":
        if preset["seasonality"] == "있음":
            result = result[result["계절성"] == True]
        else:
            result = result[result["계절성"] == False]

    # 4. 작년최대검색월
    if "작년최대검색월" in result.columns and preset["max_months"]:
        result = result[result["작년최대검색월"].isin(preset["max_months"])]

    # 5. 피크월검색량
    if "피크월검색량" in result.columns:
        result = result[
            (result["피크월검색량"] >= preset["peak_vol_min"]) &
            (result["피크월검색량"] <= preset["peak_vol_max"])
        ]

    # 6. 쿠팡평균가
    if "쿠팡평균가" in result.columns:
        result = result[
            (result["쿠팡평균가"] >= preset["coupang_price_min"]) &
            (result["쿠팡평균가"] <= preset["coupang_price_max"])
        ]

    # 7. 쿠팡총리뷰수
    if "쿠팡총리뷰수" in result.columns:
        result = result[
            (result["쿠팡총리뷰수"] >= preset["coupang_review_min"]) &
            (result["쿠팡총리뷰수"] <= preset["coupang_review_max"])
        ]

    # 8. 쿠팡해외배송비율 → 내림차순 정렬
    if "쿠팡해외배송비율" in result.columns:
        result = result[
            (result["쿠팡해외배송비율"] >= preset["coupang_overseas_min"]) &
            (result["쿠팡해외배송비율"] <= preset["coupang_overseas_max"])
        ]
        result = result.sort_values("쿠팡해외배송비율", ascending=False)

    return result


# ───────────────────────── 설정 패널 렌더링 함수 ─────────────────────────
def render_settings_panel(idx):
    p = st.session_state.presets[idx]

    col_a, col_b = st.columns(2)

    with col_a:
        # 1. 브랜드키워드
        st.markdown('<div class="filter-section-title">① 브랜드 키워드</div>', unsafe_allow_html=True)
        brand = st.radio(
            "브랜드 키워드",
            ["전체", "O", "X"],
            index=["전체", "O", "X"].index(p["brand_keyword"]),
            horizontal=True,
            key=f"brand_{idx}",
            label_visibility="collapsed",
        )

        # 2. 작년검색량
        st.markdown('<div class="filter-section-title">② 작년 검색량</div>', unsafe_allow_html=True)
        s_min = st.number_input(
            "최소", value=int(p["search_min"]), min_value=0,
            key=f"smin_{idx}", label_visibility="visible"
        )
        s_max = st.number_input(
            "최대", value=int(p["search_max"]), min_value=0,
            key=f"smax_{idx}", label_visibility="visible"
        )

        # 3. 계절성
        st.markdown('<div class="filter-section-title">③ 계절성</div>', unsafe_allow_html=True)
        seasonality = st.radio(
            "계절성",
            ["전체", "있음", "없음"],
            index=["전체", "있음", "없음"].index(p["seasonality"]),
            horizontal=True,
            key=f"seas_{idx}",
            label_visibility="collapsed",
        )

        # 5. 피크월검색량
        st.markdown('<div class="filter-section-title">⑤ 피크월 검색량</div>', unsafe_allow_html=True)
        peak_min = st.number_input(
            "최소", value=int(p["peak_vol_min"]), min_value=0,
            key=f"pvmin_{idx}", label_visibility="visible"
        )
        peak_max = st.number_input(
            "최대", value=int(p["peak_vol_max"]), min_value=0,
            key=f"pvmax_{idx}", label_visibility="visible"
        )

    with col_b:
        # 4. 작년최대검색월 - 체크박스 12개
        st.markdown('<div class="filter-section-title">④ 작년 최대 검색월 (중복선택)</div>', unsafe_allow_html=True)
        month_cols = st.columns(6)
        selected_months = []
        for m in range(1, 13):
            col_idx = (m - 1) % 6
            with month_cols[col_idx]:
                checked = st.checkbox(
                    str(m),
                    value=(m in p["max_months"]),
                    key=f"month_{idx}_{m}",
                )
                if checked:
                    selected_months.append(m)

        # 6. 쿠팡평균가
        st.markdown('<div class="filter-section-title">⑥ 쿠팡 평균가 (원)</div>', unsafe_allow_html=True)
        cp_min = st.number_input(
            "최소", value=int(p["coupang_price_min"]), min_value=0,
            key=f"cpmin_{idx}", label_visibility="visible"
        )
        cp_max = st.number_input(
            "최대", value=int(p["coupang_price_max"]), min_value=0,
            key=f"cpmax_{idx}", label_visibility="visible"
        )

        # 7. 쿠팡총리뷰수
        st.markdown('<div class="filter-section-title">⑦ 쿠팡 총 리뷰수</div>', unsafe_allow_html=True)
        cr_min = st.number_input(
            "최소", value=int(p["coupang_review_min"]), min_value=0,
            key=f"crmin_{idx}", label_visibility="visible"
        )
        cr_max = st.number_input(
            "최대", value=int(p["coupang_review_max"]), min_value=0,
            key=f"crmax_{idx}", label_visibility="visible"
        )

        # 8. 쿠팡해외배송비율
        st.markdown('<div class="filter-section-title">⑧ 쿠팡 해외배송비율 (결과 내림차순 정렬)</div>', unsafe_allow_html=True)
        co_min = st.number_input(
            "최소 (0.0~1.0)", value=float(p["coupang_overseas_min"]),
            min_value=0.0, max_value=1.0, step=0.01, format="%.2f",
            key=f"comin_{idx}", label_visibility="visible"
        )
        co_max = st.number_input(
            "최대 (0.0~1.0)", value=float(p["coupang_overseas_max"]),
            min_value=0.0, max_value=1.0, step=0.01, format="%.2f",
            key=f"comax_{idx}", label_visibility="visible"
        )

    # 저장 버튼
    if st.button("💾 저장", key=f"save_{idx}"):
        st.session_state.presets[idx].update({
            "brand_keyword": brand,
            "search_min": s_min,
            "search_max": s_max,
            "seasonality": seasonality,
            "max_months": selected_months,
            "peak_vol_min": peak_min,
            "peak_vol_max": peak_max,
            "coupang_price_min": cp_min,
            "coupang_price_max": cp_max,
            "coupang_review_min": cr_min,
            "coupang_review_max": cr_max,
            "coupang_overseas_min": co_min,
            "coupang_overseas_max": co_max,
        })
        st.success(f"✅ 프리셋 {idx + 1} 저장 완료!")


# ───────────────────────── UI 레이아웃 ─────────────────────────

# 1) 헤더 카드
with st.container(border=True):
    st.markdown(
        "<h2 style='margin:0;color:#1a2050;font-size:22px;font-weight:800;'>"
        "🚀 끝장캐리 키워드 분석</h2>"
        "<p style='margin:4px 0 0;color:#6672a0;font-size:13px;'>"
        "네이버 쇼핑 키워드 데이터를 업로드하여 조건별로 분석하세요.</p>",
        unsafe_allow_html=True,
    )

# 2) 파일 업로더 카드
with st.container(border=True):
    st.markdown(
        "<p style='font-size:14px;font-weight:700;color:#1a2050;margin-bottom:8px;'>"
        "📂 엑셀 파일 업로드</p>",
        unsafe_allow_html=True,
    )
    uploaded_file = st.file_uploader(
        "네이버 쇼핑 키워드 엑셀 파일을 업로드하세요 (.xlsx)",
        type=["xlsx"],
        label_visibility="collapsed",
    )
    if uploaded_file:
        st.success(f"✅ 파일 로드됨: {uploaded_file.name}")

# 3) 키워드 필터 카드
with st.container(border=True):

    # 상단 행: 라벨 + 버튼 3개
    col_label, col_sp, col_s, col_r, col_d = st.columns([3, 1, 2, 2, 2])

    with col_label:
        st.markdown(
            "<p style='font-size:15px;font-weight:800;color:#1a2050;"
            "margin:0;padding-top:8px;'>🔖 키워드 필터</p>",
            unsafe_allow_html=True,
        )

    with col_s:
        st.markdown('<div class="btn-settings">', unsafe_allow_html=True)
        if st.button("⚙️ 키워드설정", key="btn_settings"):
            st.session_state.show_settings = not st.session_state.show_settings
        st.markdown("</div>", unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="btn-run">', unsafe_allow_html=True)
        run_clicked = st.button("🔍 분석실행", key="btn_run")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_d:
        st.markdown('<div class="btn-download">', unsafe_allow_html=True)
        if st.session_state.df_result is not None:
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                st.session_state.df_result.to_excel(writer, index=False, sheet_name="결과")
            st.download_button(
                label="📥 엑셀다운로드",
                data=output.getvalue(),
                file_name="키워드분석결과.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="dl_btn",
            )
        else:
            st.button("📥 엑셀다운로드", key="dl_disabled", disabled=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # 키워드설정 패널
    if st.session_state.show_settings:
        st.markdown("<hr style='margin:16px 0;border-color:#e0e4f0;'>", unsafe_allow_html=True)
        preset_tabs = st.tabs(["1", "2", "3", "4", "5"])
        for idx, tab in enumerate(preset_tabs):
            with tab:
                render_settings_panel(idx)


# ───────────────────────── 분석 실행 ─────────────────────────
if run_clicked:
    if uploaded_file is None:
        st.warning("⚠️ 먼저 엑셀 파일을 업로드하세요.")
    else:
        df_raw = load_excel(uploaded_file)
        if df_raw is not None:
            df_raw = normalize_columns(df_raw)
            preset = st.session_state.presets[st.session_state.active_preset]
            df_filtered = apply_preset(df_raw, preset)
            st.session_state.df_result = df_filtered
            st.success(f"✅ 분석 완료: {len(df_filtered):,}개 키워드 필터링됨")


# ───────────────────────── 결과 테이블 ─────────────────────────
if st.session_state.df_result is not None:
    with st.container(border=True):
        st.markdown(
            "<p style='font-size:14px;font-weight:700;color:#1a2050;margin-bottom:8px;'>"
            "📊 분석 결과</p>",
            unsafe_allow_html=True,
        )
        df_show = st.session_state.df_result
        gb = GridOptionsBuilder.from_dataframe(df_show)
        gb.configure_pagination(paginationAutoPageSize=True)
        gb.configure_side_bar()
        gb.configure_default_column(resizable=True, sortable=True, filter=True)
        AgGrid(
            df_show,
            gridOptions=gb.build(),
            update_mode=GridUpdateMode.NO_UPDATE,
            allow_unsafe_jscode=True,
            theme="streamlit",
            height=420,
        )
