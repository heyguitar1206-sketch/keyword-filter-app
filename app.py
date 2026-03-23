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

/* ── 파일 업로더 외곽 박스 ── */
[data-testid="stFileUploader"] {
    background: #f5f7ff !important;
    border: 2px dashed #a0aad4 !important;
    border-radius: 12px !important;
    padding: 0 !important;
    overflow: hidden !important;
}

/* 드롭존 내부: 세로 정렬, Browse files 버튼이 안으로 들어오도록 */
[data-testid="stFileUploaderDropzone"] {
    background: transparent !important;
    border: none !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 6px !important;
    padding: 20px 16px !important;
    width: 100% !important;
}

/* 드롭존 안의 모든 자식을 block으로 */
[data-testid="stFileUploaderDropzone"] > * {
    width: auto !important;
}

/* Browse files 버튼 - 드롭존 안에만 적용 */
[data-testid="stFileUploaderDropzone"] button {
    background: #3b5bff !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 22px !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    padding: 8px 28px !important;
    min-height: 38px !important;
    cursor: pointer !important;
    display: inline-block !important;
    position: relative !important;
    bottom: auto !important;
    left: auto !important;
    right: auto !important;
    transform: none !important;
    margin: 0 !important;
}

/* ── 탭 숫자 1~5 크고 굵게 ── */
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

/* ── 일반 버튼 공통 초기화 ── */
.stButton > button {
    all: unset !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-family: 'Noto Sans KR', sans-serif !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    border-radius: 22px !important;
    padding: 8px 18px !important;
    min-height: 40px !important;
    width: 100% !important;
    cursor: pointer !important;
    box-sizing: border-box !important;
    transition: background 0.15s ease !important;
    white-space: nowrap !important;
}

/* 키워드설정 버튼 */
.btn-settings .stButton > button {
    background: #ffffff !important;
    color: #3b5bff !important;
    border: 1.5px solid #3b5bff !important;
}
.btn-settings .stButton > button:hover {
    background: #f0f3ff !important;
}

/* 분석실행 버튼 */
.btn-run .stButton > button {
    background: #3b5bff !important;
    color: #ffffff !important;
    border: none !important;
}
.btn-run .stButton > button:hover {
    background: #2a47e0 !important;
}

/* 엑셀다운로드 버튼 - 키워드설정과 완전히 동일 */
.btn-download .stButton > button,
.btn-download [data-testid="stDownloadButton"] > button {
    all: unset !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-family: 'Noto Sans KR', sans-serif !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    border-radius: 22px !important;
    padding: 8px 18px !important;
    min-height: 40px !important;
    width: 100% !important;
    cursor: pointer !important;
    box-sizing: border-box !important;
    background: #ffffff !important;
    color: #3b5bff !important;
    border: 1.5px solid #3b5bff !important;
    white-space: nowrap !important;
}
.btn-download .stButton > button:hover,
.btn-download [data-testid="stDownloadButton"] > button:hover {
    background: #f0f3ff !important;
}

/* ── 필터 섹션 구분선 제목 ── */
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
    "brand_keyword": "전체",
    "search_min": 0,
    "search_max": 999999,
    "seasonality": "전체",
    "max_months": [],
    "peak_vol_min": 0,
    "peak_vol_max": 999999,
    "coupang_price_min": 0,
    "coupang_price_max": 9999999,
    "coupang_review_min": 0,
    "coupang_review_max": 9999999,
    "coupang_overseas_min": 0,    # ← 퍼센트 단위 0~100
    "coupang_overseas_max": 100,  # ← 퍼센트 단위 0~100
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
        elif ("작년" in c or "연간" in c) and "검색량" in c and "최대" not in c and "피크" not in c:
            rename[col] = "작년검색량"
        elif "계절성" in c or "시즈널" in c:
            rename[col] = "계절성"
        elif "최대" in c and "월" in c and "검색량" not in c:
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
        result = result[result["계절성"] == (preset["seasonality"] == "있음")]

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

    # 8. 쿠팡해외배송비율 (퍼센트 → 비율로 변환 후 필터, 결과 내림차순)
    if "쿠팡해외배송비율" in result.columns:
        o_min = preset["coupang_overseas_min"] / 100.0
        o_max = preset["coupang_overseas_max"] / 100.0
        result = result[
            (result["쿠팡해외배송비율"] >= o_min) &
            (result["쿠팡해외배송비율"] <= o_max)
        ]
        result = result.sort_values("쿠팡해외배송비율", ascending=False)

    return result


# ───────────────────────── 설정 패널 렌더링 ─────────────────────────
def render_settings_panel(idx):
    p = st.session_state.presets[idx]
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<div class="filter-section-title">① 브랜드 키워드</div>', unsafe_allow_html=True)
        brand = st.radio(
            "브랜드 키워드", ["전체", "O", "X"],
            index=["전체", "O", "X"].index(p["brand_keyword"]),
            horizontal=True, key=f"brand_{idx}", label_visibility="collapsed",
        )

        st.markdown('<div class="filter-section-title">② 작년 검색량</div>', unsafe_allow_html=True)
        s_min = st.number_input("최소", value=int(p["search_min"]), min_value=0, key=f"smin_{idx}")
        s_max = st.number_input("최대", value=int(p["search_max"]), min_value=0, key=f"smax_{idx}")

        st.markdown('<div class="filter-section-title">③ 계절성</div>', unsafe_allow_html=True)
        seasonality = st.radio(
            "계절성", ["전체", "있음", "없음"],
            index=["전체", "있음", "없음"].index(p["seasonality"]),
            horizontal=True, key=f"seas_{idx}", label_visibility="collapsed",
        )

        st.markdown('<div class="filter-section-title">⑤ 피크월 검색량</div>', unsafe_allow_html=True)
        peak_min = st.number_input("최소", value=int(p["peak_vol_min"]), min_value=0, key=f"pvmin_{idx}")
        peak_max = st.number_input("최대", value=int(p["peak_vol_max"]), min_value=0, key=f"pvmax_{idx}")

    with col_b:
        st.markdown('<div class="filter-section-title">④ 작년 최대 검색월 (중복선택)</div>', unsafe_allow_html=True)
        month_cols = st.columns(6)
        selected_months = []
        for m in range(1, 13):
            with month_cols[(m - 1) % 6]:
                if st.checkbox(str(m), value=(m in p["max_months"]), key=f"month_{idx}_{m}"):
                    selected_months.append(m)

        st.markdown('<div class="filter-section-title">⑥ 쿠팡 평균가 (원)</div>', unsafe_allow_html=True)
        cp_min = st.number_input("최소", value=int(p["coupang_price_min"]), min_value=0, key=f"cpmin_{idx}")
        cp_max = st.number_input("최대", value=int(p["coupang_price_max"]), min_value=0, key=f"cpmax_{idx}")

        st.markdown('<div class="filter-section-title">⑦ 쿠팡 총 리뷰수</div>', unsafe_allow_html=True)
        cr_min = st.number_input("최소", value=int(p["coupang_review_min"]), min_value=0, key=f"crmin_{idx}")
        cr_max = st.number_input("최대", value=int(p["coupang_review_max"]), min_value=0, key=f"crmax_{idx}")

        # ── 8. 쿠팡해외배송비율 - 퍼센트(%) 단위 ──
        st.markdown('<div class="filter-section-title">⑧ 쿠팡 해외배송비율 % (결과 내림차순 정렬)</div>', unsafe_allow_html=True)
        co_min = st.number_input(
            "최소 (%)", value=int(p["coupang_overseas_min"]),
            min_value=0, max_value=100, step=1,
            key=f"comin_{idx}"
        )
        co_max = st.number_input(
            "최대 (%)", value=int(p["coupang_overseas_max"]),
            min_value=0, max_value=100, step=1,
            key=f"comax_{idx}"
        )

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

# 1) 헤더
with st.container(border=True):
    st.markdown(
        "<h2 style='margin:0;color:#1a2050;font-size:22px;font-weight:800;'>"
        "🚀 끝장캐리 키워드 분석</h2>"
        "<p style='margin:4px 0 0;color:#6672a0;font-size:13px;'>"
        "네이버 쇼핑 키워드 데이터를 업로드하여 조건별로 분석하세요.</p>",
        unsafe_allow_html=True,
    )

# 2) 파일 업로더
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

# 3) 키워드 필터
with st.container(border=True):
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
