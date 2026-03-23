import streamlit as st
import pandas as pd
import io
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.set_page_config(page_title="키워드 분석 도구", page_icon="🔍", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #f5f7fb; }
    .main-title { font-size: 28px; font-weight: 800; color: #1a1a2e; margin-bottom: 4px; }
    .main-title span { color: #4361ee; }
    .sub-title { font-size: 13px; color: #888; margin-bottom: 20px; }
    .card { background: white; border-radius: 16px; padding: 24px; box-shadow: 0 2px 12px rgba(0,0,0,0.07); margin-bottom: 20px; }
    .result-count { font-size: 15px; color: #4361ee; font-weight: 700; padding: 8px 0; }
    .field-label { font-size: 13px; font-weight: 700; color: #333; margin-bottom: 4px; }
    .stButton > button { border-radius: 24px !important; font-weight: 800 !important; }
    div[data-testid="stFileUploader"] { max-width: 480px; }
</style>
""", unsafe_allow_html=True)

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
    st.session_state.presets = [
        {**DEFAULT_PRESET, "name": "시즌소싱 26년봄"},
        {**DEFAULT_PRESET, "name": "비시즌 가구"},
        {**DEFAULT_PRESET, "name": "프리셋 3"},
        {**DEFAULT_PRESET, "name": "프리셋 4"},
        {**DEFAULT_PRESET, "name": "프리셋 5"},
    ]
if "active_preset" not in st.session_state:
    st.session_state.active_preset = 0
if "show_modal" not in st.session_state:
    st.session_state.show_modal = False
if "df" not in st.session_state:
    st.session_state.df = None
if "result_df" not in st.session_state:
    st.session_state.result_df = None
if "filtered_count" not in st.session_state:
    st.session_state.filtered_count = 0
if "debug_mode" not in st.session_state:
    st.session_state.debug_mode = False

@st.cache_data
def load_excel(file_bytes):
    raw = pd.read_excel(io.BytesIO(file_bytes), sheet_name="all", header=[0, 1, 2])
    new_cols = []
    for col in raw.columns:
        parts = [str(c).strip() for c in col if str(c).strip() not in ("nan", "")]
        merged = "_".join(dict.fromkeys(parts)) if parts else "unknown"
        new_cols.append(merged)
    raw.columns = new_cols
    return raw.reset_index(drop=True)

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
        "키워드": keyword_col,
        "브랜드": find_col(df, ["브랜드"]),
        "쇼핑성": find_col(df, ["쇼핑성"]),
        "경쟁률": find_col(df, ["경쟁률"]),
        "작년검색량": find_col(df, ["작년", "검색량"]),
        "작년최대검색월": find_col(df, ["작년최대", "검색월"]),
        "피크월검색량": find_col(df, ["피크월", "검색량"]),
        "계절성": find_col(df, ["계절성"]),
        "쿠팡총리뷰수": find_col(df, ["쿠팡", "총리뷰수"]),
        "쿠팡해외배송비율": find_col(df, ["쿠팡", "해외배송비율"]),
    }

def apply_preset(df, col_map, preset, debug=False):
    fdf = df.copy()
    steps = []

    total_start = len(fdf)
    steps.append(f"📊 시작 데이터: {total_start}행")

    # 1. 쇼핑성 고정 O
    if col_map.get("쇼핑성"):
        col = col_map["쇼핑성"]
        before = len(fdf)
        vals = fdf[col].astype(str).str.strip()
        if debug:
            unique_vals = vals.unique().tolist()
            steps.append(f"🛒 쇼핑성 컬럼({col}) 고유값: {unique_vals}")
        fdf = fdf[vals == "O"]
        steps.append(f"✅ 쇼핑성=O 필터 후: {len(fdf)}행 (제거: {before - len(fdf)}행)")
    else:
        steps.append("⚠️ 쇼핑성 컬럼을 찾지 못함 - 필터 건너뜀")

    # 2. 키워드 중복 제거
    if col_map.get("키워드"):
        before = len(fdf)
        fdf = fdf.drop_duplicates(subset=[col_map["키워드"]])
        steps.append(f"🔑 키워드 중복 제거 후: {len(fdf)}행 (제거: {before - len(fdf)}행)")

    # 3. 브랜드 필터
    brand_filter = preset.get("브랜드", "전체")
    if col_map.get("브랜드") and brand_filter != "전체":
        col = col_map["브랜드"]
        before = len(fdf)
        vals = fdf[col].astype(str).str.strip()
        if debug:
            steps.append(f"🏷️ 브랜드 컬럼({col}) 고유값: {vals.unique().tolist()}")
        fdf = fdf[vals == brand_filter]
        steps.append(f"🏷️ 브랜드={brand_filter} 필터 후: {len(fdf)}행 (제거: {before - len(fdf)}행)")

    # 4. 시즌성 필터
    season_filter = preset.get("시즌성", "전체")
    if col_map.get("계절성") and season_filter != "전체":
        col = col_map["계절성"]
        before = len(fdf)
        vals = fdf[col].astype(str).str.strip()
        if debug:
            steps.append(f"🌸 계절성 컬럼({col}) 고유값: {vals.unique().tolist()}")
        if season_filter == "있음":
            fdf = fdf[vals == "O"]
        elif season_filter == "없음":
            fdf = fdf[vals == "X"]
        steps.append(f"🌸 시즌성={season_filter} 필터 후: {len(fdf)}행 (제거: {before - len(fdf)}행)")

    # 5. 작년검색량 범위
    if col_map.get("작년검색량"):
        col = col_map["작년검색량"]
        fdf[col] = pd.to_numeric(fdf[col], errors="coerce")
        before = len(fdf)
        mn, mx = preset.get("작년검색량_min", 0), preset.get("작년검색량_max", 9999999)
        if debug:
            steps.append(f"📈 작년검색량 컬럼({col}) 샘플값: {fdf[col].dropna().head(5).tolist()}")
        fdf = fdf[(fdf[col] >= mn) & (fdf[col] <= mx)]
        steps.append(f"📈 작년검색량 {mn}~{mx} 필터 후: {len(fdf)}행 (제거: {before - len(fdf)}행)")

    # 6. 작년최대검색월 (다중선택)
    selected_months = preset.get("작년최대검색월", [])
    if col_map.get("작년최대검색월") and selected_months:
        col = col_map["작년최대검색월"]
        before = len(fdf)
        vals = fdf[col].astype(str).str.strip()
        if debug:
            steps.append(f"📅 작년최대검색월 컬럼({col}) 고유값: {vals.unique().tolist()}")
            steps.append(f"📅 선택된 월: {selected_months}")
        fdf = fdf[vals.isin(selected_months)]
        steps.append(f"📅 최대검색월 필터 후: {len(fdf)}행 (제거: {before - len(fdf)}행)")

    # 7. 피크월검색량 범위
    if col_map.get("피크월검색량"):
        col = col_map["피크월검색량"]
        fdf[col] = pd.to_numeric(fdf[col], errors="coerce")
        before = len(fdf)
        mn, mx = preset.get("피크월검색량_min", 0), preset.get("피크월검색량_max", 9999999)
        fdf = fdf[(fdf[col] >= mn) & (fdf[col] <= mx)]
        steps.append(f"📊 피크월검색량 {mn}~{mx} 필터 후: {len(fdf)}행 (제거: {before - len(fdf)}행)")

    # 8. 쿠팡 총리뷰수 범위
    if col_map.get("쿠팡총리뷰수"):
        col = col_map["쿠팡총리뷰수"]
        fdf[col] = pd.to_numeric(fdf[col], errors="coerce")
        before = len(fdf)
        mn, mx = preset.get("쿠팡총리뷰수_min", 0), preset.get("쿠팡총리뷰수_max", 9999999)
        fdf = fdf[(fdf[col] >= mn) & (fdf[col] <= mx)]
        steps.append(f"⭐ 쿠팡총리뷰 {mn}~{mx} 필터 후: {len(fdf)}행 (제거: {before - len(fdf)}행)")

    # 9. 쿠팡 해외배송비율 범위
    if col_map.get("쿠팡해외배송비율"):
        col = col_map["쿠팡해외배송비율"]
        fdf[col] = pd.to_numeric(fdf[col], errors="coerce")
        before = len(fdf)
        mn = preset.get("쿠팡해외배송비율_min", 0) / 100
        mx = preset.get("쿠팡해외배송비율_max", 100) / 100
        if debug:
            steps.append(f"🚢 해외배송비율 컬럼({col}) 샘플값: {fdf[col].dropna().head(5).tolist()}")
        fdf = fdf[(fdf[col] >= mn) & (fdf[col] <= mx)]
        steps.append(f"🚢 쿠팡해외배송비율 {mn*100:.0f}%~{mx*100:.0f}% 필터 후: {len(fdf)}행 (제거: {before - len(fdf)}행)")

    # 정렬
    if col_map.get("쿠팡해외배송비율"):
        fdf = fdf.sort_values(by=col_map["쿠팡해외배송비율"], ascending=False)

    return fdf.reset_index(drop=True), steps

def build_display_df(fdf, col_map):
    mapping = [
        ("키워드", "키워드"),
        ("브랜드", "브랜드"),
        ("경쟁률", "경쟁률"),
        ("작년검색량", "작년검색량"),
        ("작년최대검색월", "작년최대검색월"),
        ("피크월검색량", "피크월검색량"),
        ("계절성", "계절성"),
        ("쿠팡총리뷰수", "쿠팡총리뷰"),
        ("쿠팡해외배송비율", "쿠팡해외배송비율(%)"),
    ]
    cols_to_use = [(col_map[k], label) for k, label in mapping if col_map.get(k) and col_map[k] in fdf.columns]
    if not cols_to_use:
        return pd.DataFrame()
    result = fdf[[c for c, _ in cols_to_use]].copy()
    result.columns = [label for _, label in cols_to_use]
    if "쿠팡해외배송비율(%)" in result.columns:
        result["쿠팡해외배송비율(%)"] = (
            pd.to_numeric(result["쿠팡해외배송비율(%)"], errors="coerce") * 100
        ).round(1)
    return result

LOCALE_TEXT = {
    "page": "페이지",
    "more": "더보기",
    "to": "~",
    "of": "/",
    "next": "다음",
    "last": "마지막",
    "first": "처음",
    "previous": "이전",
    "loadingOoo": "로딩 중...",
    "noRowsToShow": "데이터가 없습니다",
    "filterOoo": "필터...",
    "applyFilter": "필터 적용",
    "equals": "같음",
    "notEqual": "같지 않음",
    "lessThan": "미만",
    "greaterThan": "초과",
    "lessThanOrEqual": "이하",
    "greaterThanOrEqual": "이상",
    "inRange": "범위",
    "contains": "포함",
    "notContains": "미포함",
    "startsWith": "시작",
    "endsWith": "끝",
    "andCondition": "AND",
    "orCondition": "OR",
    "columns": "컬럼",
    "filters": "필터",
    "sortAscending": "오름차순 정렬",
    "sortDescending": "내림차순 정렬",
    "pinColumn": "컬럼 고정",
    "pinLeft": "왼쪽 고정",
    "pinRight": "오른쪽 고정",
    "noPin": "고정 해제",
    "autosizeThiscolumn": "이 컬럼 자동 크기",
    "autosizeAllColumns": "모든 컬럼 자동 크기",
    "resetColumns": "컬럼 초기화",
    "copy": "복사",
    "copyWithHeaders": "헤더 포함 복사",
    "export": "내보내기",
    "csvExport": "CSV 내보내기",
    "excelExport": "엑셀 내보내기",
    "sum": "합계",
    "min": "최솟값",
    "max": "최댓값",
    "none": "없음",
    "count": "개수",
    "average": "평균",
    "filteredRows": "필터된 행",
    "selectedRows": "선택된 행",
    "totalRows": "전체 행",
    "totalAndFilteredRows": "전체/필터 행",
    "blanks": "빈 값",
    "searchOoo": "검색...",
    "selectAll": "전체 선택",
}

def show_aggrid(display_df):
    gb = GridOptionsBuilder.from_dataframe(display_df)
    gb.configure_default_column(
        resizable=True,
        sortable=True,
        filter=True,
        wrapHeaderText=True,
        autoHeaderHeight=True,
    )
    col_widths = {
        "키워드": (140, 200),
        "브랜드": (55, 70),
        "경쟁률": (65, 80),
        "작년검색량": (90, 110),
        "작년최대검색월": (95, 115),
        "피크월검색량": (90, 110),
        "계절성": (60, 75),
        "쿠팡총리뷰": (80, 100),
        "쿠팡해외배송비율(%)": (110, 130),
    }
    for col, (mn, mx) in col_widths.items():
        if col in display_df.columns:
            gb.configure_column(col, minWidth=mn, maxWidth=mx)
    gb.configure_column("키워드", pinned="left")
    gb.configure_grid_options(localeText=LOCALE_TEXT)
    grid_options = gb.build()
    AgGrid(
        display_df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.NO_UPDATE,
        fit_columns_on_grid_load=False,
        allow_unsafe_jscode=True,
        height=500,
        theme="streamlit",
    )

# ─── UI ───────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">🔍 <span>키워드</span> 분석 도구</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">엑셀 파일을 업로드하고 프리셋 조건으로 키워드를 필터링하세요</div>', unsafe_allow_html=True)

# 파일 업로드
uploaded = st.file_uploader("엑셀 파일 업로드 (.xlsx)", type=["xlsx"], label_visibility="collapsed")
if uploaded:
    file_bytes = uploaded.read()
    df = load_excel(file_bytes)
    st.session_state.df = df
    st.success(f"✅ 파일 로드 완료 — 총 {len(df):,}개 키워드")

# 디버그 모드 토글
st.session_state.debug_mode = st.checkbox("🔧 디버그 모드 (필터 단계별 확인)", value=st.session_state.debug_mode)

st.markdown("---")

# 프리셋 선택 버튼
st.markdown("**프리셋 선택**")
preset_cols = st.columns(6)
for i, preset in enumerate(st.session_state.presets):
    with preset_cols[i]:
        label = f"{'✅ ' if i == st.session_state.active_preset else ''}{preset['name']}"
        if st.button(label, key=f"preset_btn_{i}", use_container_width=True):
            st.session_state.active_preset = i

with preset_cols[5]:
    if st.button("⚙️ 설정", use_container_width=True):
        st.session_state.show_modal = not st.session_state.show_modal

# 프리셋 설정 모달
if st.session_state.show_modal:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**프리셋 설정**")
    tabs = st.tabs([p["name"] for p in st.session_state.presets])
    for i, tab in enumerate(tabs):
        with tab:
            p = st.session_state.presets[i]
            p["name"] = st.text_input("프리셋 이름", value=p["name"], key=f"name_{i}")
            c1, c2 = st.columns(2)
            with c1:
                p["브랜드"] = st.radio("브랜드키워드", ["전체", "O", "X"], index=["전체","O","X"].index(p.get("브랜드","전체")), key=f"brand_{i}", horizontal=True)
            with c2:
                p["시즌성"] = st.radio("시즌성", ["전체", "있음", "없음"], index=["전체","있음","없음"].index(p.get("시즌성","전체")), key=f"season_{i}", horizontal=True)

            st.markdown("**작년검색량 범위**")
            c3, c4 = st.columns(2)
            with c3:
                p["작년검색량_min"] = st.number_input("최소", value=p.get("작년검색량_min", 0), step=1000, key=f"ys_min_{i}")
            with c4:
                p["작년검색량_max"] = st.number_input("최대", value=p.get("작년검색량_max", 9999999), step=1000, key=f"ys_max_{i}")

            st.markdown("**작년 최대검색월 (다중선택)**")
            month_rows = [["1월","2월","3월","4월"], ["5월","6월","7월","8월"], ["9월","10월","11월","12월"]]
            selected_months = p.get("작년최대검색월", [])
            new_months = []
            for row in month_rows:
                cols = st.columns(4)
                for j, month in enumerate(row):
                    with cols[j]:
                        if st.checkbox(month, value=(month in selected_months), key=f"month_{i}_{month}"):
                            new_months.append(month)
            p["작년최대검색월"] = new_months

            st.markdown("**피크월검색량 범위**")
            c5, c6 = st.columns(2)
            with c5:
                p["피크월검색량_min"] = st.number_input("최소", value=p.get("피크월검색량_min", 0), step=1000, key=f"pk_min_{i}")
            with c6:
                p["피크월검색량_max"] = st.number_input("최대", value=p.get("피크월검색량_max", 9999999), step=1000, key=f"pk_max_{i}")

            st.markdown("**쿠팡 총리뷰수 범위**")
            c7, c8 = st.columns(2)
            with c7:
                p["쿠팡총리뷰수_min"] = st.number_input("최소", value=p.get("쿠팡총리뷰수_min", 0), step=100, key=f"rv_min_{i}")
            with c8:
                p["쿠팡총리뷰수_max"] = st.number_input("최대", value=p.get("쿠팡총리뷰수_max", 9999999), step=100, key=f"rv_max_{i}")

            st.markdown("**쿠팡 해외배송비율 범위 (%)**")
            c9, c10 = st.columns(2)
            with c9:
                p["쿠팡해외배송비율_min"] = st.number_input("최소(%)", value=p.get("쿠팡해외배송비율_min", 0), min_value=0, max_value=100, key=f"ob_min_{i}")
            with c10:
                p["쿠팡해외배송비율_max"] = st.number_input("최대(%)", value=p.get("쿠팡해외배송비율_max", 100), min_value=0, max_value=100, key=f"ob_max_{i}")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# 분석 실행
if st.button("🔍 분석 실행", type="primary", use_container_width=False):
    if st.session_state.df is None:
        st.error("먼저 엑셀 파일을 업로드해 주세요.")
    else:
        df = st.session_state.df
        col_map = get_col_map(df)
        preset = st.session_state.presets[st.session_state.active_preset]
        filtered, steps = apply_preset(df, col_map, preset, debug=st.session_state.debug_mode)
        st.session_state.result_df = build_display_df(filtered, col_map)
        st.session_state.filtered_count = len(filtered)
        st.session_state.filter_steps = steps

        # 컬럼 매핑 디버그 표시
        if st.session_state.debug_mode:
            st.markdown("**🗂️ 컬럼 매핑 결과**")
            for k, v in col_map.items():
                st.write(f"`{k}` → `{v}`")

# 필터 단계 표시 (디버그 모드)
if st.session_state.debug_mode and "filter_steps" in st.session_state:
    st.markdown("**🔎 필터 단계별 결과**")
    for step in st.session_state.filter_steps:
        st.write(step)

# 결과 표시
if st.session_state.result_df is not None:
    result = st.session_state.result_df
    preset_name = st.session_state.presets[st.session_state.active_preset]["name"]
    st.markdown(f'<div class="result-count">📋 필터 결과: <b>{st.session_state.filtered_count:,}개</b> 키워드 ({preset_name})</div>', unsafe_allow_html=True)

    if len(result) > 0:
        buf = io.BytesIO()
        result.to_excel(buf, index=False)
        buf.seek(0)
        st.download_button("📥 엑셀 다운로드", data=buf, file_name=f"키워드분석_{preset_name}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        show_aggrid(result)
    else:
        st.warning("조건에 맞는 키워드가 없습니다. 필터 조건을 완화해 보세요.")
        if not st.session_state.debug_mode:
            st.info("💡 '디버그 모드'를 켜고 다시 분석 실행하면 어느 단계에서 데이터가 제거되는지 확인할 수 있습니다.")
else:
    if st.session_state.df is None:
        st.markdown('<div class="card">📂 엑셀 파일을 업로드한 후 프리셋을 선택하고 분석을 실행하세요.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="card">✅ 파일이 로드되었습니다. 프리셋 조건을 설정하고 <b>분석 실행</b>을 눌러주세요.</div>', unsafe_allow_html=True)
