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

/* Browse files 버튼 – 드롭존 내부 버튼만 타겟 */
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
    font-family: 'Noto Sans KR', sans-serif !important;
}
div[data-testid="stTabs"] div[role="tablist"] button[role="tab"][aria-selected="true"] p,
div[data-testid="stTabs"] div[role="tablist"] button[role="tab"][aria-selected="true"] {
    color: #3b5bff !important;
    border-bottom: 3px solid #3b5bff !important;
}

/* ── 탭 패널 (키워드설정 내부) 흰 배경 ── */
div[data-testid="stTabs"] div[role="tabpanel"] {
    background: #ffffff !important;
    border-radius: 12px !important;
    border: 1.5px solid #c0c8de !important;
    padding: 20px !important;
    margin-top: 8px !important;
    box-shadow: 0 2px 10px rgba(60,80,180,0.08) !important;
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

/* 키워드설정 버튼 */
.btn-settings .stButton > button {
    background: #ffffff !important;
    color: #3b5bff !important;
    border: 1.5px solid #3b5bff !important;
}
.btn-settings .stButton > button:hover { background: #f0f3ff !important; }

/* 분석실행 버튼 */
.btn-run .stButton > button {
    background: #3b5bff !important;
    color: #ffffff !important;
    border: none !important;
}
.btn-run .stButton > button:hover { background: #2a47e0 !important; }

/* 엑셀다운로드 버튼 */
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
</style>
""", unsafe_allow_html=True)


# ───────────────────────── 기본값 & 세션 초기화 ─────────────────────────
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
def load_excel(file):
    try:
        return pd.read_excel(file, engine="openpyxl")
    except Exception as e:
        st.error(f"엑셀 파일 로드 실패: {e}")
        return None

def normalize_columns(df):
    rename = {}
    for col in df.columns:
        c = col.strip()
        if "키워드" in c and "브랜드" not in c:
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
    return df.rename(columns=rename)

def apply_preset(df, preset):
    result = df.copy()
    if "브랜드키워드" in result.columns and preset["brand_keyword"] != "전체":
        val = preset["brand_keyword"] == "O"
        result = result[result["브랜드키워드"] == val]
    if "연간검색량" in result.columns:
        result = result[
            (result["연간검색량"] >= preset["search_min"]) &
            (result["연간검색량"] <= preset["search_max"])
        ]
    if "최대월" in result.columns and preset["max_months"]:
        result = result[result["최대월"].isin(preset["max_months"])]
    if "피크시작월" in result.columns:
        result = result[result["피크시작월"] >= preset["peak_start"]]
    if "피크종료월" in result.columns:
        result = result[result["피크종료월"] <= preset["peak_end"]]
    if "계절성" in result.columns:
        result = result[
            (result["계절성"] >= preset["seasonality_min"]) &
            (result["계절성"] <= preset["seasonality_max"])
        ]
    if "쿠팡해외배송비율" in result.columns:
        result = result[
            (result["쿠팡해외배송비율"] >= preset["coupang_min"]) &
            (result["쿠팡해외배송비율"] <= preset["coupang_max"])
        ]
    return result


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

# 3) 키워드 필터 카드 (버튼 3개 + 설정 패널)
with st.container(border=True):

    # ── 상단 행: 라벨 + 버튼 3개 나란히 ──
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
        # 결과가 있을 때만 다운로드 버튼 활성화
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

    # ── 키워드설정 패널 (탭 1~5) ──
    if st.session_state.show_settings:
        st.markdown("<hr style='margin:16px 0;border-color:#e0e4f0;'>", unsafe_allow_html=True)
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
                    st.success(f"✅ 프리셋 {idx + 1} 저장 완료!")


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
