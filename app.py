import streamlit as st
import pandas as pd
import io
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.set_page_config(
    page_title="키워드 분석 도구",
    page_icon="🔍",
    layout="wide"
)

st.markdown("""
<style>
    .stApp { background-color: #f5f7fb; }
    .main-title { font-size: 28px; font-weight: 800; color: #1a1a2e; margin-bottom: 4px; }
    .main-title span { color: #4361ee; }
    .sub-title { font-size: 13px; color: #888; margin-bottom: 20px; }
    .card { background: white; border-radius: 16px; padding: 24px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.07); margin-bottom: 20px; }
    .result-count { font-size: 15px; color: #4361ee; font-weight: 700; padding: 8px 0; }
    .field-label { font-size: 13px; font-weight: 700; color: #333; margin-bottom: 4px; }
    .stButton > button { border-radius: 24px !important; font-weight: 700 !important; }
    .stTabs [aria-selected="true"] { color: #4361ee !important; }
</style>
""", unsafe_allow_html=True)

# ── 세션 초기화 ──
DEFAULT_PRESET = {
    "name": "프리셋",
    "브랜드": "전체",
    "시즌성": "전체",
    "작년검색량_min": 0,
    "작년검색량_max": 9999999,
    "작년최대검색월": [],
    "피크월검색량_min": 0,
    "피크월검색량_max": 9999999,
    "쿠팡총리뷰수_min": 0,
    "쿠팡총리뷰수_max": 9999999,
    "쿠팡해외배송비율_min": 0,
    "쿠팡해외배송비율_max": 100,
}

if "presets" not in st.session_state:
    st.session_state.presets = {
        0: {**DEFAULT_PRESET, "name": "시즌소싱 26년 봄",
            "브랜드": "X", "시즌성": "있음"},
        1: {**DEFAULT_PRESET, "name": "비시즌 가구",
            "브랜드": "X", "시즌성": "없음"},
        2: {**DEFAULT_PRESET, "name": "프리셋 3"},
        3: {**DEFAULT_PRESET, "name": "프리셋 4"},
        4: {**DEFAULT_PRESET, "name": "프리셋 5"},
    }

if "active_preset" not in st.session_state:
    st.session_state.active_preset = 0
if "show_preset_modal" not in st.session_state:
    st.session_state.show_preset_modal = False
if "df" not in st.session_state:
    st.session_state.df = None
if "result_df" not in st.session_state:
    st.session_state.result_df = None
if "filtered_count" not in st.session_state:
    st.session_state.filtered_count = 0

# ── 데이터 로드 ──
@st.cache_data
def load_excel(file_bytes):
    raw = pd.read_excel(
        io.BytesIO(file_bytes), sheet_name="all", header=[0, 1, 2])
    new_cols = []
    for col in raw.columns:
        parts = [str(c).strip() for c in col
                 if str(c).strip() not in ("nan", "")]
        new_cols.append("_".join(dict.fromkeys(parts)))
    raw.columns = new_cols
    return raw

def find_col(df, keywords):
    for col in df.columns:
        if all(kw in col for kw in keywords):
            return col
    return None

def get_col_map(df):
    keyword_col = next(
        (col for col in df.columns
         if "키워드" in col
         and "신규진입" not in col
         and "브랜드" not in col
         and "쇼핑성" not in col),
        None
    )
    return {
        "키워드":           keyword_col,
        "브랜드":           find_col(df, ["브랜드"]),
        "쇼핑성":           find_col(df, ["쇼핑성"]),
        "경쟁률":           find_col(df, ["경쟁률"]),
        "작년검색량":       find_col(df, ["작년", "검색량"]),
        "작년최대검색월":   (find_col(df, ["작년최대", "검색월"]) or
                            find_col(df, ["작년", "최대검색", "월"]) or
                            find_col(df, ["작년", "최대", "월"])),
        "피크월검색량":     (find_col(df, ["작년최대", "검색량"]) or
                            find_col(df, ["작년최대검색월", "검색량"]) or
                            find_col(df, ["작년", "최대검색량"])),
        "계절성":           find_col(df, ["계절성"]),
        "계절성월":         find_col(df, ["계절성", "월"]),
        "네이버경쟁강도":   find_col(df, ["경쟁강도"]),
        "쿠팡총리뷰수":     find_col(df, ["쿠팡", "총리뷰수"]),
        "쿠팡해외배송비율": find_col(df, ["쿠팡", "해외배송비율"]),
    }

def apply_preset(df, col_map, preset):
    fdf = df.copy()

    if col_map.get("쇼핑성"):
        fdf = fdf[fdf[col_map["쇼핑성"]].astype(str).str.strip() == "O"]

    if col_map.get("키워드"):
        fdf = fdf.drop_duplicates(subset=[col_map["키워드"]])

    if preset["브랜드"] != "전체" and col_map.get("브랜드"):
        fdf = fdf[fdf[col_map["브랜드"]].astype(str).str.strip()
                  == preset["브랜드"]]

    if preset["시즌성"] != "전체" and col_map.get("계절성"):
        fdf = fdf[fdf[col_map["계절성"]].astype(str).str.strip()
                  == preset["시즌성"]]

    if col_map.get("작년검색량"):
        fdf[col_map["작년검색량"]] = pd.to_numeric(
            fdf[col_map["작년검색량"]], errors="coerce")
        fdf = fdf[
            (fdf[col_map["작년검색량"]] >= preset["작년검색량_min"]) &
            (fdf[col_map["작년검색량"]] <= preset["작년검색량_max"])
        ]

    if preset["작년최대검색월"] and col_map.get("작년최대검색월"):
        selected_months = [int(m) for m in preset["작년최대검색월"]]
        fdf[col_map["작년최대검색월"]] = pd.to_numeric(
            fdf[col_map["작년최대검색월"]], errors="coerce")
        fdf = fdf[fdf[col_map["작년최대검색월"]].isin(selected_months)]

    if col_map.get("피크월검색량"):
        fdf[col_map["피크월검색량"]] = pd.to_numeric(
            fdf[col_map["피크월검색량"]], errors="coerce")
        fdf = fdf[
            (fdf[col_map["피크월검색량"]] >= preset["피크월검색량_min"]) &
            (fdf[col_map["피크월검색량"]] <= preset["피크월검색량_max"])
        ]

    if col_map.get("쿠팡총리뷰수"):
        fdf[col_map["쿠팡총리뷰수"]] = pd.to_numeric(
            fdf[col_map["쿠팡총리뷰수"]], errors="coerce")
        fdf = fdf[
            (fdf[col_map["쿠팡총리뷰수"]] >= preset["쿠팡총리뷰수_min"]) &
            (fdf[col_map["쿠팡총리뷰수"]] <= preset["쿠팡총리뷰수_max"])
        ]

    if col_map.get("쿠팡해외배송비율"):
        fdf[col_map["쿠팡해외배송비율"]] = pd.to_numeric(
            fdf[col_map["쿠팡해외배송비율"]], errors="coerce")
        min_val = preset["쿠팡해외배송비율_min"] / 100
        max_val = preset["쿠팡해외배송비율_max"] / 100
        fdf = fdf[
            (fdf[col_map["쿠팡해외배송비율"]] >= min_val) &
            (fdf[col_map["쿠팡해외배송비율"]] <= max_val)
        ]
        fdf = fdf.sort_values(
            by=col_map["쿠팡해외배송비율"], ascending=False)

    return fdf.reset_index(drop=True)

def build_display_df(fdf, col_map):
    mapping = {
        "키워드":           "키워드",
        "브랜드":           "브랜드",
        "경쟁률":           "경쟁률",
        "작년검색량":       "작년검색량",
        "작년최대검색월":   "최대검색월",
        "피크월검색량":     "피크월검색량",
        "계절성":           "계절성",
        "계절성월":         "계절성월",
        "네이버경쟁강도":   "경쟁강도",
        "쿠팡총리뷰수":     "총리뷰수",
        "쿠팡해외배송비율": "해외배송(%)",
    }
    display_cols = {}
    for key, label in mapping.items():
        if col_map.get(key) and col_map[key] in fdf.columns:
            display_cols[col_map[key]] = label

    result = fdf[list(display_cols.keys())].rename(columns=display_cols)

    if "해외배송(%)" in result.columns:
        result["해외배송(%)"] = (
            pd.to_numeric(result["해외배송(%)"], errors="coerce") * 100
        ).round(1)

    return result

# ── AgGrid 한글 메뉴 ──
LOCALE_TEXT = {
    "sortAscending":        "오름차순 ↑",
    "sortDescending":       "내림차순 ↓",
    "pinColumn":            "컬럼 고정",
    "pinLeft":              "왼쪽 고정",
    "pinRight":             "오른쪽 고정",
    "noPin":                "고정 해제",
    "autosizeThiscolumn":   "너비 자동조정",
    "autosizeAllColumns":   "전체 너비 자동조정",
    "resetColumns":         "컬럼 초기화",
    "hideColumn":           "컬럼 숨기기",
    "unhide":               "숨기기 해제",
    "chooseCols":           "컬럼 선택",
    "filter":               "필터",
    "noRowsToShow":         "데이터가 없습니다.",
    "filterOoo":            "필터 입력...",
    "equals":               "같음",
    "notEqual":             "같지 않음",
    "lessThan":             "미만",
    "greaterThan":          "초과",
    "lessThanOrEqual":      "이하",
    "greaterThanOrEqual":   "이상",
    "inRange":              "범위",
    "contains":             "포함",
    "notContains":          "미포함",
    "startsWith":           "시작 문자",
    "endsWith":             "끝 문자",
    "andCondition":         "AND",
    "orCondition":          "OR",
    "applyFilter":          "적용",
    "resetFilter":          "초기화",
    "clearFilter":          "지우기",
    "cancelFilter":         "취소",
    "copy":                 "복사",
    "copyWithHeaders":      "헤더 포함 복사",
    "export":               "내보내기",
    "csvExport":            "CSV 다운로드",
    "excelExport":          "엑셀 다운로드",
    "totalRows":            "전체 행",
    "page":                 "페이지",
    "nextPage":             "다음",
    "lastPage":             "마지막",
    "firstPage":            "처음",
    "previousPage":         "이전",
}

def show_aggrid(result_df):
    gb = GridOptionsBuilder.from_dataframe(result_df)
    gb.configure_default_column(
        sortable=True,
        filter=True,
        resizable=True,
        # ✅ 헤더 줄바꿈 허용 → 컬럼명 전체 표시
        wrapHeaderText=True,
        autoHeaderHeight=True,
        suppressMenu=False,
    )

    # ✅ 컬럼별 너비 최적화 (충분히 넓게)
    gb.configure_column("키워드",       minWidth=150, maxWidth=220, pinned="left")
    gb.configure_column("브랜드",       width=70)
    gb.configure_column("경쟁률",       width=80)
    gb.configure_column("작년검색량",   width=110)
    gb.configure_column("최대검색월",   width=100)
    gb.configure_column("피크월검색량", width=110)
    gb.configure_column("계절성",       width=80)
    gb.configure_column("계절성월",     width=120)
    gb.configure_column("경쟁강도",     width=80)
    gb.configure_column("총리뷰수",     width=85)
    gb.configure_column("해외배송(%)",  width=100,
                        valueFormatter="value + '%'")

    grid_options = gb.build()
    grid_options["localeText"] = LOCALE_TEXT

    AgGrid(
        result_df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.NO_UPDATE,
        # ✅ fit_columns_on_grid_load=False → 설정 너비 그대로 사용
        fit_columns_on_grid_load=False,
        height=600,
        theme="alpine",
    )

# ────────────────────────────────────────
# 메인 UI
# ────────────────────────────────────────
st.markdown("""
<div class="main-title">키워드 <span>분석 도구</span></div>
<div class="sub-title">쇼핑성 키워드 선별 및 데이터 전략 분석 도구</div>
""", unsafe_allow_html=True)

# ── 파일 업로드 ──
st.markdown('<div class="card">', unsafe_allow_html=True)
col_up, col_info = st.columns([3, 1])
with col_up:
    uploaded = st.file_uploader(
        "📂 엑셀 파일 업로드 (.xlsx)",
        type=["xlsx"],
        label_visibility="visible")
with col_info:
    if st.session_state.df is not None:
        st.markdown(
            f"<div style='padding-top:28px; color:#4361ee; font-weight:700;'>"
            f"✅ {len(st.session_state.df):,}개 키워드 로드됨</div>",
            unsafe_allow_html=True)
if uploaded:
    file_bytes = uploaded.read()
    st.session_state.df = load_excel(file_bytes)
    st.success(
        f"✅ 파일 로드 완료! 총 **{len(st.session_state.df):,}개** 키워드")
st.markdown('</div>', unsafe_allow_html=True)

# ── 프리셋 선택 바 ──
st.markdown('<div class="card">', unsafe_allow_html=True)
col_btns, col_setting, col_run = st.columns([6, 1, 1])

with col_btns:
    st.markdown("**분석 프리셋 선택**")
    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            label = st.session_state.presets[i]["name"]
            btn_type = "primary" if st.session_state.active_preset == i \
                else "secondary"
            if st.button(label, key=f"preset_btn_{i}",
                         type=btn_type, use_container_width=True):
                st.session_state.active_preset = i
                st.rerun()

with col_setting:
    st.markdown("&nbsp;")
    if st.button("⚙️ 설정", use_container_width=True):
        st.session_state.show_preset_modal = True
        st.rerun()

with col_run:
    st.markdown("&nbsp;")
    run_clicked = st.button(
        "🔍 분석 실행", type="primary", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── 프리셋 설정 모달 ──
if st.session_state.show_preset_modal:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### ⚙️ 프리셋 설정")
    st.markdown("---")

    tabs = st.tabs([st.session_state.presets[i]["name"] for i in range(5)])

    for i, tab in enumerate(tabs):
        with tab:
            p = st.session_state.presets[i]
            new_name = st.text_input(
                "프리셋 이름", value=p["name"], key=f"name_{i}")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<div class="field-label">브랜드키워드</div>',
                            unsafe_allow_html=True)
                new_브랜드 = st.selectbox(
                    "", ["전체", "O", "X"],
                    index=["전체", "O", "X"].index(p["브랜드"]),
                    key=f"브랜드_{i}", label_visibility="collapsed")

                st.markdown('<div class="field-label">작년 검색량 범위</div>',
                            unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    new_작년_min = st.number_input(
                        "최소", value=int(p["작년검색량_min"]),
                        min_value=0, key=f"작년min_{i}")
                with c2:
                    new_작년_max = st.number_input(
                        "최대", value=int(p["작년검색량_max"]),
                        min_value=0, key=f"작년max_{i}")

                st.markdown('<div class="field-label">피크월검색량 범위</div>',
                            unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    new_피크_min = st.number_input(
                        "최소", value=int(p["피크월검색량_min"]),
                        min_value=0, key=f"피크min_{i}")
                with c2:
                    new_피크_max = st.number_input(
                        "최대", value=int(p["피크월검색량_max"]),
                        min_value=0, key=f"피크max_{i}")

                st.markdown('<div class="field-label">쿠팡 총리뷰수 범위</div>',
                            unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    new_리뷰_min = st.number_input(
                        "최소", value=int(p["쿠팡총리뷰수_min"]),
                        min_value=0, key=f"리뷰min_{i}")
                with c2:
                    new_리뷰_max = st.number_input(
                        "최대", value=int(p["쿠팡총리뷰수_max"]),
                        min_value=0, key=f"리뷰max_{i}")

            with col2:
                st.markdown('<div class="field-label">계절성</div>',
                            unsafe_allow_html=True)
                new_시즌 = st.selectbox(
                    "", ["전체", "있음", "없음"],
                    index=["전체", "있음", "없음"].index(p["시즌성"]),
                    key=f"시즌_{i}", label_visibility="collapsed")

                st.markdown(
                    '<div class="field-label">작년 최대검색월 (미선택시 전체)</div>',
                    unsafe_allow_html=True)
                selected_months = p.get("작년최대검색월", [])
                new_월 = []
                month_rows = [[1,2,3],[4,5,6],[7,8,9],[10,11,12]]
                for row in month_rows:
                    cols_m = st.columns(3)
                    for j, month in enumerate(row):
                        with cols_m[j]:
                            month_str = str(month)
                            is_selected = month_str in selected_months
                            if st.checkbox(
                                f"{month}월",
                                value=is_selected,
                                key=f"month_{i}_{month}"
                            ):
                                new_월.append(month_str)

                st.markdown(
                    '<div class="field-label">쿠팡 해외배송비율 범위 (%)</div>',
                    unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    new_해외_min = st.number_input(
                        "최소 (%)",
                        value=int(p["쿠팡해외배송비율_min"]),
                        min_value=0, max_value=100,
                        step=1, key=f"해외min_{i}")
                with c2:
                    new_해외_max = st.number_input(
                        "최대 (%)",
                        value=int(p["쿠팡해외배송비율_max"]),
                        min_value=0, max_value=100,
                        step=1, key=f"해외max_{i}")

            st.info("💡 쇼핑성 키워드는 항상 **O** 로 자동 고정됩니다.")
            st.markdown("<br>", unsafe_allow_html=True)
            s1, s2 = st.columns(2)
            with s1:
                if st.button("💾 설정 저장 및 적용", key=f"save_{i}",
                             type="primary", use_container_width=True):
                    st.session_state.presets[i] = {
                        "name":                 new_name,
                        "브랜드":               new_브랜드,
                        "시즌성":               new_시즌,
                        "작년검색량_min":       int(new_작년_min),
                        "작년검색량_max":       int(new_작년_max),
                        "작년최대검색월":       new_월,
                        "피크월검색량_min":     int(new_피크_min),
                        "피크월검색량_max":     int(new_피크_max),
                        "쿠팡총리뷰수_min":     int(new_리뷰_min),
                        "쿠팡총리뷰수_max":     int(new_리뷰_max),
                        "쿠팡해외배송비율_min": int(new_해외_min),
                        "쿠팡해외배송비율_max": int(new_해외_max),
                    }
                    st.session_state.active_preset = i
                    st.session_state.show_preset_modal = False
                    st.success(f"✅ [{new_name}] 저장 완료!")
                    st.rerun()
            with s2:
                if st.button("취소", key=f"cancel_{i}",
                             use_container_width=True):
                    st.session_state.show_preset_modal = False
                    st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ── 분석 실행 ──
if run_clicked:
    if st.session_state.df is None:
        st.warning("⚠️ 먼저 엑셀 파일을 업로드해 주세요!")
    else:
        df = st.session_state.df
        col_map = get_col_map(df)
        preset = st.session_state.presets[st.session_state.active_preset]
        with st.spinner("🔄 분석 중..."):
            filtered = apply_preset(df, col_map, preset)
            st.session_state.result_df = build_display_df(filtered, col_map)
            st.session_state.filtered_count = len(filtered)

# ── 결과 표시 ──
if st.session_state.result_df is not None:
    result = st.session_state.result_df
    count = st.session_state.filtered_count
    preset_name = st.session_state.presets[
        st.session_state.active_preset]["name"]

    st.markdown('<div class="card">', unsafe_allow_html=True)
    r1, r2 = st.columns([3, 1])
    with r1:
        st.markdown(
            f'<div class="result-count">📊 [{preset_name}] 결과: '
            f'<b>{count:,}개</b> 키워드 '
            f'(해외배송비율 높은 순)</div>',
            unsafe_allow_html=True)
    with r2:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            result.to_excel(writer, index=False, sheet_name="필터결과")
        st.download_button(
            label="⬇️ 엑셀 다운로드",
            data=buffer.getvalue(),
            file_name=f"키워드분석_{preset_name}.xlsx",
            mime="application/vnd.openxmlformats-officedocument"
                 ".spreadsheetml.sheet",
            use_container_width=True)

    show_aggrid(result)
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # ✅ 파일 없을 때 안내 메시지
    if st.session_state.df is None:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align:center; padding:40px; color:#bbb;">
            <div style="font-size:48px;">📂</div>
            <div style="font-size:16px; margin-top:12px;">
                파일을 업로드하고 분석 버튼을 눌러주세요.</div>
            <div style="font-size:13px; margin-top:6px; color:#ccc;">
                데이터가 없습니다.</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.info("📂 파일이 로드됐어요! 프리셋을 선택하고 **분석 실행** 버튼을 눌러주세요.")
        st.markdown('</div>', unsafe_allow_html=True)
