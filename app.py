import streamlit as st
import pandas as pd
import json
import os
import re
import io

# ──────────────────────────────────────────────
# 페이지 설정
# ──────────────────────────────────────────────
st.set_page_config(page_title="초코라떼 키워드서칭프로", page_icon="☕", layout="wide")

# ──────────────────────────────────────────────
# 커스텀 CSS (70% 폭 제한 및 디자인 수정)
# ──────────────────────────────────────────────
st.markdown("""
<style>
/* ── 전역 ── */
#MainMenu, footer {visibility: hidden;}

/* 메인 화면 컨테이너를 가로 70%로 제한하고 중앙 정렬 (최우선 순위) */
[data-testid="stMainBlockContainer"] {
    max-width: 70% !important;
    min-width: 800px !important;
    margin: 0 auto !important;
    padding-top: 2rem !important;
}

/* ── 헤더 카드 ── */
.header-card {
    background: linear-gradient(135deg, #e8eeff 0%, #f4f1ff 100%);
    border-radius: 16px;
    padding: 28px 36px;
    margin-bottom: 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.header-card .title-area h1 {
    margin: 0;
    font-size: 28px;
    font-weight: 800;
    color: #1a1a2e;
}
.header-card .title-area p {
    margin: 4px 0 0 0;
    font-size: 14px;
    color: #6b7280;
}
.header-card .version-badge {
    background: #fff;
    border: 1.5px solid #4f6df5;
    color: #4f6df5;
    font-size: 12px;
    font-weight: 600;
    padding: 6px 14px;
    border-radius: 20px;
    white-space: nowrap;
}

/* ── 파일 업로드 영역 스타일 ── */
div[data-testid="stFileUploader"] {
    border: 2.5px dashed #a5b4fc;
    border-radius: 16px;
    padding: 20px;
    background: #fafaff;
    margin-bottom: 24px;
}

/* ── 파일 로드 완료 배지 ── */
.file-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: #f0fdf4;
    border: 1px solid #86efac;
    color: #166534;
    font-size: 14px;
    font-weight: 500;
    padding: 8px 16px;
    border-radius: 10px;
    margin-bottom: 20px;
}

/* ── 프리셋 버튼 스타일 ── */
div[data-testid="stHorizontalBlock"] button[kind="secondary"] {
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 6px 20px !important;
    border: 1.5px solid #d1d5db !important;
    background: #fff !important;
    color: #374151 !important;
}

/* ── 분석실행 버튼 ── */
div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #4f6df5 0%, #6366f1 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 12px !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    padding: 12px 0 !important;
    box-shadow: 0 4px 14px rgba(79,109,245,0.3) !important;
}

/* ── 결과 섹션 ── */
.result-header {
    font-size: 22px;
    font-weight: 800;
    color: #1a1a2e;
    margin-bottom: 12px;
}
.result-count {
    color: #4f6df5;
}

/* ── 메시지 영역 ── */
.empty-state {
    text-align: center;
    padding: 40px 20px;
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    color: #9ca3af;
    font-size: 15px;
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# 로그인 (비밀번호 인증)
# ──────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    # 컬럼 비율을 조정하여 입력창을 더욱 콤팩트하게 배치 (중앙 컬럼 너비 축소)
    c1, c2, c3 = st.columns([1.5, 1, 1.5]) 
    with c2:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 24px;">
            <h1 style="color: #1a1a2e; font-size: 26px; font-weight: 800;">☕ 키워드서칭프로</h1>
            <p style="color: #6b7280; font-size: 14px; line-height: 1.5;">수강생 전용 프로그램입니다.<br>비밀번호를 입력해주세요.</p>
        </div>
        """, unsafe_allow_html=True)
        
        pwd_input = st.text_input("비밀번호", type="password", placeholder="비밀번호 입력", label_visibility="collapsed")
        st.markdown("<div style='margin-top: -10px;'></div>", unsafe_allow_html=True) # 간격 조정
        if st.button("접속하기", use_container_width=True, type="primary"):
            if pwd_input == "chocolatte2":
                st.session_state["authenticated"] = True
                st.rerun()
            elif pwd_input != "":
                st.error("❌ 비밀번호가 올바르지 않습니다.")
    
    st.stop()


# ──────────────────────────────────────────────
# 프리셋 설정 데이터 (메모리 관리)
# ──────────────────────────────────────────────
PRESET_VERSION = 3
EMPTY_FILTERS = {
    "브랜드키워드": "전체", "쇼핑성키워드": "전체", "계절성": "전체",
    "작년검색량_lo": 0, "작년검색량_hi": 0, "작년최대검색월": [],
    "피크월검색량_lo": 0, "피크월검색량_hi": 0, "쿠팡해외배송비율_lo": 0.0,
    "쿠팡해외배송비율_hi": 0.0, "쿠팡평균가_lo": 0, "쿠팡평균가_hi": 0,
    "쿠팡총리뷰수_lo": 0, "쿠팡총리뷰수_hi": 0,
}

DEFAULT_PRESETS = {
    "version": PRESET_VERSION,
    "presets": [{"name": f"프리셋 {i+1}", "filters": dict(EMPTY_FILTERS)} for i in range(5)],
}

# ──────────────────────────────────────────────
# 유틸리티 함수
# ──────────────────────────────────────────────
def safe_int(v, default=0):
    try: return int(v)
    except: return default

def safe_float(v, default=0.0):
    try: return float(v)
    except: return default

def get_preset_name(idx):
    return st.session_state["presets"]["presets"][idx]["name"]

def get_preset_filters(idx):
    f = st.session_state["presets"]["presets"][idx]["filters"]
    merged = dict(EMPTY_FILTERS)
    merged.update(f)
    return merged

# ──────────────────────────────────────────────
# 엑셀 로딩 로직
# ──────────────────────────────────────────────
def is_header_text(val):
    if val is None or (isinstance(val, float) and pd.isna(val)): return False
    s = str(val).strip()
    if s == "" or s.lower() in ("nan", "none") or re.fullmatch(r"[\d.,\-+%]+", s): return False
    return True

def load_excel(uploaded):
    raw = pd.read_excel(uploaded, header=None)
    n_rows, n_cols = raw.shape
    header_row_count = 1
    for r in range(min(n_rows, 5)):
        row_vals = raw.iloc[r]
        if sum(1 for v in row_vals if is_header_text(v)) >= max(1, n_cols * 0.3):
            header_row_count = r + 1
    col_names = []
    for c in range(n_cols):
        parts = [str(raw.iloc[r, c]).strip() for r in range(header_row_count) if is_header_text(raw.iloc[r, c])]
        col_names.append("_".join(parts) if parts else f"col_{c}")
    df = raw.iloc[header_row_count:].reset_index(drop=True)
    df.columns = col_names
    for col in df.columns:
        converted = pd.to_numeric(df[col], errors="coerce")
        if converted.notna().sum() > len(df) * 0.3: df[col] = converted
    return df

# ──────────────────────────────────────────────
# 컬럼 매핑 및 필터 엔진
# ──────────────────────────────────────────────
COLUMN_PATTERNS = {
    "브랜드키워드": ["브랜드"], "쇼핑성키워드": ["쇼핑성"], "작년검색량": ["작년", "검색량"],
    "작년최대검색월검색량": ["작년", "최대", "검색월", "검색량"], "작년최대검색월": ["작년", "최대", "검색월"],
    "계절성": ["계절"], "쿠팡평균가": ["쿠팡", "평균가"], "쿠팡총리뷰수": ["쿠팡", "총리뷰"],
    "쿠팡최대리뷰수": ["쿠팡", "최대리뷰"], "쿠팡로켓배송비율": ["쿠팡", "로켓배송비율"],
    "쿠팡판매자로켓배송비율": ["쿠팡", "판매자", "로켓"], "쿠팡해외배송비율": ["쿠팡", "해외배송비율"],
    "쿠팡해외배송총리뷰수": ["쿠팡", "해외배송", "총리뷰"],
}

def build_col_map(columns):
    cmap = {"키워드": columns[1] if len(columns) > 1 else columns[0]}
    for c in columns:
        if "키워드" in str(c): cmap["키워드"] = c; break
    used = {cmap["키워드"]}
    for std_key, kws in sorted(COLUMN_PATTERNS.items(), key=lambda x: len(x[1]), reverse=True):
        for c in columns:
            if c not in used and all(kw in str(c).lower() for kw in kws):
                cmap[std_key] = c; used.add(c); break
    return cmap

DISPLAY_COLUMNS = [
    {"key": "키워드"}, {"key": "브랜드키워드", "label": "브랜드", "format": "ox"},
    {"key": "쇼핑성키워드", "label": "쇼핑성", "format": "ox"}, {"key": "작년검색량", "format": "int"},
    {"key": "작년최대검색월"}, {"key": "작년최대검색월검색량", "label": "피크월검색량", "format": "int"},
    {"key": "계절성", "format": "season_ox"}, {"key": "쿠팡평균가", "format": "int"},
    {"key": "쿠팡총리뷰수", "format": "int"}, {"key": "쿠팡로켓배송비율", "format": "pct"},
    {"key": "쿠팡해외배송비율", "format": "pct"},
]

def build_display_df(df, cmap):
    rows = {}
    for spec in DISPLAY_COLUMNS:
        key, label, fmt = spec["key"], spec.get("label", spec["key"]), spec.get("format")
        if key in cmap and cmap[key] in df.columns:
            src = df[cmap[key]]
            if fmt == "ox": rows[label] = ["O" if str(v).upper() in ("O", "TRUE", "1", "Y") else "X" for v in src]
            elif fmt == "int": rows[label] = pd.to_numeric(src, errors="coerce").fillna(0).astype(int)
            elif fmt == "pct": 
                v = pd.to_numeric(src, errors="coerce").fillna(0)
                rows[label] = (v * 100 if v.max() <= 1.0 else v).round(1)
            else: rows[label] = src
    return pd.DataFrame(rows)

def apply_filters(df, filters, cmap):
    out = df.copy()
    for key, val in filters.items():
        if val == "전체" or key not in cmap or cmap[key] not in out.columns: continue
        col = cmap[key]
        if "lo" in key or "hi" in key: continue # 수치 필터는 아래에서 별도 처리
    
    # 수치형 범위 필터 적용
    for k, lo_k, hi_k in [("작년검색량", "작년검색량_lo", "작년검색량_hi"), ("쿠팡평균가", "쿠팡평균가_lo", "쿠팡평균가_hi")]:
        if k in cmap:
            lo, hi = safe_float(filters.get(lo_k)), safe_float(filters.get(hi_k))
            series = pd.to_numeric(out[cmap[k]], errors="coerce")
            if lo > 0: out = out[series >= lo]
            if hi > 0: out = out[series <= hi]
    return out

# ──────────────────────────────────────────────
# 세션 상태 초기화
# ──────────────────────────────────────────────
if "presets" not in st.session_state: st.session_state["presets"] = json.loads(json.dumps(DEFAULT_PRESETS))
if "active_preset" not in st.session_state: st.session_state["active_preset"] = 0
if "df_raw" not in st.session_state: st.session_state["df_raw"] = None
if "df_filtered" not in st.session_state: st.session_state["df_filtered"] = None
if "cmap" not in st.session_state: st.session_state["cmap"] = {}
if "show_settings" not in st.session_state: st.session_state["show_settings"] = False

# ──────────────────────────────────────────────
# 메인 UI
# ──────────────────────────────────────────────
st.markdown("""
<div class="header-card">
    <div class="title-area">
        <h1>☕ 초코라떼 키워드서칭프로</h1>
        <p>수강생 여러분의 효율적인 소싱을 돕는 시장 분석 도구</p>
    </div>
    <div class="version-badge">ver. 2.25</div>
</div>
""", unsafe_allow_html=True)

uploaded = st.file_uploader("📂 분석할 파일을 업로드하세요 (.xlsx, .csv)", type=["xlsx", "xls", "csv"])

if uploaded:
    if st.session_state["df_raw"] is None or st.session_state.get("_fname") != uploaded.name:
        with st.spinner("데이터 로딩 중..."):
            df = pd.read_csv(uploaded) if uploaded.name.endswith(".csv") else load_excel(uploaded)
            st.session_state["df_raw"], st.session_state["cmap"], st.session_state["_fname"] = df, build_col_map(df.columns), uploaded.name
    st.markdown(f'<div class="file-badge">✅ {uploaded.name} 로드 완료 ({len(st.session_state["df_raw"]):,}행)</div>', unsafe_allow_html=True)

# 프리셋 제어 바
num_presets = len(st.session_state["presets"]["presets"])
preset_cols = st.columns([1] * num_presets + [0.4, 1.2])

for i in range(num_presets):
    with preset_cols[i]:
        if st.button(get_preset_name(i), key=f"p_{i}", use_container_width=True, type="primary" if i == st.session_state["active_preset"] else "secondary"):
            st.session_state["active_preset"], st.session_state["show_settings"] = i, False

with preset_cols[num_presets]:
    if st.button("⚙️"): st.session_state["show_settings"] = not st.session_state["show_settings"]

with preset_cols[num_presets + 1]:
    run_clicked = st.button("▶  분석 실행", use_container_width=True, type="primary")

active = st.session_state["active_preset"]

# 설정 화면 (3분할 레이아웃으로 입력창 너비 축소)
if st.session_state["show_settings"]:
    with st.expander(f"⚙️ {get_preset_name(active)} 세부 필터 설정", expanded=True):
        f = get_preset_filters(active)
        new_name = st.text_input("프리셋 이름 수정", value=get_preset_name(active))
        
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1: 
            s_lo = st.number_input("작년검색량 (최소)", value=safe_int(f.get("작년검색량_lo")), step=100)
            a_lo = st.number_input("쿠팡평균가 (최소)", value=safe_int(f.get("쿠팡평균가_lo")), step=1000)
        with c2: 
            s_hi = st.number_input("작년검색량 (최대, 0=무제한)", value=safe_int(f.get("작년검색량_hi")), step=100)
            a_hi = st.number_input("쿠팡평균가 (최대, 0=무제한)", value=safe_int(f.get("쿠팡평균가_hi")), step=1000)
        # c3는 비워두어 입력창 너비가 넓어지지 않게 조절
        
        if st.button("💾 필터 임시 저장"):
            st.session_state["presets"]["presets"][active].update({"name": new_name, "filters": {"작년검색량_lo": s_lo, "작년검색량_hi": s_hi, "쿠팡평균가_lo": a_lo, "쿠팡평균가_hi": a_hi}})
            st.success("설정이 현재 세션에 반영되었습니다.")

if run_clicked and st.session_state["df_raw"] is not None:
    df_f = apply_filters(st.session_state["df_raw"], get_preset_filters(active), st.session_state["cmap"])
    st.session_state["df_filtered"] = df_f

if st.session_state["df_filtered"] is not None:
    display_df = build_display_df(st.session_state["df_filtered"], st.session_state["cmap"])
    st.markdown(f'<div class="result-header">📊 분석 결과 (<span class="result-count">{len(display_df):,}건</span>)</div>', unsafe_allow_html=True)
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    buf = io.BytesIO()
    display_df.to_excel(buf, index=False)
    st.download_button("📥 결과 엑셀 다운로드", buf.getvalue(), file_name="분석결과.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
