import streamlit as st
import pandas as pd
import io
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.set_page_config(page_title="끝장캐리 키워드 분석", layout="wide")

# ───────────────────────── CSS ─────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800;900&display=swap');

*, *::before, *::after {
    font-family: 'Noto Sans KR', sans-serif !important;
    box-sizing: border-box;
}

/* 기본 Streamlit UI 숨기기 */
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
footer { display: none !important; }

/* 페이지 배경 */
.stApp, body { background: #dde2ef !important; }

/* 메인 컨테이너 너비 60% */
.block-container {
    max-width: 60% !important;
    margin: 0 auto !important;
    padding: 32px 0 60px !important;
}

/* ── 공통 카드 스타일 ──
   st.container(border=True) → [data-testid="stVerticalBlockBorderWrapper"]
*/
[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff !important;
    border: 1.5px solid #c0c8de !important;
    border-radius: 16px !important;
    box-shadow: 0 2px 14px rgba(60,80,180,0.10) !important;
    padding: 20px 24px !important;
    margin-bottom: 16px !important;
}

/* ── 파일 업로더 영역 ──
   "Browse files" 버튼이 박스 밖으로 나가지 않도록 */
[data-testid="stFileUploader"] {
    background: #f5f7ff !important;
    border: 2px dashed #a0aad4 !important;
    border-radius: 12px !important;
    padding: 16px !important;
}
[data-testid="stFileUploader"] section {
    padding: 0 !important;
}
[data-testid="stFileUploaderDropzone"] {
    background: transparent !important;
    border: none !important;
    padding: 8px 0 !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    gap: 8px !important;
}
/* "Browse files" 버튼 */
[data-testid="stFileUploaderDropzone"] button {
    background: #3b5bff !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 22px !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    padding: 8px 24px !important;
    cursor: pointer !important;
    width: auto !important;
    display: inline-block !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] {
    font-size: 13px !important;
    color: #6672a0 !important;
}

/* ── 탭 숫자 1 2 3 4 5 크고 굵게 ── */
div[data-testid="stTabs"] div[role="tablist"] button[role="tab"],
div[data-testid="stTabs"] div[role="tablist"] button[role="tab"] p,
div[data-testid="stTabs"] div[role="tablist"] button[role="tab"] * {
    font-size: 22px !important;
    font-weight: 900 !important;
    color: #3a3f5c !important;
    font-family: 'Noto Sans KR', sans-serif !important;
}
div[data-testid="stTabs"] div[role="tablist"] button[role="tab"][aria-selected="true"],
div[data-testid="stTabs"] div[role="tablist"] button[role="tab"][aria-selected="true"] p {
    color: #3b5bff !important;
    border-bottom: 3px solid #3b5bff !important;
}

/* ── 탭 콘텐츠 (키워드설정 패널) 흰색 배경 ── */
div[data-testid="stTabs"] div[role="tabpanel"] {
    background: #ffffff !important;
    border-radius: 12px !important;
    border: 1.5px solid #c0c8de !important;
    padding: 20px !important;
    margin-top: 8px !important;
    box-shadow: 0 2px 10px rgba(60,80,180,0.08) !important;
}

/* ── 일반 Streamlit 버튼 (키워드설정·분석실행·엑셀다운로드) ── */
.stButton > button {
    font-family: 'Noto Sans KR', sans-serif !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    border-radius: 22px !important;
    padding: 8px 18px !important;
    min-height: 40px !important;
    width: 100% !important;
    cursor: pointer !important;
    transition: all 0.15s ease !important;
    transform: none !important;
    position: relative !important;
    top: 0 !important;
}

/* 키워드설정 버튼 – 흰 배경, 인디고 테두리 */
.btn-settings .stButton > button {
    background: #ffffff !important;
    color: #3b5bff !important;
    border: 1.5px solid #3b5bff !important;
}
.btn-settings .stButton > button:hover {
    background: #f0f3ff !important;
}

/* 분석실행 버튼 – 인디고 배경 */
.btn-run .stButton > button {
    background: #3b5bff !important;
    color: #ffffff !important;
    border: none !important;
}
.btn-run .stButton > button:hover {
    background: #2a47e0 !important;
}

/* 엑셀다운로드 버튼 – 흰 배경, 파란 테두리 */
.btn-download .stButton > button {
    background: #ffffff !important;
    color: #3b5bff !important;
    border: 1.5px solid #3b5bff !important;
}
.btn-download .stButton > button:hover {
    background: #f0f3ff !important;
}

/* 버튼 클릭시 위치 흔들림 방지 */
.stButton > button:active,
.stButton > button:focus {
    transform: none !important;
    top: 0 !important;
    box-shadow: none !important;
    outline: none !important;
}

/* AgGrid 결과 테이블 */
.ag-theme-streamlit {
    border-radius: 10px !important;
    overflow: hidden !important;
}
</style>
""", unsafe_allow_html=True)


# ───────────────────────── 기본 프리셋 정의 ─────────────────────────
DEFAULT_PRESET = {
    "이름": "프리셋",
    "brand_keyword": "전체",
    "search_min": 0,
    "search_max": 999999,
    "max_months": [],
    "peak_start": 1,
    "peak_end": 12,
    "seasonality_min": 0.0,
    "seasonality_max": 1.0,
    "coupang_min": 0.0,
    "coupang_max": 1.0,
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
MONTH_MAP = {
    "1월": 1, "2월": 2, "3월": 3, "4월": 4,
    "5월": 5, "6월": 6, "7월": 7, "8월": 8,
    "9월": 9, "10월": 10, "11월": 11, "12월": 12,
}

def load_excel(file):
    try:
        df = pd.read_excel(file, engine="openpyxl")
        return df
    except Exception as e:
        st.error(f"엑셀 파일 로드 실패: {e}")
        return None

def normalize_columns(df):
    rename = {}
    for col in df.columns:
        c = col.strip()
        if "키워드" in c:
            rename[col] = "키워드"
        elif "브랜드" in c:
            rename[col] = "브랜드키워드"
        elif "검색량" in c and "합" in c:
            rename[col] = "연간검색량"
        elif "최대" in c and "월" in c:
            rename[col] = "최대월"
        elif "피크" in c and "시작" in c:
            rename[col] = "피크시작월"
        elif "피크" in c and "종료" in c:
            rename[col] = "피크종료월"
        elif "계절성" in c or "시즈널" in c:
            rename[col] = "계절성"
        elif "쿠팡" in c and ("해외" in c or "직구" in c or "배송" in c):
            rename[col] = "쿠팡해외배송비율"
    df = df.rename(columns=rename)
    return df

def apply_preset(df, preset):
    result = df.copy()
    # 브랜드 키워드 필터
    if "브랜드키워드" in result.columns and preset["brand_keyword"] != "전체":
        val = True if preset["brand_keyword"] == "O" else False
        result = result[result["브랜드키워드"] == val]
    # 연간검색량
    if "연간검색량" in result.columns:
        result = result[
            (result["연간검색량"] >= preset["search_min"]) &
            (result["연간검색량"] <= preset["search_max"])
        ]
    # 최대월
    if "최대월" in result.columns and preset["max_months"]:
        result = result[result["최대월"].isin(preset["max_months"])]
    # 피크 시작·종료월
    if "피크시작월" in result.columns:
        result = result[result["피크시작월"] >= preset["peak_start"]]
    if "피크종료월" in result.columns:
        result = result[result["피크종료월"] <= preset["peak_end"]]
    # 계절성
    if "계절성" in result.columns:
        result = result[
            (result["계절성"] >= preset["seasonality_min"]) &
            (result["계절성"] <= preset["seasonality_max"])
        ]
    # 쿠팡 해외배송
    if "쿠팡해외배송비율" in result.columns:
        result = result[
            (result["쿠팡해외배송비율"] >= preset["coupang_min"]) &
            (result["쿠팡해외배송비율"] <= preset["coupang_max"])
        ]
    return result


# ───────────────────────── UI: 헤더 ─────────────────────────
with st.container(border=True):
    st.markdown(
        "<h2 style='margin:0; color:#1a2050; font-size:22px; font-weight:800;'>"
        "🚀 끝장캐리 키워드 분석</h2>"
        "<p style='margin:4px 0 0; color:#6672a0; font-size:13px;'>"
        "네이버 쇼핑 키워드 데이터를 업로드하여 조건별로 분석하세요.</p>",
        unsafe_allow_html=True,
    )

# ───────────────────────── UI: 파일 업로더 ─────────────────────────
with st.container(border=True):
    st.markdown(
        "<p style='font-size:14px; font-weight:700; color:#1a2050; margin-bottom:8px;'>"
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


# ───────────────────────── UI: 키워드 필터 박스 ─────────────────────────
with st.container(border=True):
    # 상단 행: "키워드 필터" 라벨 + 버튼 3개 가로정렬
    label_col, sp, c1, c2, c3 = st.columns([3, 1, 2, 2, 2])

    with label_col:
        st.markdown(
            "<p style='font-size:15px; font-weight:800; color:#1a2050; "
            "margin:0; padding-top:6px;'>🔖 키워드 필터</p>",
            unsafe_allow_html=True,
        )

    with c1:
        st.markdown('<div class="btn-settings">', unsafe_allow_html=True)
        if st.button("⚙️ 키워드설정", key="btn_settings"):
            st.session_state.show_settings = not st.session_state.show_settings
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="btn-run">', unsafe_allow_html=True)
        run_clicked = st.button("🔍 분석실행", key="btn_run")
        st.markdown("</div>", unsafe_allow_html=True)

    with c3:
        st.markdown('<div class="btn-download">', unsafe_allow_html=True)
        download_placeholder = st.empty()
        st.markdown("</div>", unsafe_allow_html=True)

    # 키워드설정 패널 (탭 1~5)
    if st.session_state.show_settings:
        st.markdown("---")
        preset_tabs = st.tabs(["1", "2", "3", "4", "5"])
        for idx, tab in enumerate(preset_tabs):
            with tab:
                p = st.session_state.presets[idx]

                col_a, col_b = st.columns(2)
                with col_a:
                    brand = st.selectbox(
                        "브랜드 키워드",
                        ["전체", "O", "X"],
                        index=["전체", "O", "X"].index(p["brand_keyword"]),
                        key=f"brand_{idx}",
                    )
                    s_min = st.number_input(
                        "연간검색량 최소", value=int(p["search_min"]),
                        min_value=0, key=f"smin_{idx}"
                    )
                    s_max = st.number_input(
                        "연간검색량 최대", value=int(p["search_max"]),
                        min_value=0, key=f"smax_{idx}"
                    )
                    all_months = [f"{m}월" for m in range(1, 13)]
                    selected_months = st.multiselect(
                        "최대월 선택 (비워두면 전체)",
                        all_months,
                        default=p["max_months"],
                        key=f"months_{idx}",
                    )

                with col_b:
                    peak_s = st.slider(
                        "피크 시작월", 1, 12, int(p["peak_start"]), key=f"ps_{idx}"
                    )
                    peak_e = st.slider(
                        "피크 종료월", 1, 12, int(p["peak_end"]), key=f"pe_{idx}"
                    )
                    seas_min, seas_max = st.slider(
                        "계절성 범위", 0.0, 1.0,
                        (float(p["seasonality_min"]), float(p["seasonality_max"])),
                        0.01, key=f"seas_{idx}"
                    )
                    coup_min, coup_max = st.slider(
                        "쿠팡 해외배송비율 범위", 0.0, 1.0,
                        (float(p["coupang_min"]), float(p["coupang_max"])),
                        0.01, key=f"coup_{idx}"
                    )

                if st.button("💾 저장", key=f"save_{idx}"):
                    st.session_state.presets[idx].update({
                        "brand_keyword": brand,
                        "search_min": s_min,
                        "search_max": s_max,
                        "max_months": selected_months,
                        "peak_start": peak_s,
                        "peak_end": peak_e,
                        "seasonality_min": seas_min,
                        "seasonality_max": seas_max,
                        "coupang_min": coup_min,
                        "coupang_max": coup_max,
                    })
                    st.success(f"프리셋 {idx + 1} 저장 완료!")


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
    df_show = st.session_state.df_result

    with st.container(border=True):
        st.markdown(
            "<p style='font-size:14px; font-weight:700; color:#1a2050; margin-bottom:8px;'>"
            "📊 분석 결과</p>",
            unsafe_allow_html=True,
        )

        gb = GridOptionsBuilder.from_dataframe(df_show)
        gb.configure_pagination(paginationAutoPageSize=True)
        gb.configure_side_bar()
        gb.configure_default_column(
            resizable=True, sortable=True, filter=True, wrapText=False
        )
        grid_options = gb.build()

        AgGrid(
            df_show,
            gridOptions=grid_options,
            update_mode=GridUpdateMode.NO_UPDATE,
            allow_unsafe_jscode=True,
            theme="streamlit",
            height=420,
        )

        # 엑셀 다운로드
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_show.to_excel(writer, index=False, sheet_name="결과")
        excel_bytes = output.getvalue()

        with download_placeholder:
            st.markdown('<div class="btn-download">', unsafe_allow_html=True)
            st.download_button(
                label="📥 엑셀다운로드",
                data=excel_bytes,
                file_name="키워드분석결과.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="dl_btn",
            )
            st.markdown("</div>", unsafe_allow_html=True)
