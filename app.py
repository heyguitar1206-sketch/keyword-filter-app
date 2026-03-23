import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="끝장캐리 키워드 분석", layout="wide")

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

[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff !important;
    border: 2px solid #b8c0d8 !important;
    border-radius: 16px !important;
    box-shadow: 0 4px 18px rgba(60,80,180,0.13) !important;
    padding: 20px 24px !important;
    margin-bottom: 16px !important;
}

[data-testid="stFileUploader"] {
    background: #f5f7ff !important;
    border: 2px dashed #a0aad4 !important;
    border-radius: 12px !important;
    padding: 0 !important;
    overflow: hidden !important;
    min-height: 80px !important;
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
    min-height: 80px !important;
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
    transform: none !important;
    margin: 0 !important;
    white-space: nowrap !important;
}
[data-testid="stFileUploaderDropzone"] button:hover {
    background: #2a47e0 !important;
}

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
div[data-testid="stTabs"] div[role="tabpanel"] {
    background: #ffffff !important;
    border-radius: 12px !important;
    border: 1.5px solid #c0c8de !important;
    padding: 20px !important;
    margin-top: 8px !important;
    box-shadow: 0 2px 10px rgba(60,80,180,0.08) !important;
}

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
    box-sizing: border-box !important;
    white-space: nowrap !important;
    transition: color 0.15s ease !important;
}
.btn-settings .stButton > button:hover { color: #3b5bff !important; }
.btn-run .stButton > button { color: #3b5bff !important; }
.btn-run .stButton > button:hover { color: #1a3bcc !important; }
.btn-download .stButton > button:hover,
.btn-download [data-testid="stDownloadButton"] > button:hover { color: #3b5bff !important; }
.btn-download .stButton > button:disabled { color: #b0b8d0 !important; cursor: default !important; }

div[role="tabpanel"] [data-testid="stNumberInput"] > div {
    background: #ffffff !important;
    border: 1.5px solid #c0c8de !important;
    border-radius: 10px !important;
    overflow: hidden !important;
    display: flex !important;
    align-items: center !important;
}
div[role="tabpanel"] [data-testid="stNumberInput"] > div:focus-within {
    border-color: #3b5bff !important;
    box-shadow: 0 0 0 2px rgba(59,91,255,0.12) !important;
}
div[role="tabpanel"] [data-testid="stNumberInput"] input {
    background: #ffffff !important;
    border: none !important;
    font-size: 12px !important;
    color: #2a2f55 !important;
    font-weight: 500 !important;
    padding: 7px 10px !important;
    flex: 1 !important;
    outline: none !important;
    box-shadow: none !important;
}
div[role="tabpanel"] [data-testid="stNumberInput"] button {
    all: unset !important;
    background: #3b5bff !important;
    color: #ffffff !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    width: 32px !important;
    min-width: 32px !important;
    min-height: 36px !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    cursor: pointer !important;
    flex-shrink: 0 !important;
}
div[role="tabpanel"] [data-testid="stNumberInput"] button:hover {
    background: #2a47e0 !important;
}

.filter-section-title {
    font-size: 14px !important;
    font-weight: 800 !important;
    color: #3a3f5c !important;
    margin: 16px 0 8px 0 !important;
    padding-bottom: 5px !important;
    border-bottom: 1.5px solid #d4d9ee !important;
}
div[role="tabpanel"] [data-testid="stRadio"] label,
div[role="tabpanel"] [data-testid="stCheckbox"] label,
div[role="tabpanel"] label {
    font-size: 11px !important;
    color: #4a5080 !important;
}
div[role="tabpanel"] .stButton > button {
    all: unset !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    min-height: 34px !important;
    padding: 6px 20px !important;
    width: auto !important;
    background: #ffffff !important;
    color: #3b5bff !important;
    border: 1.5px solid #3b5bff !important;
    border-radius: 8px !important;
    cursor: pointer !important;
    box-sizing: border-box !important;
}
div[role="tabpanel"] .stButton > button:hover { background: #f0f3ff !important; }
</style>
""", unsafe_allow_html=True)


# ───────────────────────── 세션 초기화 ─────────────────────────
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
    "coupang_overseas_min": 0,
    "coupang_overseas_max": 100,
}

def make_preset(name, **kwargs):
    p = DEFAULT_PRESET.copy()
    p["이름"] = name
    p.update(kwargs)
    return p

for key, val in {
    "presets": [make_preset(str(i + 1)) for i in range(5)],
    "active_preset": 0,
    "df_result": None,
    "show_settings": False,
    "uploaded_file_bytes": None,
    "uploaded_file_name": "",
}.items():
    if key not in st.session_state:
        st.session_state[key] = val


# ───────────────────────── 유틸 함수 ─────────────────────────
def load_excel(file_bytes):
    try:
        return pd.read_excel(io.BytesIO(file_bytes), engine="openpyxl")
    except Exception as e:
        st.error(f"엑셀 파일 로드 실패: {e}")
        return None

def normalize_columns(df):
    """
    중복 컬럼명 방지: 이미 표준명으로 매핑된 컬럼은 건너뜀.
    컬럼 인덱스를 초기화하여 duplicate label 에러 방지.
    """
    # 1) 컬럼 인덱스 중복 제거 (같은 이름의 컬럼이 여러 개면 뒤에 _1, _2 붙임)
    cols = pd.Series(df.columns)
    for dup in cols[cols.duplicated()].unique():
        dup_idx = cols[cols == dup].index.tolist()
        for i, idx in enumerate(dup_idx[1:], 1):
            cols[idx] = f"{dup}_{i}"
    df.columns = cols.tolist()

    rename = {}
    used_targets = set()

    for col in df.columns:
        c = col.strip()
        target = None

        if "키워드" in c and "브랜드" not in c and "키워드" not in used_targets:
            target = "키워드"
        elif "브랜드" in c and "브랜드키워드" not in used_targets:
            target = "브랜드키워드"
        elif ("작년" in c or "연간" in c) and "검색량" in c \
                and "최대" not in c and "피크" not in c \
                and "작년검색량" not in used_targets:
            target = "작년검색량"
        elif ("계절성" in c or "시즈널" in c) and "계절성" not in used_targets:
            target = "계절성"
        elif "최대" in c and "월" in c and "검색량" not in c \
                and "작년최대검색월" not in used_targets:
            target = "작년최대검색월"
        elif (("최대" in c and "검색량" in c) or ("피크" in c and "검색량" in c)) \
                and "피크월검색량" not in used_targets:
            target = "피크월검색량"
        elif "쿠팡" in c and ("가격" in c or "평균가" in c or "평균" in c) \
                and "쿠팡평균가" not in used_targets:
            target = "쿠팡평균가"
        elif "쿠팡" in c and ("리뷰" in c or "후기" in c) \
                and "쿠팡총리뷰수" not in used_targets:
            target = "쿠팡총리뷰수"
        elif "쿠팡" in c and ("해외" in c or "직구" in c or "배송" in c) \
                and "쿠팡해외배송비율" not in used_targets:
            target = "쿠팡해외배송비율"

        if target:
            rename[col] = target
            used_targets.add(target)

    df = df.rename(columns=rename)

    # 2) 혹시 남아있는 중복 컬럼 최종 제거 (첫 번째 컬럼만 유지)
    df = df.loc[:, ~df.columns.duplicated()]

    return df

def safe_numeric(series):
    """숫자 비교 전 강제로 numeric 변환, 실패하면 NaN"""
    return pd.to_numeric(series, errors="coerce")

def apply_preset(df, preset):
    result = df.copy()

    try:
        # 1. 브랜드키워드
        if "브랜드키워드" in result.columns and preset["brand_keyword"] != "전체":
            target_val = preset["brand_keyword"] == "O"
            col = result["브랜드키워드"]
            # True/False 또는 'O'/'X' 문자열 모두 처리
            if col.dtype == object:
                result = result[col.str.upper().str.strip() == ("O" if target_val else "X")]
            else:
                result = result[col == target_val]

        # 2. 작년검색량
        if "작년검색량" in result.columns:
            col = safe_numeric(result["작년검색량"])
            result = result[(col >= preset["search_min"]) & (col <= preset["search_max"])]

        # 3. 계절성
        if "계절성" in result.columns and preset["seasonality"] != "전체":
            col = result["계절성"]
            if col.dtype == object:
                if preset["seasonality"] == "있음":
                    result = result[col.str.upper().str.strip().isin(["O", "TRUE", "Y", "있음", "YES", "1"])]
                else:
                    result = result[col.str.upper().str.strip().isin(["X", "FALSE", "N", "없음", "NO", "0"])]
            else:
                result = result[col == (preset["seasonality"] == "있음")]

        # 4. 작년최대검색월
        if "작년최대검색월" in result.columns and preset["max_months"]:
            col = safe_numeric(result["작년최대검색월"])
            result = result[col.isin(preset["max_months"])]

        # 5. 피크월검색량
        if "피크월검색량" in result.columns:
            col = safe_numeric(result["피크월검색량"])
            result = result[(col >= preset["peak_vol_min"]) & (col <= preset["peak_vol_max"])]

        # 6. 쿠팡평균가
        if "쿠팡평균가" in result.columns:
            col = safe_numeric(result["쿠팡평균가"])
            result = result[(col >= preset["coupang_price_min"]) & (col <= preset["coupang_price_max"])]

        # 7. 쿠팡총리뷰수
        if "쿠팡총리뷰수" in result.columns:
            col = safe_numeric(result["쿠팡총리뷰수"])
            result = result[(col >= preset["coupang_review_min"]) & (col <= preset["coupang_review_max"])]

        # 8. 쿠팡해외배송비율 (퍼센트 → 비율 변환 후 필터, 내림차순 정렬)
        if "쿠팡해외배송비율" in result.columns:
            col = safe_numeric(result["쿠팡해외배송비율"])
            o_min = preset["coupang_overseas_min"] / 100.0
            o_max = preset["coupang_overseas_max"] / 100.0
            result = result[(col >= o_min) & (col <= o_max)]
            result = result.sort_values("쿠팡해외배송비율", ascending=False)

    except Exception as e:
        st.error(f"필터 적용 중 오류: {e}")
        return df  # 오류 시 원본 반환

    # 인덱스 리셋
    return result.reset_index(drop=True)


# ───────────────────────── 설정 패널 ─────────────────────────
def render_settings_panel(idx):
    p = st.session_state.presets[idx]
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<div class="filter-section-title">① 브랜드 키워드</div>', unsafe_allow_html=True)
        brand = st.radio("브랜드 키워드", ["전체", "O", "X"],
            index=["전체", "O", "X"].index(p["brand_keyword"]),
            horizontal=True, key=f"brand_{idx}", label_visibility="collapsed")

        st.markdown('<div class="filter-section-title">② 작년 검색량</div>', unsafe_allow_html=True)
        s_min = st.number_input("최소", value=int(p["search_min"]), min_value=0, key=f"smin_{idx}")
        s_max = st.number_input("최대", value=int(p["search_max"]), min_value=0, key=f"smax_{idx}")

        st.markdown('<div class="filter-section-title">③ 계절성</div>', unsafe_allow_html=True)
        seasonality = st.radio("계절성", ["전체", "있음", "없음"],
            index=["전체", "있음", "없음"].index(p["seasonality"]),
            horizontal=True, key=f"seas_{idx}", label_visibility="collapsed")

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

        st.markdown('<div class="filter-section-title">⑧ 쿠팡 해외배송비율 % (결과 내림차순 정렬)</div>', unsafe_allow_html=True)
        co_min = st.number_input("최소 (%)", value=int(p["coupang_overseas_min"]),
                                  min_value=0, max_value=100, step=1, key=f"comin_{idx}")
        co_max = st.number_input("최대 (%)", value=int(p["coupang_overseas_max"]),
                                  min_value=0, max_value=100, step=1, key=f"comax_{idx}")

    if st.button("💾 저장", key=f"save_{idx}"):
        st.session_state.presets[idx].update({
            "brand_keyword": brand,
            "search_min": s_min, "search_max": s_max,
            "seasonality": seasonality,
            "max_months": selected_months,
            "peak_vol_min": peak_min, "peak_vol_max": peak_max,
            "coupang_price_min": cp_min, "coupang_price_max": cp_max,
            "coupang_review_min": cr_min, "coupang_review_max": cr_max,
            "coupang_overseas_min": co_min, "coupang_overseas_max": co_max,
        })
        st.success(f"✅ 프리셋 {idx + 1} 저장 완료!")


# ═══════════════════════════════════════════════
#  UI 렌더링
# ═══════════════════════════════════════════════

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
        "파일을 끌어다 놓거나 버튼을 클릭하세요",
        type=["xlsx"],
        label_visibility="collapsed",
        key="file_uploader",
    )
    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        if file_bytes:
            st.session_state.uploaded_file_bytes = file_bytes
            st.session_state.uploaded_file_name = uploaded_file.name

    if st.session_state.uploaded_file_bytes is not None:
        st.success(f"✅ 파일 로드됨: {st.session_state.uploaded_file_name}")

# 3) 키워드 필터
with st.container(border=True):
    col_label, col_sp, col_s, col_r, col_d = st.columns([3, 1, 2, 2, 2])

    with col_label:
        st.markdown(
            "<p style='font-size:15px;font-weight:800;color:#1a2050;"
            "margin:0;padding-top:6px;'>🔖 키워드 필터</p>",
            unsafe_allow_html=True,
        )
    with col_s:
        st.markdown('<div class="btn-settings">', unsafe_allow_html=True)
        if st.button("⚙️ 키워드설정", key="btn_settings"):
            st.session_state.show_settings = not st.session_state.show_settings
        st.markdown("</div>", unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="btn-run">', unsafe_allow_html=True)
        run_btn = st.button("🔍 분석실행", key="btn_run")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_d:
        st.markdown('<div class="btn-download">', unsafe_allow_html=True)
        if st.session_state.df_result is not None:
            out = io.BytesIO()
            with pd.ExcelWriter(out, engine="openpyxl") as w:
                st.session_state.df_result.to_excel(w, index=False, sheet_name="결과")
            st.download_button(
                label="📥 엑셀다운로드",
                data=out.getvalue(),
                file_name="키워드분석결과.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="dl_btn",
            )
        else:
            st.button("📥 엑셀다운로드", key="dl_disabled", disabled=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.show_settings:
        st.markdown("<hr style='margin:16px 0;border-color:#e0e4f0;'>", unsafe_allow_html=True)
        tabs = st.tabs(["1", "2", "3", "4", "5"])
        for i, tab in enumerate(tabs):
            with tab:
                render_settings_panel(i)

# ── 분석 실행 ──────────────────────────────────────────────
if run_btn:
    if st.session_state.uploaded_file_bytes is None:
        st.warning("⚠️ 먼저 엑셀 파일을 업로드하세요.")
    else:
        with st.spinner("⏳ 분석 중..."):
            try:
                df_raw = load_excel(st.session_state.uploaded_file_bytes)
                if df_raw is not None:
                    # 컬럼명 정규화
                    df_raw = normalize_columns(df_raw)

                    # 실제 존재하는 컬럼 목록 디버깅용 출력 (문제 시 확인)
                    # st.write("인식된 컬럼:", df_raw.columns.tolist())

                    preset = st.session_state.presets[st.session_state.active_preset]
                    df_filtered = apply_preset(df_raw, preset)
                    st.session_state.df_result = df_filtered
                    st.success(f"✅ 분석 완료: {len(df_filtered):,}개 키워드 필터링됨")
            except Exception as e:
                st.error(f"❌ 분석 오류: {e}")
                st.info("💡 엑셀 파일의 컬럼명을 확인해주세요.")

# ── 결과 테이블 ────────────────────────────────────────────
if st.session_state.df_result is not None:
    with st.container(border=True):
        df_show = st.session_state.df_result
        st.markdown(
            f"<p style='font-size:14px;font-weight:700;color:#1a2050;margin-bottom:8px;'>"
            f"📊 분석 결과 &nbsp;"
            f"<span style='font-size:12px;color:#6672a0;font-weight:500;'>"
            f"총 {len(df_show):,}개</span></p>",
            unsafe_allow_html=True,
        )
        st.dataframe(df_show, use_container_width=True, height=460)
