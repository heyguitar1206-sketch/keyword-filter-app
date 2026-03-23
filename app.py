import streamlit as st
import pandas as pd
import io
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.set_page_config(page_title="끝장캐리 키워드 분석", page_icon="🔍", layout="wide")

st.markdown("""
<style>
    /* 전체 배경 */
    .stApp { background-color: #f0f2f5; }

    /* 전체 최대 너비 70% 중앙 정렬 */
    .block-container {
        max-width: 70% !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        margin: 0 auto !important;
    }

    /* 헤더 카드 */
    .header-card {
        background: white;
        border-radius: 16px;
        padding: 24px 32px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.07);
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .header-left .main-title {
        font-size: 26px;
        font-weight: 900;
        color: #1a1a2e;
        margin: 0 0 4px 0;
    }
    .header-left .main-title span {
        color: #3b82f6;
    }
    .header-left .sub-title {
        font-size: 12px;
        color: #888;
        margin: 0;
    }
    .version-badge {
        background: white;
        border: 1.5px solid #3b82f6;
        color: #3b82f6;
        border-radius: 20px;
        padding: 6px 16px;
        font-size: 12px;
        font-weight: 700;
    }

    /* 업로드 카드 */
    .upload-card {
        background: white;
        border-radius: 16px;
        padding: 36px 32px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.07);
        margin-bottom: 20px;
        border: 2px dashed #3b82f6;
        text-align: center;
    }
    .upload-icon { font-size: 36px; margin-bottom: 8px; }
    .upload-title { font-size: 16px; font-weight: 700; color: #1a1a2e; margin-bottom: 4px; }
    .upload-sub { font-size: 12px; color: #888; }

    /* 프리셋 + 액션 카드 */
    .preset-card {
        background: white;
        border-radius: 16px;
        padding: 16px 24px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.07);
        margin-bottom: 20px;
    }

    /* 프리셋 버튼 스타일 */
    .stButton > button {
        border-radius: 20px !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        height: 38px !important;
        border: 1.5px solid #e2e8f0 !important;
        background: white !important;
        color: #374151 !important;
        transition: all 0.2s !important;
    }
    .stButton > button:hover {
        border-color: #3b82f6 !important;
        color: #3b82f6 !important;
    }

    /* 분석실행 버튼 */
    .run-btn > button {
        background: #3b82f6 !important;
        color: white !important;
        border: none !important;
        border-radius: 20px !important;
        font-weight: 800 !important;
        font-size: 14px !important;
        height: 42px !important;
        padding: 0 28px !important;
    }

    /* 다운로드 버튼 */
    .dl-btn > button, .stDownloadButton > button {
        background: #10b981 !important;
        color: white !important;
        border: none !important;
        border-radius: 20px !important;
        font-weight: 800 !important;
        font-size: 14px !important;
        height: 42px !important;
        padding: 0 28px !important;
    }

    /* 결과 테이블 카드 */
    .result-card {
        background: white;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.07);
        margin-bottom: 20px;
    }
    .result-label {
        font-size: 13px;
        color: #6b7280;
        font-weight: 600;
        margin-bottom: 12px;
    }
    .result-label span {
        color: #3b82f6;
        font-weight: 800;
        font-size: 15px;
    }

    /* AgGrid */
    .ag-theme-streamlit {
        width: 100% !important;
        font-size: 14px !important;
        border-radius: 10px !important;
        overflow: hidden !important;
    }
    .ag-header {
        background: #f8fafc !important;
        border-bottom: 2px solid #e2e8f0 !important;
    }
    .ag-header-cell-label {
        font-size: 13px !important;
        font-weight: 700 !important;
        color: #374151 !important;
    }
    .ag-row-even { background: #ffffff !important; }
    .ag-row-odd  { background: #f9fafb !important; }
    .ag-row:hover { background: #eff6ff !important; }
    .ag-cell {
        font-size: 14px !important;
        color: #1f2937 !important;
        border-right: 1px solid #f1f5f9 !important;
    }

    /* 설정 모달 */
    .settings-card {
        background: white;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border: 1px solid #e2e8f0;
    }
    .settings-title {
        font-size: 16px;
        font-weight: 800;
        color: #1a1a2e;
        margin-bottom: 16px;
        padding-bottom: 12px;
        border-bottom: 2px solid #f1f5f9;
    }

    /* 파일 업로더 숨기기/커스텀 */
    div[data-testid="stFileUploader"] {
        max-width: 360px;
        margin: 0 auto;
    }
    div[data-testid="stFileUploader"] label { display: none; }
    div[data-testid="stFileUploader"] section {
        border: none !important;
        background: transparent !important;
        padding: 0 !important;
    }

    /* 탭 스타일 */
    .stTabs [data-baseweb="tab"] {
        font-size: 13px !important;
        font-weight: 700 !important;
    }
    .stTabs [aria-selected="true"] {
        color: #3b82f6 !important;
        border-bottom-color: #3b82f6 !important;
    }

    /* 구분선 제거 */
    hr { display: none; }
</style>
""", unsafe_allow_html=True)

# ── 기본값 & 세션 상태 ──────────────────────────────────────────────
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
if "active_preset"   not in st.session_state: st.session_state.active_preset   = 0
if "show_modal"      not in st.session_state: st.session_state.show_modal       = False
if "df"              not in st.session_state: st.session_state.df               = None
if "result_df"       not in st.session_state: st.session_state.result_df        = None
if "filtered_count"  not in st.session_state: st.session_state.filtered_count   = 0

# ── 데이터 함수 ─────────────────────────────────────────────────────
@st.cache_data
def load_excel(file_bytes):
    raw = pd.read_excel(io.BytesIO(file_bytes), sheet_name="all", header=[0, 1, 2])
    new_cols = []
    for col in raw.columns:
        parts = [str(c).strip() for c in col if str(c).strip() not in ("nan", "")]
        new_cols.append("_".join(dict.fromkeys(parts)) if parts else "unknown")
    raw.columns = new_cols
    return raw.reset_index(drop=True)

def find_col(df, keywords):
    for col in df.columns:
        if all(kw in col for kw in keywords):
            return col
    return None

def find_col_any(df, keyword_sets):
    for keywords in keyword_sets:
        r = find_col(df, keywords)
        if r:
            return r
    return None

def get_col_map(df):
    keyword_col = next(
        (c for c in df.columns if "키워드" in c
         and "신규진입" not in c and "브랜드" not in c and "쇼핑성" not in c),
        None
    )
    peak_col = find_col_any(df, [
        ["피크월", "검색량"], ["최대검색월", "검색량"],
        ["작년최대검색월", "검색량"], ["피크", "검색량"],
    ])
    if not peak_col:
        for c in df.columns:
            if ("검색월" in c and "검색량" in c) or ("피크" in c and "검색량" in c):
                peak_col = c
                break
    return {
        "키워드":           keyword_col,
        "브랜드":           find_col(df, ["브랜드"]),
        "쇼핑성":           find_col(df, ["쇼핑성"]),
        "경쟁률":           find_col(df, ["경쟁률"]),
        "작년검색량":       find_col(df, ["작년", "검색량"]),
        "작년최대검색월":   find_col(df, ["작년최대", "검색월"]),
        "피크월검색량":     peak_col,
        "계절성":           find_col(df, ["계절성"]),
        "쿠팡총리뷰수":     find_col(df, ["쿠팡", "총리뷰수"]),
        "쿠팡해외배송비율": find_col(df, ["쿠팡", "해외배송비율"]),
    }

def normalize_month(val):
    s = str(val).strip()
    if s in ("nan", "None", ""):
        return ""
    if s.endswith("월"):
        try:
            n = int(float(s[:-1]))
            if 1 <= n <= 12:
                return f"{n}월"
        except:
            pass
        return s
    try:
        n = int(float(s))
        if 1 <= n <= 12:
            return f"{n}월"
    except:
        pass
    return s

def apply_preset(df, col_map, preset):
    fdf = df.copy()

    if col_map.get("쇼핑성"):
        fdf = fdf[fdf[col_map["쇼핑성"]].astype(str).str.strip() == "O"]

    if col_map.get("키워드"):
        fdf = fdf.drop_duplicates(subset=[col_map["키워드"]])

    brand = preset.get("브랜드", "전체")
    if col_map.get("브랜드") and brand != "전체":
        fdf = fdf[fdf[col_map["브랜드"]].astype(str).str.strip() == brand]

    season = preset.get("시즌성", "전체")
    if col_map.get("계절성") and season != "전체":
        vals = fdf[col_map["계절성"]].astype(str).str.strip()
        if season == "있음":
            fdf = fdf[vals.isin(["O","o","있음","Y","y","1","True","true"])]
        else:
            fdf = fdf[vals.isin(["X","x","없음","N","n","0","False","false"])]

    if col_map.get("작년검색량"):
        col = col_map["작년검색량"]
        fdf[col] = pd.to_numeric(fdf[col], errors="coerce")
        fdf = fdf[(fdf[col] >= preset.get("작년검색량_min",0)) &
                  (fdf[col] <= preset.get("작년검색량_max",9999999))]

    months = preset.get("작년최대검색월", [])
    if col_map.get("작년최대검색월") and months:
        normalized = fdf[col_map["작년최대검색월"]].apply(normalize_month)
        fdf = fdf[normalized.isin(months)]

    if col_map.get("피크월검색량"):
        col = col_map["피크월검색량"]
        fdf[col] = pd.to_numeric(fdf[col], errors="coerce")
        fdf = fdf[(fdf[col] >= preset.get("피크월검색량_min",0)) &
                  (fdf[col] <= preset.get("피크월검색량_max",9999999))]

    if col_map.get("쿠팡총리뷰수"):
        col = col_map["쿠팡총리뷰수"]
        fdf[col] = pd.to_numeric(fdf[col], errors="coerce")
        fdf = fdf[(fdf[col] >= preset.get("쿠팡총리뷰수_min",0)) &
                  (fdf[col] <= preset.get("쿠팡총리뷰수_max",9999999))]

    if col_map.get("쿠팡해외배송비율"):
        col = col_map["쿠팡해외배송비율"]
        fdf[col] = pd.to_numeric(fdf[col], errors="coerce")
        nn = fdf[col].notna().sum()
        if nn > 0:
            dmax = fdf[col].dropna().max()
            mn_p = preset.get("쿠팡해외배송비율_min", 0)
            mx_p = preset.get("쿠팡해외배송비율_max", 100)
            mn_c = mn_p/100 if dmax <= 1.0 else mn_p
            mx_c = mx_p/100 if dmax <= 1.0 else mx_p
            fdf = fdf[(fdf[col].isna()) | ((fdf[col] >= mn_c) & (fdf[col] <= mx_c))]
        fdf = fdf.sort_values(by=col, ascending=False, na_position="last")

    return fdf.reset_index(drop=True)

def build_display_df(fdf, col_map):
    mapping = [
        ("키워드",           "키워드"),
        ("브랜드",           "브랜드"),
        ("경쟁률",           "경쟁률"),
        ("작년검색량",       "작년검색량"),
        ("작년최대검색월",   "작년최대검색월"),
        ("피크월검색량",     "피크월검색량"),
        ("계절성",           "계절성"),
        ("쿠팡총리뷰수",     "쿠팡총리뷰"),
        ("쿠팡해외배송비율", "쿠팡해외배송비율(%)"),
    ]
    cols_to_use = [(col_map[k], lbl) for k, lbl in mapping
                   if col_map.get(k) and col_map[k] in fdf.columns]
    if not cols_to_use:
        return pd.DataFrame()
    result = fdf[[c for c,_ in cols_to_use]].copy()
    result.columns = [lbl for _,lbl in cols_to_use]

    if "작년최대검색월" in result.columns:
        result["작년최대검색월"] = result["작년최대검색월"].apply(normalize_month)

    if "쿠팡해외배송비율(%)" in result.columns:
        v = pd.to_numeric(result["쿠팡해외배송비율(%)"], errors="coerce")
        result["쿠팡해외배송비율(%)"] = (v*100).round(1) if (not v.dropna().empty and v.dropna().max()<=1.0) else v.round(1)

    return result

LOCALE_TEXT = {
    "page":"페이지","more":"더보기","to":"~","of":"/",
    "next":"다음","last":"마지막","first":"처음","previous":"이전",
    "loadingOoo":"로딩 중...","noRowsToShow":"데이터가 없습니다",
    "filterOoo":"필터...","applyFilter":"필터 적용",
    "equals":"같음","notEqual":"같지 않음","lessThan":"미만","greaterThan":"초과",
    "lessThanOrEqual":"이하","greaterThanOrEqual":"이상","inRange":"범위",
    "contains":"포함","notContains":"미포함","startsWith":"시작","endsWith":"끝",
    "andCondition":"AND","orCondition":"OR","columns":"컬럼","filters":"필터",
    "sortAscending":"오름차순 정렬","sortDescending":"내림차순 정렬",
    "pinColumn":"컬럼 고정","pinLeft":"왼쪽 고정","pinRight":"오른쪽 고정","noPin":"고정 해제",
    "autosizeThiscolumn":"이 컬럼 자동 크기","autosizeAllColumns":"모든 컬럼 자동 크기",
    "resetColumns":"컬럼 초기화","copy":"복사","copyWithHeaders":"헤더 포함 복사",
    "export":"내보내기","csvExport":"CSV 내보내기","excelExport":"엑셀 내보내기",
    "sum":"합계","min":"최솟값","max":"최댓값","none":"없음","count":"개수","average":"평균",
    "filteredRows":"필터된 행","selectedRows":"선택된 행","totalRows":"전체 행",
    "totalAndFilteredRows":"전체/필터 행","blanks":"빈 값","searchOoo":"검색...","selectAll":"전체 선택",
}

def show_aggrid(display_df):
    gb = GridOptionsBuilder.from_dataframe(display_df)
    gb.configure_default_column(
        resizable=True, sortable=True, filter=True,
        wrapHeaderText=True, autoHeaderHeight=True,
        cellStyle={"fontSize": "14px", "color": "#1f2937"},
    )
    col_widths = {
        "키워드":              (180, 260),
        "브랜드":              (70,  85),
        "경쟁률":              (80,  95),
        "작년검색량":          (110, 130),
        "작년최대검색월":      (115, 135),
        "피크월검색량":        (110, 130),
        "계절성":              (75,  90),
        "쿠팡총리뷰":          (95,  115),
        "쿠팡해외배송비율(%)": (125, 150),
    }
    for col, (mn, mx) in col_widths.items():
        if col in display_df.columns:
            gb.configure_column(col, minWidth=mn, maxWidth=mx,
                                cellStyle={"fontSize":"14px","color":"#1f2937"})
    gb.configure_column("키워드", pinned="left")
    gb.configure_grid_options(localeText=LOCALE_TEXT)
    AgGrid(
        display_df,
        gridOptions=gb.build(),
        update_mode=GridUpdateMode.NO_UPDATE,
        fit_columns_on_grid_load=True,
        allow_unsafe_jscode=True,
        height=560,
        theme="streamlit",
        use_container_width=True,
    )

# ══════════════════════════════════════════════
#  UI 렌더링
# ══════════════════════════════════════════════

# ① 헤더
st.markdown("""
<div class="header-card">
  <div class="header-left">
    <p class="main-title">끝장캐리 <span>키워드 분석</span></p>
    <p class="sub-title">쇼핑성 키워드 선별 및 데이터 전략 분석 도구</p>
  </div>
  <div class="version-badge">Premium Version v1.0</div>
</div>
""", unsafe_allow_html=True)

# ② 파일 업로드
st.markdown("""
<div class="upload-card">
  <div class="upload-icon">📁</div>
  <div class="upload-title">분석할 파일을 이곳에 올려주세요</div>
  <div class="upload-sub">엑셀(.xlsx) 파일을 드래그하거나 클릭하여 선택</div>
</div>
""", unsafe_allow_html=True)

uploaded = st.file_uploader("파일 업로드", type=["xlsx"], label_visibility="collapsed")
if uploaded:
    file_bytes = uploaded.read()
    df = load_excel(file_bytes)
    st.session_state.df = df
    col_map_check = get_col_map(df)
    peak_found = col_map_check.get("피크월검색량")
    if peak_found:
        st.success(f"✅ 파일 로드 완료 — 총 {len(df):,}개 키워드")
    else:
        st.warning(f"⚠️ 파일 로드 완료 — 총 {len(df):,}개 | 피크월검색량 컬럼 미확인")
        with st.expander("전체 컬럼 목록 확인"):
            st.write(list(df.columns))

# ③ 프리셋 선택 + 분석실행/다운로드 버튼
st.markdown('<div class="preset-card">', unsafe_allow_html=True)

left_cols = st.columns([1.2, 1, 1, 1, 1, 0.6, 2.5, 1.2, 1.2])

for i in range(5):
    with left_cols[i]:
        p = st.session_state.presets[i]
        is_active = (i == st.session_state.active_preset)
        label = p["name"]
        btn_style = f"""
        <style>
        div[data-testid="stButton"]:nth-of-type({i+1}) > button {{
            background: {'#3b82f6' if is_active else 'white'} !important;
            color: {'white' if is_active else '#374151'} !important;
            border: 1.5px solid {'#3b82f6' if is_active else '#e2e8f0'} !important;
        }}
        </style>
        """
        st.markdown(btn_style, unsafe_allow_html=True)
        if st.button(label, key=f"preset_btn_{i}", use_container_width=True):
            st.session_state.active_preset = i

with left_cols[5]:
    if st.button("⚙️", key="settings_btn", use_container_width=True):
        st.session_state.show_modal = not st.session_state.show_modal

with left_cols[6]:
    st.empty()

with left_cols[7]:
    st.markdown('<div class="run-btn">', unsafe_allow_html=True)
    run_clicked = st.button("🔍 분석 실행", key="run_btn", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with left_cols[8]:
    if st.session_state.result_df is not None and len(st.session_state.result_df) > 0:
        buf = io.BytesIO()
        st.session_state.result_df.to_excel(buf, index=False)
        buf.seek(0)
        st.markdown('<div class="dl-btn">', unsafe_allow_html=True)
        st.download_button(
            "📥 엑셀 다운로드", data=buf,
            file_name=f"키워드분석_{st.session_state.presets[st.session_state.active_preset]['name']}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ④ 설정 모달
if st.session_state.show_modal:
    st.markdown('<div class="settings-card">', unsafe_allow_html=True)
    st.markdown('<div class="settings-title">⚙️ 프리셋 설정</div>', unsafe_allow_html=True)
    tabs = st.tabs([p["name"] for p in st.session_state.presets])
    for i, tab in enumerate(tabs):
        with tab:
            p = st.session_state.presets[i]
            p["name"] = st.text_input("프리셋 이름", value=p["name"], key=f"name_{i}")
            c1, c2 = st.columns(2)
            with c1:
                p["브랜드"] = st.radio("브랜드키워드", ["전체","O","X"],
                    index=["전체","O","X"].index(p.get("브랜드","전체")),
                    key=f"brand_{i}", horizontal=True)
            with c2:
                p["시즌성"] = st.radio("시즌성", ["전체","있음","없음"],
                    index=["전체","있음","없음"].index(p.get("시즌성","전체")),
                    key=f"season_{i}", horizontal=True)

            st.markdown("**작년검색량 범위**")
            c3, c4 = st.columns(2)
            with c3:
                p["작년검색량_min"] = st.number_input("최소", value=p.get("작년검색량_min",0), step=1000, key=f"ys_min_{i}")
            with c4:
                p["작년검색량_max"] = st.number_input("최대", value=p.get("작년검색량_max",9999999), step=1000, key=f"ys_max_{i}")

            st.markdown("**작년 최대검색월 (다중선택)**")
            month_rows = [["1월","2월","3월","4월"],["5월","6월","7월","8월"],["9월","10월","11월","12월"]]
            selected = p.get("작년최대검색월", [])
            new_months = []
            for row in month_rows:
                cols = st.columns(4)
                for j, m in enumerate(row):
                    with cols[j]:
                        if st.checkbox(m, value=(m in selected), key=f"month_{i}_{m}"):
                            new_months.append(m)
            p["작년최대검색월"] = new_months

            st.markdown("**피크월검색량 범위**")
            c5, c6 = st.columns(2)
            with c5:
                p["피크월검색량_min"] = st.number_input("최소", value=p.get("피크월검색량_min",0), step=1000, key=f"pk_min_{i}")
            with c6:
                p["피크월검색량_max"] = st.number_input("최대", value=p.get("피크월검색량_max",9999999), step=1000, key=f"pk_max_{i}")

            st.markdown("**쿠팡 총리뷰수 범위**")
            c7, c8 = st.columns(2)
            with c7:
                p["쿠팡총리뷰수_min"] = st.number_input("최소", value=p.get("쿠팡총리뷰수_min",0), step=100, key=f"rv_min_{i}")
            with c8:
                p["쿠팡총리뷰수_max"] = st.number_input("최대", value=p.get("쿠팡총리뷰수_max",9999999), step=100, key=f"rv_max_{i}")

            st.markdown("**쿠팡 해외배송비율 범위 (%)**")
            c9, c10 = st.columns(2)
            with c9:
                p["쿠팡해외배송비율_min"] = st.number_input("최소(%)", value=p.get("쿠팡해외배송비율_min",0),
                    min_value=0, max_value=100, key=f"ob_min_{i}")
            with c10:
                p["쿠팡해외배송비율_max"] = st.number_input("최대(%)", value=p.get("쿠팡해외배송비율_max",100),
                    min_value=0, max_value=100, key=f"ob_max_{i}")
    st.markdown('</div>', unsafe_allow_html=True)

# ⑤ 분석 실행
if run_clicked:
    if st.session_state.df is None:
        st.error("먼저 엑셀 파일을 업로드해 주세요.")
    else:
        col_map = get_col_map(st.session_state.df)
        preset  = st.session_state.presets[st.session_state.active_preset]
        filtered = apply_preset(st.session_state.df, col_map, preset)
        st.session_state.result_df     = build_display_df(filtered, col_map)
        st.session_state.filtered_count = len(filtered)

# ⑥ 결과 테이블
if st.session_state.result_df is not None:
    result = st.session_state.result_df
    preset_name = st.session_state.presets[st.session_state.active_preset]["name"]
    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="result-label">필터 결과: <span>{st.session_state.filtered_count:,}개</span> 키워드 ({preset_name})</div>',
        unsafe_allow_html=True
    )
    if len(result) > 0:
        show_aggrid(result)
    else:
        st.warning("조건에 맞는 키워드가 없습니다. 필터 조건을 완화해 보세요.")
    st.markdown('</div>', unsafe_allow_html=True)
else:
    if st.session_state.df is None:
        st.markdown('<div class="result-card" style="text-align:center; color:#888; padding:40px;">📂 엑셀 파일을 업로드한 후 분석을 실행하세요.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="result-card" style="text-align:center; color:#888; padding:40px;">✅ 파일 로드 완료. 프리셋 조건을 설정하고 <b>분석 실행</b>을 눌러주세요.</div>', unsafe_allow_html=True)
