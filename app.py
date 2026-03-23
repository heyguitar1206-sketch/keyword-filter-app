import streamlit as st
import pandas as pd
import io
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.set_page_config(page_title="끝장캐리 키워드 분석", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700&display=swap');

* { font-family: 'Noto Sans KR', sans-serif !important; box-sizing: border-box; }

[data-testid="stHeader"]     { display: none !important; }
[data-testid="stToolbar"]    { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
footer                       { display: none !important; }

.stApp, body {
    background-color: #e8ecf4 !important;
}

.block-container {
    max-width: 72% !important;
    margin: 0 auto !important;
    padding: 32px 0 60px 0 !important;
}

/* ── 헤더 카드 ── */
.header-card {
    background: #ffffff !important;
    border-radius: 16px !important;
    padding: 22px 32px !important;
    margin-bottom: 18px !important;
    box-shadow: 0 2px 12px rgba(60,80,180,0.07) !important;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.header-title { font-size: 20px; font-weight: 700; color: #1a1a2e; }
.header-title span { color: #3b5bff; }
.header-sub { font-size: 13px; color: #888; margin-top: 4px; }
.version-badge {
    background: #f0f3ff;
    color: #3b5bff;
    border: 1px solid #c7d0ff;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 12px;
    font-weight: 600;
}

/* ── 업로드 영역 ── */
[data-testid="stFileUploader"] {
    background: #ffffff !important;
    border-radius: 16px !important;
    padding: 8px 16px !important;
    box-shadow: 0 2px 12px rgba(60,80,180,0.07) !important;
}
[data-testid="stFileUploader"] > label { display: none !important; }
[data-testid="stFileUploaderDropzone"] {
    background: #ffffff !important;
    border: none !important;
    padding: 12px 8px !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] > div > span {
    font-size: 14px !important;
    font-weight: 600 !important;
    color: #1a1a2e !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] > div > small {
    font-size: 12px !important;
    color: #888 !important;
}
/* Browse files 버튼 스타일 */
[data-testid="stFileUploaderDropzone"] button {
    background: #3b5bff !important;
    color: white !important;
    border: none !important;
    border-radius: 22px !important;
    padding: 10px 28px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    cursor: pointer !important;
    transition: background 0.18s !important;
}
[data-testid="stFileUploaderDropzone"] button:hover {
    background: #2a47e0 !important;
}

/* ── 프리셋 카드 ── */
.preset-card {
    background: #ffffff !important;
    border-radius: 16px !important;
    padding: 20px 28px !important;
    margin-bottom: 18px !important;
    box-shadow: 0 2px 12px rgba(60,80,180,0.07) !important;
}
.preset-label {
    font-size: 13px;
    font-weight: 600;
    color: #888;
    margin-bottom: 12px;
    letter-spacing: 0.05em;
}

/* ── 프리셋 버튼: Browse files와 동일한 스타일 ── */
div[data-testid="column"] .stButton button {
    background: #3b5bff !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 22px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    padding: 10px 20px !important;
    width: 100% !important;
    white-space: nowrap !important;
    transition: background 0.18s !important;
    cursor: pointer !important;
}
div[data-testid="column"] .stButton button:hover {
    background: #2a47e0 !important;
    color: #ffffff !important;
}

/* 활성 프리셋: 더 진한 인디고 + 테두리 강조 */
.active-preset-btn div[data-testid="column"] .stButton button,
.active-preset-btn .stButton button {
    background: #1a3bcc !important;
    color: #ffffff !important;
    border: 2.5px solid #0d2299 !important;
    box-shadow: 0 2px 10px rgba(59,91,255,0.30) !important;
}

/* 설정 버튼 */
.btn-settings .stButton button {
    background: #f0f3ff !important;
    color: #3b5bff !important;
    border: 1.5px solid #c7d0ff !important;
    border-radius: 22px !important;
    font-size: 18px !important;
    padding: 8px 16px !important;
    width: 100% !important;
}
.btn-settings .stButton button:hover {
    background: #e0e7ff !important;
}

/* 분석 실행 버튼 */
.btn-run .stButton button {
    background: #3b5bff !important;
    color: white !important;
    border: none !important;
    border-radius: 22px !important;
    font-size: 14px !important;
    font-weight: 700 !important;
    padding: 10px 20px !important;
    width: 100% !important;
}
.btn-run .stButton button:hover {
    background: #2a47e0 !important;
}

/* 다운로드 버튼 */
.btn-download .stDownloadButton button,
.btn-download .stButton button {
    background: #f0f3ff !important;
    color: #3b5bff !important;
    border: 1.5px solid #c7d0ff !important;
    border-radius: 22px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    padding: 10px 16px !important;
    width: 100% !important;
}
.btn-download .stDownloadButton button:hover {
    background: #e0e7ff !important;
}

/* ── 결과 카드 ── */
.result-card {
    background: #ffffff !important;
    border-radius: 16px !important;
    padding: 24px 32px !important;
    margin-bottom: 18px !important;
    box-shadow: 0 2px 12px rgba(60,80,180,0.07) !important;
}
.result-count {
    font-size: 15px;
    font-weight: 600;
    color: #1a1a2e;
    margin-bottom: 16px;
}
.result-count span { color: #3b5bff; }

/* ── AgGrid ── */
.ag-theme-streamlit {
    border-radius: 10px !important;
    overflow: hidden !important;
    font-family: 'Noto Sans KR', sans-serif !important;
}
.ag-theme-streamlit .ag-header {
    background: #f0f3ff !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    color: #3b5bff !important;
}
.ag-theme-streamlit .ag-row-even { background: #fafbff !important; }
.ag-theme-streamlit .ag-row-odd  { background: #ffffff !important; }
.ag-theme-streamlit .ag-row:hover { background: #e8f0fe !important; }
.ag-theme-streamlit .ag-cell {
    font-size: 13px !important;
    color: #333 !important;
    display: flex !important;
    align-items: center !important;
}
</style>
""", unsafe_allow_html=True)

# ── 기본값 ──────────────────────────────────────────────────────────────────
DEFAULT_PRESET = {
    "이름": "프리셋",
    "브랜드키워드": "전체",
    "시즌성": "전체",
    "작년검색량_min": 0,
    "작년검색량_max": 9999999,
    "피크월검색량_min": 0,
    "피크월검색량_max": 9999999,
    "작년최대검색월": [],
    "쿠팡리뷰수_min": 0,
    "쿠팡리뷰수_max": 9999999,
    "쿠팡해외배송비율_min": 0.0,
    "쿠팡해외배송비율_max": 100.0,
}

def make_preset(name, **kwargs):
    p = DEFAULT_PRESET.copy()
    p["이름"] = name
    p.update(kwargs)
    return p

if "presets" not in st.session_state:
    st.session_state.presets = [
        make_preset("1"),
        make_preset("2"),
        make_preset("3"),
        make_preset("4"),
        make_preset("5"),
    ]
if "active_preset"  not in st.session_state: st.session_state.active_preset  = 0
if "show_settings"  not in st.session_state: st.session_state.show_settings  = False
if "df"             not in st.session_state: st.session_state.df             = None
if "result_df"      not in st.session_state: st.session_state.result_df      = None
if "filtered_count" not in st.session_state: st.session_state.filtered_count = 0
if "file_name"      not in st.session_state: st.session_state.file_name      = None

# ── 유틸 함수 ────────────────────────────────────────────────────────────────
@st.cache_data
def load_excel(file_bytes: bytes):
    try:
        raw = pd.read_excel(io.BytesIO(file_bytes), sheet_name="all", header=[0, 1, 2])
    except Exception:
        raw = pd.read_excel(io.BytesIO(file_bytes), header=0)
    cols = []
    for col in raw.columns:
        if isinstance(col, tuple):
            parts = [str(c).strip() for c in col if str(c).strip() not in ("nan", "")]
            cols.append("_".join(dict.fromkeys(parts)))
        else:
            cols.append(str(col).strip())
    raw.columns = cols
    return raw.reset_index(drop=True)

def find_col(df, keywords):
    kws = [k.lower() for k in keywords]
    for col in df.columns:
        if all(k in col.lower() for k in kws):
            return col
    return None

def find_col_any(df, keyword_sets):
    for kws in keyword_sets:
        r = find_col(df, kws)
        if r:
            return r
    return None

def get_col_map(df):
    return {
        "키워드":           find_col(df, ["키워드"]),
        "브랜드키워드":     find_col_any(df, [["브랜드","키워드"], ["brand"]]),
        "쇼핑성키워드":     find_col_any(df, [["쇼핑성"], ["shopping"]]),
        "경쟁강도":         find_col_any(df, [["경쟁강도"], ["경쟁"]]),
        "계절성":           find_col_any(df, [["계절성"], ["시즌"], ["season"]]),
        "작년검색량":       find_col_any(df, [["작년","검색량"], ["검색량_합"], ["총검색량"]]),
        "작년최대검색월":   find_col_any(df, [["작년","최대","검색월"], ["최대검색월"], ["피크","월"]]),
        "피크월검색량":     find_col_any(df, [
            ["피크월","검색량"], ["최대검색월","검색량"],
            ["작년최대검색월","검색량"], ["피크","검색량"], ["최대월","검색량"],
        ]),
        "쿠팡리뷰수":       find_col_any(df, [["쿠팡","리뷰"], ["리뷰수"]]),
        "쿠팡해외배송비율": find_col_any(df, [["해외","배송","비율"], ["해외배송"], ["overseas"]]),
    }

def normalize_month(val):
    import re
    if val is None: return val
    m = re.search(r"(\d+)", str(val).strip())
    return f"{m.group(1)}월" if m else str(val).strip()

def apply_preset(df, preset, col_map):
    fdf = df.copy()

    # 쇼핑성 항상 O
    if col_map.get("쇼핑성키워드"):
        col = col_map["쇼핑성키워드"]
        fdf = fdf[fdf[col].astype(str).str.strip().isin(["O","o","Y","y","1","True","true","쇼핑성"])]

    # 브랜드키워드
    if col_map.get("브랜드키워드") and preset.get("브랜드키워드","전체") != "전체":
        col = col_map["브랜드키워드"]
        vals = fdf[col].astype(str).str.strip()
        if preset["브랜드키워드"] == "O":
            fdf = fdf[vals.isin(["O","o","Y","y","1","True","true"])]
        else:
            fdf = fdf[vals.isin(["X","x","N","n","0","False","false"])]

    # 시즌성
    if col_map.get("계절성") and preset.get("시즌성","전체") != "전체":
        col = col_map["계절성"]
        vals = fdf[col].astype(str).str.strip()
        if preset["시즌성"] == "있음":
            fdf = fdf[vals.isin(["O","o","있음","Y","y","1","True","true"])]
        else:
            fdf = fdf[vals.isin(["X","x","없음","N","n","0","False","false"])]

    # 작년검색량
    if col_map.get("작년검색량"):
        s = pd.to_numeric(fdf[col_map["작년검색량"]], errors="coerce")
        fdf = fdf[s.between(preset.get("작년검색량_min",0), preset.get("작년검색량_max",9999999)) | s.isna()]

    # 피크월검색량
    if col_map.get("피크월검색량"):
        s = pd.to_numeric(fdf[col_map["피크월검색량"]], errors="coerce")
        fdf = fdf[s.between(preset.get("피크월검색량_min",0), preset.get("피크월검색량_max",9999999)) | s.isna()]

    # 작년최대검색월
    if col_map.get("작년최대검색월") and preset.get("작년최대검색월"):
        selected = [f"{m}월" for m in preset["작년최대검색월"]]
        normalized = fdf[col_map["작년최대검색월"]].apply(normalize_month)
        fdf = fdf[normalized.isin(selected)]

    # 쿠팡리뷰수
    if col_map.get("쿠팡리뷰수"):
        s = pd.to_numeric(fdf[col_map["쿠팡리뷰수"]], errors="coerce")
        fdf = fdf[s.between(preset.get("쿠팡리뷰수_min",0), preset.get("쿠팡리뷰수_max",9999999)) | s.isna()]

    # 쿠팡해외배송비율
    if col_map.get("쿠팡해외배송비율"):
        s = pd.to_numeric(fdf[col_map["쿠팡해외배송비율"]], errors="coerce")
        mx_val = s.max(skipna=True)
        mn_p, mx_p = preset.get("쿠팡해외배송비율_min",0.0), preset.get("쿠팡해외배송비율_max",100.0)
        if mx_val is not None and mx_val <= 1.0:
            fdf = fdf[s.between(mn_p/100, mx_p/100) | s.isna()]
        else:
            fdf = fdf[s.between(mn_p, mx_p) | s.isna()]

    return fdf.reset_index(drop=True)

def build_display(df, col_map):
    cols_order = [
        ("키워드","키워드"), ("브랜드키워드","브랜드"), ("계절성","시즌성"),
        ("작년검색량","작년검색량"), ("작년최대검색월","최대검색월"),
        ("피크월검색량","피크월검색량"), ("쿠팡리뷰수","쿠팡리뷰수"),
        ("쿠팡해외배송비율","해외배송비율(%)"),
    ]
    records, rename = {}, {}
    for key, label in cols_order:
        orig = col_map.get(key)
        if orig and orig in df.columns:
            records[orig] = df[orig]
            rename[orig] = label
    out = pd.DataFrame(records).rename(columns=rename)
    if "최대검색월" in out.columns:
        out["최대검색월"] = out["최대검색월"].apply(normalize_month)
    if "해외배송비율(%)" in out.columns:
        s = pd.to_numeric(out["해외배송비율(%)"], errors="coerce")
        if s.max(skipna=True) is not None and s.max(skipna=True) <= 1.0:
            out["해외배송비율(%)"] = (s * 100).round(1).astype(str) + "%"
        else:
            out["해외배송비율(%)"] = s.round(1).astype(str) + "%"
    return out

def show_aggrid(df):
    locale_text = {
        "page":"페이지","more":"더보기","to":"~","of":"/","next":"다음",
        "last":"마지막","first":"처음","previous":"이전","loadingOoo":"로딩 중...",
        "noRowsToShow":"데이터가 없습니다.","filterOoo":"필터...","applyFilter":"적용",
        "equals":"같음","notEqual":"같지않음","lessThan":"미만","greaterThan":"초과",
        "contains":"포함","notContains":"미포함","startsWith":"시작","endsWith":"끝남",
        "andCondition":"AND","orCondition":"OR",
    }
    col_widths = {
        "키워드":180,"브랜드":80,"시즌성":80,"작년검색량":110,
        "최대검색월":100,"피크월검색량":120,"쿠팡리뷰수":100,"해외배송비율(%)":120,
    }
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(resizable=True, sortable=True, filter=True, min_width=80)
    for col, w in col_widths.items():
        if col in df.columns:
            gb.configure_column(col, width=w)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=20)
    gb.configure_grid_options(localeText=locale_text, domLayout="normal")
    AgGrid(df, gridOptions=gb.build(), update_mode=GridUpdateMode.NO_UPDATE,
           theme="streamlit", height=480, allow_unsafe_jscode=True,
           fit_columns_on_grid_load=False)

# ═══════════════════════════════ UI ══════════════════════════════════════════

# 1. 헤더 카드
st.markdown("""
<div class="header-card">
  <div>
    <div class="header-title">끝장캐리 <span>키워드 분석</span></div>
    <div class="header-sub">쇼핑성 키워드 선별 및 데이터 전략 분석 도구</div>
  </div>
  <div class="version-badge">Premium Version v1.7</div>
</div>
""", unsafe_allow_html=True)

# 2. 업로드
uploaded = st.file_uploader("파일 업로드", type=["xlsx"], label_visibility="collapsed")

if uploaded:
    file_bytes = uploaded.read()
    if st.session_state.file_name != uploaded.name:
        st.session_state.file_name = uploaded.name
        st.session_state.df = load_excel(file_bytes)
        st.session_state.result_df = None
        cm = get_col_map(st.session_state.df)
        if cm.get("피크월검색량"):
            st.success(f"✅ 파일 로드 완료 — 총 {len(st.session_state.df):,}개 키워드 | 피크월검색량: `{cm['피크월검색량']}`")
        else:
            st.warning(f"⚠️ 파일 로드 완료 — 총 {len(st.session_state.df):,}개 키워드 | 피크월검색량 컬럼을 찾지 못했습니다.")

# 3. 프리셋 카드
st.markdown('<div class="preset-card">', unsafe_allow_html=True)
st.markdown('<div class="preset-label">분석 프리셋</div>', unsafe_allow_html=True)

presets = st.session_state.presets
n = len(presets)
# 프리셋5개 + 설정⚙️ + 분석실행 + 다운로드
cols = st.columns([1.4]*n + [0.6, 1.6, 1.6])

for i, p in enumerate(presets):
    with cols[i]:
        is_active = (i == st.session_state.active_preset)
        # 활성 버튼에 CSS 클래스 적용
        if is_active:
            st.markdown('<div class="active-preset-btn">', unsafe_allow_html=True)
        if st.button(p["이름"], key=f"preset_btn_{i}"):
            st.session_state.active_preset = i
            st.rerun()
        if is_active:
            st.markdown('</div>', unsafe_allow_html=True)

with cols[n]:
    st.markdown('<div class="btn-settings">', unsafe_allow_html=True)
    if st.button("⚙️", key="btn_settings"):
        st.session_state.show_settings = not st.session_state.show_settings
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with cols[n+1]:
    st.markdown('<div class="btn-run">', unsafe_allow_html=True)
    run_clicked = st.button("🔍 분석 실행", key="btn_run")
    st.markdown('</div>', unsafe_allow_html=True)

with cols[n+2]:
    st.markdown('<div class="btn-download">', unsafe_allow_html=True)
    if st.session_state.result_df is not None and len(st.session_state.result_df) > 0:
        disp = build_display(st.session_state.result_df, get_col_map(st.session_state.df))
        buf = io.BytesIO()
        disp.to_excel(buf, index=False, engine="openpyxl")
        st.download_button("📥 엑셀 다운로드", data=buf.getvalue(),
                           file_name="filtered_keywords.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                           key="btn_dl")
    else:
        st.button("📥 엑셀 다운로드", disabled=True, key="btn_dl_dis")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # preset-card 닫기

# 4. 설정 패널
if st.session_state.show_settings:
    with st.expander("⚙️ 프리셋 설정", expanded=True):
        tabs = st.tabs([p["이름"] for p in presets])
        for i, tab in enumerate(tabs):
            with tab:
                p = st.session_state.presets[i]
                p["이름"] = st.text_input("프리셋 이름", p["이름"], key=f"name_{i}")
                c1, c2 = st.columns(2)
                with c1:
                    p["브랜드키워드"] = st.radio("브랜드키워드", ["전체","O","X"],
                        index=["전체","O","X"].index(p.get("브랜드키워드","전체")), key=f"brand_{i}")
                with c2:
                    p["시즌성"] = st.radio("시즌성", ["전체","있음","없음"],
                        index=["전체","있음","없음"].index(p.get("시즌성","전체")), key=f"season_{i}")
                c3, c4 = st.columns(2)
                with c3:
                    p["작년검색량_min"] = st.number_input("작년검색량 최소", value=int(p.get("작년검색량_min",0)), min_value=0, key=f"ys_min_{i}")
                with c4:
                    p["작년검색량_max"] = st.number_input("작년검색량 최대", value=int(p.get("작년검색량_max",9999999)), min_value=0, key=f"ys_max_{i}")
                c5, c6 = st.columns(2)
                with c5:
                    p["피크월검색량_min"] = st.number_input("피크월검색량 최소", value=int(p.get("피크월검색량_min",0)), min_value=0, key=f"pk_min_{i}")
                with c6:
                    p["피크월검색량_max"] = st.number_input("피크월검색량 최대", value=int(p.get("피크월검색량_max",9999999)), min_value=0, key=f"pk_max_{i}")
                all_months = list(range(1,13))
                p["작년최대검색월"] = st.multiselect("작년최대검색월 (다중선택)",
                    options=all_months, format_func=lambda x: f"{x}월",
                    default=p.get("작년최대검색월",[]), key=f"month_{i}")
                c7, c8 = st.columns(2)
                with c7:
                    p["쿠팡리뷰수_min"] = st.number_input("쿠팡리뷰수 최소", value=int(p.get("쿠팡리뷰수_min",0)), min_value=0, key=f"rv_min_{i}")
                with c8:
                    p["쿠팡리뷰수_max"] = st.number_input("쿠팡리뷰수 최대", value=int(p.get("쿠팡리뷰수_max",9999999)), min_value=0, key=f"rv_max_{i}")
                c9, c10 = st.columns(2)
                with c9:
                    p["쿠팡해외배송비율_min"] = st.number_input("해외배송비율 최소(%)", value=float(p.get("쿠팡해외배송비율_min",0.0)), min_value=0.0, max_value=100.0, key=f"os_min_{i}")
                with c10:
                    p["쿠팡해외배송비율_max"] = st.number_input("해외배송비율 최대(%)", value=float(p.get("쿠팡해외배송비율_max",100.0)), min_value=0.0, max_value=100.0, key=f"os_max_{i}")
                st.session_state.presets[i] = p

# 5. 분석 실행
if run_clicked:
    if st.session_state.df is None:
        st.error("❌ 파일을 먼저 업로드해주세요.")
    else:
        col_map = get_col_map(st.session_state.df)
        preset  = st.session_state.presets[st.session_state.active_preset]
        result  = apply_preset(st.session_state.df, preset, col_map)
        st.session_state.result_df      = result
        st.session_state.filtered_count = len(result)
        st.rerun()

# 6. 결과 카드
st.markdown('<div class="result-card">', unsafe_allow_html=True)
if st.session_state.result_df is not None:
    cnt = st.session_state.filtered_count
    st.markdown(f'<div class="result-count">필터링 결과: <span>{cnt:,}개</span> 키워드</div>',
                unsafe_allow_html=True)
    if cnt > 0:
        show_aggrid(build_display(st.session_state.result_df, get_col_map(st.session_state.df)))
    else:
        st.warning("⚠️ 조건에 맞는 키워드가 없습니다. 필터 조건을 완화해보세요.")
else:
    st.markdown(
        '<div style="text-align:center;color:#aaa;padding:32px 0;">'
        '📂 파일을 업로드하고 분석 실행 버튼을 눌러주세요.</div>',
        unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
