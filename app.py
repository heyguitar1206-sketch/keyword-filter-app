import streamlit as st
import pandas as pd
import io
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.set_page_config(page_title="끝장캐리 키워드 분석", page_icon="🔍", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap');
* { font-family: 'Noto Sans KR', sans-serif !important; box-sizing: border-box; }

/* 전체 배경 */
.stApp { background-color: #eef0f5 !important; }

/* 중앙 정렬 컨테이너 */
.block-container {
    max-width: 860px !important;
    margin: 0 auto !important;
    padding: 28px 20px 40px !important;
}

/* 공통 카드 */
.card {
    background: #ffffff;
    border-radius: 14px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.07);
    margin-bottom: 12px;
}

/* ── 헤더 ── */
.card-header {
    padding: 18px 26px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.title-main { font-size: 21px; font-weight: 900; color: #111827; margin: 0 0 2px; line-height:1.2; }
.title-main em { font-style:normal; color: #3b5bff; }
.title-sub  { font-size: 11px; color: #9ca3af; margin: 0; }
.badge {
    border: 1.5px solid #3b5bff; color: #3b5bff;
    border-radius: 20px; padding: 4px 12px;
    font-size: 11px; font-weight: 700; white-space: nowrap;
}

/* ── 업로드 ── */
.card-upload {
    padding: 30px 24px 22px;
    text-align: center;
    border: 2.5px dashed #93a8ff;
    cursor: pointer;
}
.upload-circle {
    width: 48px; height: 48px; border-radius: 50%;
    background: #eef1ff; margin: 0 auto 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px;
}
.upload-title { font-size: 14px; font-weight: 700; color: #111827; margin-bottom: 4px; }
.upload-sub   { font-size: 11px; color: #9ca3af; }
.file-badge   {
    display: inline-block; margin-top: 10px;
    background: #eef1ff; color: #3b5bff;
    border-radius: 20px; padding: 4px 14px;
    font-size: 12px; font-weight: 700;
}

/* Streamlit 파일업로더 숨김 */
div[data-testid="stFileUploader"] {
    height: 0 !important; overflow: hidden !important;
    position: absolute !important; opacity: 0 !important;
    pointer-events: none !important;
}

/* ── 프리셋 바 ── */
.card-preset { padding: 12px 20px; }

/* 모든 Streamlit 버튼 기본 리셋 */
div[data-testid="stButton"] > button {
    border-radius: 20px !important;
    font-weight: 600 !important;
    font-size: 12.5px !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    height: 33px !important;
    min-height: 33px !important;
    padding: 0 14px !important;
    border: 1.5px solid #e5e7eb !important;
    background: #ffffff !important;
    color: #374151 !important;
    transition: all 0.15s !important;
    line-height: 1 !important;
    box-shadow: none !important;
}
div[data-testid="stButton"] > button:hover {
    border-color: #3b5bff !important;
    color: #3b5bff !important;
    background: #f5f6ff !important;
    box-shadow: none !important;
}

/* 활성 프리셋 */
.btn-active div[data-testid="stButton"] > button {
    background: #3b5bff !important;
    color: #ffffff !important;
    border-color: #3b5bff !important;
}
.btn-active div[data-testid="stButton"] > button:hover {
    background: #2a47e8 !important;
}

/* 분석실행 */
.btn-run div[data-testid="stButton"] > button {
    background: #3b5bff !important;
    color: #ffffff !important;
    border-color: #3b5bff !important;
    height: 36px !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    padding: 0 18px !important;
}
.btn-run div[data-testid="stButton"] > button:hover { background: #2a47e8 !important; }

/* 다운로드 */
div[data-testid="stDownloadButton"] > button {
    background: #10b981 !important; color: #ffffff !important;
    border: none !important; border-radius: 20px !important;
    font-weight: 700 !important; font-size: 13px !important;
    height: 36px !important; width: 100% !important;
    white-space: nowrap !important; padding: 0 16px !important;
}
div[data-testid="stDownloadButton"] > button:hover { background: #059669 !important; }

/* 비활성 다운로드 */
.btn-dl-off div[data-testid="stButton"] > button {
    background: #f3f4f6 !important; color: #d1d5db !important;
    border-color: #f3f4f6 !important;
    height: 36px !important; font-size: 13px !important;
    font-weight: 700 !important; padding: 0 16px !important;
    cursor: not-allowed !important;
}

/* 기어 버튼 */
.btn-gear div[data-testid="stButton"] > button {
    padding: 0 10px !important; font-size: 14px !important;
    color: #6b7280 !important;
}

/* ── 결과 카드 ── */
.card-result { padding: 18px 22px; min-height: 100px; }
.result-meta { font-size: 12px; color: #6b7280; font-weight: 600; margin-bottom: 12px; }
.result-meta b { color: #3b5bff; font-size: 14px; }
.empty-hint { text-align:center; color:#b0b7c3; font-size:12px; padding: 28px 0; }

/* ── 설정 패널 ── */
.card-settings { padding: 20px 22px; border: 1px solid #e5e7eb; }

/* AgGrid */
.ag-theme-streamlit { width: 100% !important; }
.ag-header { background: #f8fafc !important; border-bottom: 2px solid #e5e7eb !important; }
.ag-header-cell-label { font-size: 12px !important; font-weight: 700 !important; color: #374151 !important; }
.ag-row-even { background: #ffffff !important; }
.ag-row-odd  { background: #f9fafb !important; }
.ag-row:hover { background: #eef2ff !important; }
.ag-cell { font-size: 13px !important; color: #1f2937 !important; }

/* 기타 */
hr { display: none !important; }
.stTabs [data-baseweb="tab"] { font-size: 13px !important; font-weight: 600 !important; }
.stTabs [aria-selected="true"] { color: #3b5bff !important; border-bottom-color: #3b5bff !important; }

/* Streamlit 기본 여백 제거 */
.element-container { margin-bottom: 0 !important; }
div[data-testid="stVerticalBlock"] > div { gap: 0 !important; }
</style>
""", unsafe_allow_html=True)

# ── 세션 상태 ─────────────────────────────────────────
DEFAULT_PRESET = {
    "name": "프리셋",
    "브랜드": "전체", "시즌성": "전체",
    "작년검색량_min": 0, "작년검색량_max": 9999999,
    "작년최대검색월": [],
    "피크월검색량_min": 0, "피크월검색량_max": 9999999,
    "쿠팡총리뷰수_min": 0, "쿠팡총리뷰수_max": 9999999,
    "쿠팡해외배송비율_min": 0, "쿠팡해외배송비율_max": 100,
}
if "presets" not in st.session_state:
    st.session_state.presets = [
        {**DEFAULT_PRESET, "name": "시즌소싱 26년봄"},
        {**DEFAULT_PRESET, "name": "비시즌 가구"},
        {**DEFAULT_PRESET, "name": "프리셋 3"},
        {**DEFAULT_PRESET, "name": "프리셋 4"},
        {**DEFAULT_PRESET, "name": "프리셋 5"},
    ]
for _k, _v in [("active_preset",0),("show_modal",False),
               ("df",None),("result_df",None),("filtered_count",0),("uploaded_name","")]:
    if _k not in st.session_state: st.session_state[_k] = _v

# ── 데이터 함수 ───────────────────────────────────────
@st.cache_data
def load_excel(file_bytes):
    raw = pd.read_excel(io.BytesIO(file_bytes), sheet_name="all", header=[0,1,2])
    cols = []
    for col in raw.columns:
        parts = [str(c).strip() for c in col if str(c).strip() not in ("nan","")]
        cols.append("_".join(dict.fromkeys(parts)) if parts else "unknown")
    raw.columns = cols
    return raw.reset_index(drop=True)

def find_col(df, kws):
    for col in df.columns:
        if all(k in col for k in kws): return col
    return None

def get_col_map(df):
    kw = next((c for c in df.columns if "키워드" in c
               and "신규진입" not in c and "브랜드" not in c and "쇼핑성" not in c), None)
    peak = None
    for kws in [["피크월","검색량"],["최대검색월","검색량"],["피크","검색량"]]:
        peak = find_col(df, kws)
        if peak: break
    if not peak:
        for c in df.columns:
            if ("검색월" in c and "검색량" in c) or ("피크" in c and "검색량" in c):
                peak = c; break
    return {
        "키워드": kw, "브랜드": find_col(df,["브랜드"]),
        "쇼핑성": find_col(df,["쇼핑성"]), "경쟁률": find_col(df,["경쟁률"]),
        "작년검색량": find_col(df,["작년","검색량"]),
        "작년최대검색월": find_col(df,["작년최대","검색월"]),
        "피크월검색량": peak, "계절성": find_col(df,["계절성"]),
        "쿠팡총리뷰수": find_col(df,["쿠팡","총리뷰수"]),
        "쿠팡해외배송비율": find_col(df,["쿠팡","해외배송비율"]),
    }

def normalize_month(val):
    s = str(val).strip()
    if s in ("nan","None",""): return ""
    if s.endswith("월"):
        try:
            n = int(float(s[:-1]))
            if 1 <= n <= 12: return f"{n}월"
        except: pass
        return s
    try:
        n = int(float(s))
        if 1 <= n <= 12: return f"{n}월"
    except: pass
    return s

def apply_preset(df, cm, preset):
    f = df.copy()
    if cm.get("쇼핑성"):
        f = f[f[cm["쇼핑성"]].astype(str).str.strip()=="O"]
    if cm.get("키워드"):
        f = f.drop_duplicates(subset=[cm["키워드"]])
    brand = preset.get("브랜드","전체")
    if cm.get("브랜드") and brand!="전체":
        f = f[f[cm["브랜드"]].astype(str).str.strip()==brand]
    season = preset.get("시즌성","전체")
    if cm.get("계절성") and season!="전체":
        v = f[cm["계절성"]].astype(str).str.strip()
        f = f[v.isin(["O","o","있음","Y","y","1"])] if season=="있음" \
            else f[v.isin(["X","x","없음","N","n","0"])]
    if cm.get("작년검색량"):
        c=cm["작년검색량"]; f[c]=pd.to_numeric(f[c],errors="coerce")
        f=f[(f[c]>=preset.get("작년검색량_min",0))&(f[c]<=preset.get("작년검색량_max",9999999))]
    months = preset.get("작년최대검색월",[])
    if cm.get("작년최대검색월") and months:
        f=f[f[cm["작년최대검색월"]].apply(normalize_month).isin(months)]
    if cm.get("피크월검색량"):
        c=cm["피크월검색량"]; f[c]=pd.to_numeric(f[c],errors="coerce")
        f=f[(f[c]>=preset.get("피크월검색량_min",0))&(f[c]<=preset.get("피크월검색량_max",9999999))]
    if cm.get("쿠팡총리뷰수"):
        c=cm["쿠팡총리뷰수"]; f[c]=pd.to_numeric(f[c],errors="coerce")
        f=f[(f[c]>=preset.get("쿠팡총리뷰수_min",0))&(f[c]<=preset.get("쿠팡총리뷰수_max",9999999))]
    if cm.get("쿠팡해외배송비율"):
        c=cm["쿠팡해외배송비율"]; f[c]=pd.to_numeric(f[c],errors="coerce")
        nn=f[c].notna().sum()
        if nn>0:
            dmax=f[c].dropna().max()
            mn_p=preset.get("쿠팡해외배송비율_min",0); mx_p=preset.get("쿠팡해외배송비율_max",100)
            mn_c=mn_p/100 if dmax<=1.0 else mn_p; mx_c=mx_p/100 if dmax<=1.0 else mx_p
            f=f[(f[c].isna())|((f[c]>=mn_c)&(f[c]<=mx_c))]
        f=f.sort_values(by=c,ascending=False,na_position="last")
    return f.reset_index(drop=True)

def build_display(f, cm):
    mapping=[("키워드","키워드"),("브랜드","브랜드"),("경쟁률","경쟁률"),
             ("작년검색량","작년검색량"),("작년최대검색월","작년최대검색월"),
             ("피크월검색량","피크월검색량"),("계절성","계절성"),
             ("쿠팡총리뷰수","쿠팡총리뷰"),("쿠팡해외배송비율","쿠팡해외배송비율(%)")]
    cols=[(cm[k],lbl) for k,lbl in mapping if cm.get(k) and cm[k] in f.columns]
    if not cols: return pd.DataFrame()
    r=f[[c for c,_ in cols]].copy(); r.columns=[lbl for _,lbl in cols]
    if "작년최대검색월" in r.columns:
        r["작년최대검색월"]=r["작년최대검색월"].apply(normalize_month)
    if "쿠팡해외배송비율(%)" in r.columns:
        v=pd.to_numeric(r["쿠팡해외배송비율(%)"],errors="coerce")
        r["쿠팡해외배송비율(%)"]=( v*100).round(1) if (not v.dropna().empty and v.dropna().max()<=1.0) else v.round(1)
    return r

LOCALE={
    "page":"페이지","more":"더보기","to":"~","of":"/","next":"다음","last":"마지막",
    "first":"처음","previous":"이전","loadingOoo":"로딩 중...","noRowsToShow":"데이터가 없습니다",
    "filterOoo":"필터...","applyFilter":"필터 적용","equals":"같음","notEqual":"같지 않음",
    "lessThan":"미만","greaterThan":"초과","lessThanOrEqual":"이하","greaterThanOrEqual":"이상",
    "inRange":"범위","contains":"포함","notContains":"미포함","startsWith":"시작","endsWith":"끝",
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

def show_aggrid(df):
    gb=GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(resizable=True,sortable=True,filter=True,
        wrapHeaderText=True,autoHeaderHeight=True,
        cellStyle={"fontSize":"13px","color":"#1f2937"})
    for col,(mn,mx) in {
        "키워드":(160,240),"브랜드":(65,80),"경쟁률":(75,90),
        "작년검색량":(100,120),"작년최대검색월":(110,130),
        "피크월검색량":(105,125),"계절성":(70,85),
        "쿠팡총리뷰":(90,110),"쿠팡해외배송비율(%)":(120,145),
    }.items():
        if col in df.columns:
            gb.configure_column(col,minWidth=mn,maxWidth=mx,
                cellStyle={"fontSize":"13px","color":"#1f2937"})
    gb.configure_column("키워드",pinned="left")
    gb.configure_grid_options(localeText=LOCALE)
    AgGrid(df,gridOptions=gb.build(),update_mode=GridUpdateMode.NO_UPDATE,
           fit_columns_on_grid_load=True,allow_unsafe_jscode=True,
           height=520,theme="streamlit",use_container_width=True)

# ══════════════════════════════════════════════
#  렌더링
# ══════════════════════════════════════════════

# ① 헤더 카드
st.markdown("""
<div class="card card-header">
  <div>
    <p class="title-main">끝장캐리 <em>키워드 분석</em></p>
    <p class="title-sub">쇼핑성 키워드 선별 및 데이터 전략 분석 도구</p>
  </div>
  <div class="badge">Premium Version v1.7</div>
</div>
""", unsafe_allow_html=True)

# ② 업로드 카드
fname = st.session_state.uploaded_name
file_html = f'<div class="file-badge">📎 {fname}</div>' if fname else ""
st.markdown(f"""
<div class="card card-upload" onclick="document.querySelector('[data-testid=stFileUploader] input[type=file]').click()">
  <div class="upload-circle">📄</div>
  <div class="upload-title">분석할 파일을 이곳에 올려주세요</div>
  <div class="upload-sub">엑셀(.xlsx) 또는 CSV 파일을 드래그하거나 클릭하여 선택</div>
  {file_html}
</div>
""", unsafe_allow_html=True)

uploaded = st.file_uploader("업로드", type=["xlsx"], label_visibility="collapsed")
if uploaded:
    fb = uploaded.read()
    df_loaded = load_excel(fb)
    st.session_state.df = df_loaded
    st.session_state.uploaded_name = uploaded.name
    st.rerun()

# ③ 프리셋 바 카드
st.markdown('<div class="card card-preset">', unsafe_allow_html=True)

# 컬럼: 라벨 | 프리셋×5 | 기어 | 여백 | 분석실행 | 다운로드
pc = st.columns([0.85, 1.05, 1.05, 0.9, 0.9, 0.9, 0.42, 0.6, 1.05, 1.1])

with pc[0]:
    st.markdown('<p style="font-size:12px;font-weight:700;color:#9ca3af;margin:7px 0 0;white-space:nowrap;">분석 프리셋</p>',
                unsafe_allow_html=True)

for i in range(5):
    with pc[i+1]:
        is_active = (i == st.session_state.active_preset)
        st.markdown(f'<div class="{"btn-active" if is_active else ""}">', unsafe_allow_html=True)
        if st.button(st.session_state.presets[i]["name"], key=f"pb_{i}", use_container_width=True):
            st.session_state.active_preset = i
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

with pc[6]:
    st.markdown('<div class="btn-gear">', unsafe_allow_html=True)
    if st.button("⚙️", key="gear", use_container_width=True):
        st.session_state.show_modal = not st.session_state.show_modal
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with pc[7]:
    st.empty()

with pc[8]:
    st.markdown('<div class="btn-run">', unsafe_allow_html=True)
    run_clicked = st.button("🔍 분석 실행", key="run", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with pc[9]:
    has_result = st.session_state.result_df is not None and len(st.session_state.result_df) > 0
    if has_result:
        buf = io.BytesIO()
        st.session_state.result_df.to_excel(buf, index=False); buf.seek(0)
        st.download_button("📥 엑셀 다운로드", data=buf,
            file_name=f"키워드분석_{st.session_state.presets[st.session_state.active_preset]['name']}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True)
    else:
        st.markdown('<div class="btn-dl-off">', unsafe_allow_html=True)
        st.button("📥 엑셀 다운로드", key="dl_off", disabled=True, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # card-preset 닫기

# ④ 설정 패널
if st.session_state.show_modal:
    st.markdown('<div class="card card-settings">', unsafe_allow_html=True)
    st.markdown("**⚙️ 프리셋 설정**")
    tabs = st.tabs([p["name"] for p in st.session_state.presets])
    for i, tab in enumerate(tabs):
        with tab:
            p = st.session_state.presets[i]
            p["name"] = st.text_input("프리셋 이름", value=p["name"], key=f"nm_{i}")
            c1,c2 = st.columns(2)
            with c1: p["브랜드"]=st.radio("브랜드키워드",["전체","O","X"],
                index=["전체","O","X"].index(p.get("브랜드","전체")),key=f"br_{i}",horizontal=True)
            with c2: p["시즌성"]=st.radio("시즌성",["전체","있음","없음"],
                index=["전체","있음","없음"].index(p.get("시즌성","전체")),key=f"ss_{i}",horizontal=True)
            st.markdown("**작년검색량 범위**")
            c3,c4=st.columns(2)
            with c3: p["작년검색량_min"]=st.number_input("최소",value=p.get("작년검색량_min",0),step=1000,key=f"ym_{i}")
            with c4: p["작년검색량_max"]=st.number_input("최대",value=p.get("작년검색량_max",9999999),step=1000,key=f"yx_{i}")
            st.markdown("**작년 최대검색월**")
            rows=[["1월","2월","3월","4월"],["5월","6월","7월","8월"],["9월","10월","11월","12월"]]
            sel=p.get("작년최대검색월",[]); nm2=[]
            for row in rows:
                rc=st.columns(4)
                for j,m in enumerate(row):
                    with rc[j]:
                        if st.checkbox(m,value=(m in sel),key=f"mo_{i}_{m}"): nm2.append(m)
            p["작년최대검색월"]=nm2
            st.markdown("**피크월검색량 범위**")
            c5,c6=st.columns(2)
            with c5: p["피크월검색량_min"]=st.number_input("최소",value=p.get("피크월검색량_min",0),step=1000,key=f"pm_{i}")
            with c6: p["피크월검색량_max"]=st.number_input("최대",value=p.get("피크월검색량_max",9999999),step=1000,key=f"px_{i}")
            st.markdown("**쿠팡 총리뷰수 범위**")
            c7,c8=st.columns(2)
            with c7: p["쿠팡총리뷰수_min"]=st.number_input("최소",value=p.get("쿠팡총리뷰수_min",0),step=100,key=f"rm_{i}")
            with c8: p["쿠팡총리뷰수_max"]=st.number_input("최대",value=p.get("쿠팡총리뷰수_max",9999999),step=100,key=f"rx_{i}")
            st.markdown("**쿠팡 해외배송비율 (%)**")
            c9,c10=st.columns(2)
            with c9:  p["쿠팡해외배송비율_min"]=st.number_input("최소(%)",value=p.get("쿠팡해외배송비율_min",0),min_value=0,max_value=100,key=f"om_{i}")
            with c10: p["쿠팡해외배송비율_max"]=st.number_input("최대(%)",value=p.get("쿠팡해외배송비율_max",100),min_value=0,max_value=100,key=f"ox_{i}")
    st.markdown('</div>', unsafe_allow_html=True)

# ⑤ 분석 실행
if run_clicked:
    if st.session_state.df is None:
        st.error("먼저 엑셀 파일을 업로드해 주세요.")
    else:
        cm = get_col_map(st.session_state.df)
        preset = st.session_state.presets[st.session_state.active_preset]
        filtered = apply_preset(st.session_state.df, cm, preset)
        st.session_state.result_df = build_display(filtered, cm)
        st.session_state.filtered_count = len(filtered)

# ⑥ 결과 카드
st.markdown('<div class="card card-result">', unsafe_allow_html=True)
if st.session_state.result_df is not None:
    pname = st.session_state.presets[st.session_state.active_preset]["name"]
    st.markdown(
        f'<div class="result-meta">필터 결과: <b>{st.session_state.filtered_count:,}개</b> 키워드 ({pname})</div>',
        unsafe_allow_html=True)
    if len(st.session_state.result_df) > 0:
        show_aggrid(st.session_state.result_df)
    else:
        st.markdown('<div class="empty-hint">조건에 맞는 키워드가 없습니다. 필터 조건을 완화해 보세요.</div>',
                    unsafe_allow_html=True)
else:
    msg = "📂 파일을 업로드하고 분석 버튼을 눌러주세요." if st.session_state.df is None \
          else "✅ 파일 로드 완료 — 분석 실행 버튼을 눌러주세요."
    st.markdown(f'<div class="empty-hint">{msg}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
