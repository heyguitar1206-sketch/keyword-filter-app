import streamlit as st
import pandas as pd
import json
import io
import os

# ─────────────────────────────────────────────
# 페이지 설정
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="끝장캐리 키워드 분석",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    .header-row {
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        margin-bottom: 0.3rem;
    }
    .app-title {
        font-size: 1.8rem;
        font-weight: 800;
        color: #1a1a2e;
        line-height: 1.2;
    }
    .app-title span { color: #4361ee; }
    .app-subtitle {
        font-size: 0.85rem;
        color: #888;
    }
    .version-badge {
        background: white;
        border: 1.5px solid #4361ee;
        color: #4361ee;
        padding: 0.3rem 0.9rem;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
        white-space: nowrap;
    }
    .preset-label {
        font-size: 0.82rem;
        color: #999;
        font-weight: 500;
        padding-top: 0.45rem;
    }
    .result-box {
        background: #f8f9ff;
        border: 1.5px solid #e0e4ff;
        border-radius: 14px;
        padding: 2rem;
        text-align: center;
        min-height: 160px;
    }
    .result-box p { color: #aaa; }
    .filter-section-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #333;
        margin-bottom: 0.6rem;
        padding-bottom: 0.3rem;
        border-bottom: 2px solid #4361ee;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 프리셋 기본값 & 유틸
# ─────────────────────────────────────────────
PRESET_FILE = "presets.json"

EMPTY_FILTERS = {
    "브랜드_키워드": "전체",
    "쇼핑성_키워드": "전체",
    "작년_검색량_min": None,
    "작년_검색량_max": None,
    "작년최대검색월": [],
    "피크월검색량_min": None,
    "피크월검색량_max": None,
    "계절성": "전체",
    "쿠팡_해외배송비율_min": None,
    "쿠팡_해외배송비율_max": None,
    "쿠팡_평균가_min": None,
    "쿠팡_평균가_max": None,
    "쿠팡_총리뷰수_min": None,
    "쿠팡_총리뷰수_max": None,
}

DEFAULT_PRESETS = {
    "프리셋 1": {"name": "시즌소싱 26년 봄", "filters": EMPTY_FILTERS.copy()},
    "프리셋 2": {"name": "비시즌 가구", "filters": EMPTY_FILTERS.copy()},
    "프리셋 3": {"name": "프리셋 3", "filters": EMPTY_FILTERS.copy()},
    "프리셋 4": {"name": "프리셋 4", "filters": EMPTY_FILTERS.copy()},
    "프리셋 5": {"name": "프리셋 5", "filters": EMPTY_FILTERS.copy()},
}

def load_presets():
    if os.path.exists(PRESET_FILE):
        try:
            with open(PRESET_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 기존 프리셋에 빠진 필터 키 보충
                for k, v in data.items():
                    for fk, fv in EMPTY_FILTERS.items():
                        if fk not in v.get("filters", {}):
                            v.setdefault("filters", {})[fk] = fv
                return data
        except Exception:
            return DEFAULT_PRESETS.copy()
    return DEFAULT_PRESETS.copy()

def save_presets(presets):
    with open(PRESET_FILE, 'w', encoding='utf-8') as f:
        json.dump(presets, f, ensure_ascii=False, indent=2)

# ─────────────────────────────────────────────
# 엑셀 로딩
# ─────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_excel(file_bytes, file_name):
    """엑셀 파일 로드 – 3행 헤더 병합"""
    df = pd.read_excel(io.BytesIO(file_bytes), sheet_name="all", header=None)

    row0 = df.iloc[0].fillna('').astype(str)
    row1 = df.iloc[1].fillna('').astype(str)
    row2 = df.iloc[2].fillna('').astype(str)

    merged = []
    for i in range(len(row0)):
        parts = []
        for r in [row0[i], row1[i], row2[i]]:
            s = r.strip()
            if s and s not in parts:
                parts.append(s)
        merged.append('_'.join(parts) if parts else f'col_{i}')
    df.columns = merged
    df = df.iloc[3:].reset_index(drop=True)

    # 중복 컬럼명
    seen = {}
    new_cols = []
    for c in df.columns:
        if c in seen:
            seen[c] += 1
            new_cols.append(f"{c}_{seen[c]}")
        else:
            seen[c] = 0
            new_cols.append(c)
    df.columns = new_cols

    for c in df.columns:
        try:
            df[c] = pd.to_numeric(df[c], errors='ignore')
        except Exception:
            pass
    return df

# ─────────────────────────────────────────────
# 컬럼 자동 매핑
# ─────────────────────────────────────────────
def build_col_map(df):
    cols = df.columns.tolist()
    mapping = {}

    rules = {
        '신규진입':          ['신규진입_키워드', '신규진입'],
        '키워드':            ['키워드'],
        '카테고리':          ['카테고리'],
        '브랜드':            ['브랜드_키워드', '브랜드'],
        '쇼핑성':            ['쇼핑성_키워드', '쇼핑성'],
        '경쟁률':            ['경쟁률'],
        '최근1개월검색량':   ['최근_1개월_검색량', '최근_검색량'],
        '예상1개월검색량':   ['예상_1개월_검색량', '예상_검색량'],
        '예상1개월상승률':   ['예상1개월_검색량_상승률'],
        '최근3개월검색량':   ['최근_3개월_검색량'],
        '예상3개월검색량':   ['예상_3개월_검색량'],
        '작년검색량':        ['작년_검색량'],
        '작년최대검색월':    ['작년_최대검색_월', '작년_최대검색'],
        '작년최대검색량':    ['작년최대_검색량'],
        '계절성':            ['계절성'],
        '계절성월':          ['계절성_월'],
        '네이버상품수':      ['네이버_상품수'],
        '네이버해외상품수':  ['네이버_해외_상품수'],
        '네이버평균가':      ['네이버_평균가'],
        '경쟁강도':          ['네이버_경쟁강도', '경쟁강도'],
        '네이버일반배송':    ['네이버_일반배송비율'],
        '네이버해외배송':    ['네이버_해외배송비율'],
        '네이버묶음상품':    ['네이버_묶음상품비율'],
        '쿠팡평균가':        ['쿠팡_평균가'],
        '쿠팡총리뷰수':      ['쿠팡_총리뷰수'],
        '쿠팡최대리뷰수':    ['쿠팡_최대리뷰수'],
        '쿠팡평균리뷰수':    ['쿠팡_평균리뷰수'],
        '쿠팡로켓배송':      ['쿠팡_로켓배송비율'],
        '쿠팡판매자로켓':    ['쿠팡_판매자로켓_배송비율', '쿠팡_판매자로켓'],
        '쿠팡일반배송':      ['쿠팡_일반배송비율'],
        '쿠팡해외배송비율':  ['쿠팡_해외배송비율'],
        '쿠팡해외총리뷰':    ['쿠팡_해외배송_총리뷰수', '해외배송_총리뷰수'],
        '쿠팡해외최대리뷰':  ['쿠팡_해외배송_최대리뷰수', '해외배송_최대리뷰수'],
        '쿠팡해외평균리뷰':  ['쿠팡_해외배송_평균리뷰수', '해외배송_평균리뷰수'],
    }

    for std, patterns in rules.items():
        for col in cols:
            clean = col.replace(' ', '')
            for pat in patterns:
                if pat.replace(' ', '') in clean:
                    mapping[std] = col
                    break
            if std in mapping:
                break
    return mapping

# ─────────────────────────────────────────────
# 필터 적용
# ─────────────────────────────────────────────
def apply_filters(df, filters, cmap):
    if not filters:
        return df
    out = df.copy()

    # --- O/X 선택 필터 ---
    def ox_filter(filter_key, map_key):
        nonlocal out
        val = filters.get(filter_key)
        if val and val != "전체" and map_key in cmap:
            out = out[out[cmap[map_key]].astype(str).str.strip() == val]

    ox_filter('브랜드_키워드', '브랜드')
    ox_filter('쇼핑성_키워드', '쇼핑성')

    # 계절성
    val = filters.get('계절성')
    if val and val != "전체" and '계절성' in cmap:
        if val == "O":
            out = out[out[cmap['계절성']].astype(str).str.strip() == '있음']
        elif val == "X":
            out = out[out[cmap['계절성']].astype(str).str.strip() == '없음']

    # --- 숫자 범위 필터 ---
    def range_filter(fmin_key, fmax_key, map_key):
        nonlocal out
        if map_key not in cmap:
            return
        col = cmap[map_key]
        s = pd.to_numeric(out[col], errors='coerce')
        v_min = filters.get(fmin_key)
        v_max = filters.get(fmax_key)
        if v_min is not None and v_min != '' and v_min != 0:
            try:
                out = out[s >= float(v_min)]
            except Exception:
                pass
        if v_max is not None and v_max != '' and v_max != 0:
            try:
                out = out[s <= float(v_max)]
            except Exception:
                pass

    range_filter('작년_검색량_min', '작년_검색량_max', '작년검색량')
    range_filter('피크월검색량_min', '피크월검색량_max', '작년최대검색량')
    range_filter('쿠팡_해외배송비율_min', '쿠팡_해외배송비율_max', '쿠팡해외배송비율')
    range_filter('쿠팡_평균가_min', '쿠팡_평균가_max', '쿠팡평균가')
    range_filter('쿠팡_총리뷰수_min', '쿠팡_총리뷰수_max', '쿠팡총리뷰수')

    # --- 작년최대검색월 (복수 선택) ---
    months = filters.get('작년최대검색월', [])
    if months and '작년최대검색월' in cmap:
        col = cmap['작년최대검색월']
        s = pd.to_numeric(out[col], errors='coerce')
        month_ints = [int(m) for m in months]
        out = out[s.isin(month_ints)]

    # --- 기본 정렬: 쿠팡 해외배송비율 내림차순 ---
    if '쿠팡해외배송비율' in cmap:
        sort_col = cmap['쿠팡해외배송비율']
        out[sort_col] = pd.to_numeric(out[sort_col], errors='coerce')
        out = out.sort_values(sort_col, ascending=False, na_position='last')

    return out.reset_index(drop=True)

# ─────────────────────────────────────────────
# 컬럼 표시명 변환 (피크월검색량)
# ─────────────────────────────────────────────
def rename_display_cols(df, cmap):
    """결과 출력 시 컬럼 이름 치환"""
    renames = {}
    if '작년최대검색량' in cmap:
        renames[cmap['작년최대검색량']] = '피크월검색량'
    if renames:
        return df.rename(columns=renames)
    return df

# ─────────────────────────────────────────────
# 세션 초기화
# ─────────────────────────────────────────────
if 'presets' not in st.session_state:
    st.session_state.presets = load_presets()
if 'active_preset' not in st.session_state:
    st.session_state.active_preset = '프리셋 1'
if 'df' not in st.session_state:
    st.session_state.df = None
if 'filtered_df' not in st.session_state:
    st.session_state.filtered_df = None
if 'col_map' not in st.session_state:
    st.session_state.col_map = {}
if 'show_settings' not in st.session_state:
    st.session_state.show_settings = False
if 'fullscreen' not in st.session_state:
    st.session_state.fullscreen = False

# ─────────────────────────────────────────────
# 헤더
# ─────────────────────────────────────────────
h1, h2 = st.columns([5, 1])
with h1:
    st.markdown(
        '<div class="app-title">끝장캐리 <span>키워드 분석</span></div>'
        '<div class="app-subtitle">쇼핑성 키워드 선별 및 데이터 전략 분석 도구</div>',
        unsafe_allow_html=True,
    )
with h2:
    st.markdown(
        '<div style="text-align:right;padding-top:0.6rem;">'
        '<span class="version-badge">Premium Version v2.0</span></div>',
        unsafe_allow_html=True,
    )

st.markdown("---")

# ─────────────────────────────────────────────
# 파일 업로드
# ─────────────────────────────────────────────
uploaded = st.file_uploader(
    "분석할 파일을 이곳에 올려주세요",
    type=['xlsx', 'csv'],
    help="엑셀(.xlsx) 또는 CSV 파일 (최대 500 MB)",
)

if uploaded and st.session_state.df is None:
    with st.spinner("📊 데이터 로딩 중… 대용량 파일은 1~2분 걸릴 수 있습니다."):
        try:
            raw = uploaded.read()
            if uploaded.name.endswith('.csv'):
                st.session_state.df = pd.read_csv(io.BytesIO(raw))
            else:
                st.session_state.df = load_excel(raw, uploaded.name)
            st.session_state.col_map = build_col_map(st.session_state.df)
            st.success(
                f"✅ 로드 완료! — **{len(st.session_state.df):,}**개 행 · "
                f"**{len(st.session_state.df.columns)}**개 컬럼"
            )
        except Exception as e:
            st.error(f"❌ 파일 로드 실패: {e}")

if st.session_state.df is not None:
    if st.button("🗑️ 파일 초기화"):
        for k in ['df', 'filtered_df', 'col_map']:
            st.session_state[k] = None if k != 'col_map' else {}
        st.cache_data.clear()
        st.rerun()

# ─────────────────────────────────────────────
# 프리셋 바
# ─────────────────────────────────────────────
st.markdown("")
p_cols = st.columns([1, 1, 1, 1, 1, 1, 0.4, 1.3])

with p_cols[0]:
    st.markdown('<p class="preset-label">분석 프리셋</p>', unsafe_allow_html=True)

PKEYS = ["프리셋 1", "프리셋 2", "프리셋 3", "프리셋 4", "프리셋 5"]
for i, pk in enumerate(PKEYS):
    with p_cols[i + 1]:
        nm = st.session_state.presets.get(pk, {}).get("name", pk)
        btype = "primary" if st.session_state.active_preset == pk else "secondary"
        if st.button(nm, key=f"pb_{i}", type=btype, use_container_width=True):
            st.session_state.active_preset = pk
            st.session_state.filtered_df = None
            st.rerun()

with p_cols[6]:
    if st.button("⚙️", key="gear", help="프리셋 필터 설정"):
        st.session_state.show_settings = not st.session_state.show_settings
        st.rerun()

with p_cols[7]:
    run_clicked = st.button("🔍 분석 실행", type="primary", use_container_width=True)

# ─────────────────────────────────────────────
# 프리셋 설정 패널
# ─────────────────────────────────────────────
if st.session_state.show_settings:
    st.markdown("---")
    ak = st.session_state.active_preset
    ap = st.session_state.presets.get(ak, {"name": ak, "filters": EMPTY_FILTERS.copy()})
    cf = ap.get("filters", EMPTY_FILTERS.copy())

    st.markdown(f"### ⚙️ 프리셋 설정 — `{ak}`")

    new_name = st.text_input("프리셋 이름", value=ap.get("name", ak), key="pname")

    st.markdown("")

    # ── 필터 UI ──
    c1, c2, c3 = st.columns(3)

    # ── 좌측: 기본 선택 ──
    with c1:
        st.markdown('<div class="filter-section-title">기본 조건</div>', unsafe_allow_html=True)

        brand_val = st.selectbox(
            "브랜드 여부",
            ["전체", "O", "X"],
            index=["전체", "O", "X"].index(cf.get("브랜드_키워드", "전체"))
            if cf.get("브랜드_키워드", "전체") in ["전체", "O", "X"] else 0,
            key="f_brand",
        )
        shop_val = st.selectbox(
            "쇼핑성 여부",
            ["전체", "O", "X"],
            index=["전체", "O", "X"].index(cf.get("쇼핑성_키워드", "전체"))
            if cf.get("쇼핑성_키워드", "전체") in ["전체", "O", "X"] else 0,
            key="f_shop",
        )
        season_val = st.selectbox(
            "계절성 여부",
            ["전체", "O", "X"],
            index=["전체", "O", "X"].index(cf.get("계절성", "전체"))
            if cf.get("계절성", "전체") in ["전체", "O", "X"] else 0,
            key="f_season",
        )

        st.markdown("**작년최대검색월** (복수 선택)")
        month_labels = [f"{m}월" for m in range(1, 13)]
        saved_months = cf.get("작년최대검색월", [])
        selected_months = []
        # 4열 × 3행 체크박스
        mc = st.columns(4)
        for idx, m in enumerate(range(1, 13)):
            with mc[idx % 4]:
                if st.checkbox(f"{m}월", value=(m in saved_months), key=f"m_{m}"):
                    selected_months.append(m)

    # ── 중앙: 검색량 관련 ──
    with c2:
        st.markdown('<div class="filter-section-title">검색량 · 검색월</div>', unsafe_allow_html=True)

        st.markdown("**작년 검색량**")
        yr_min = st.number_input(
            "최소", min_value=0, value=int(cf.get("작년_검색량_min") or 0),
            step=10000, key="f_yr_min", format="%d",
        )
        yr_max = st.number_input(
            "최대 (0 = 무제한)", min_value=0, value=int(cf.get("작년_검색량_max") or 0),
            step=10000, key="f_yr_max", format="%d",
        )

        st.markdown("**피크월 검색량** (작년최대검색월 검색량)")
        pk_min = st.number_input(
            "최소", min_value=0, value=int(cf.get("피크월검색량_min") or 0),
            step=5000, key="f_pk_min", format="%d",
        )
        pk_max = st.number_input(
            "최대 (0 = 무제한)", min_value=0, value=int(cf.get("피크월검색량_max") or 0),
            step=5000, key="f_pk_max", format="%d",
        )

    # ── 우측: 쿠팡 관련 ──
    with c3:
        st.markdown('<div class="filter-section-title">쿠팡 데이터</div>', unsafe_allow_html=True)

        st.markdown("**쿠팡 해외배송비율** (결과 기본정렬 기준)")
        co_min = st.number_input(
            "최소", min_value=0.0, max_value=1.0,
            value=float(cf.get("쿠팡_해외배송비율_min") or 0),
            step=0.05, format="%.2f", key="f_co_min",
        )
        co_max = st.number_input(
            "최대 (0 = 무제한)", min_value=0.0, max_value=1.0,
            value=float(cf.get("쿠팡_해외배송비율_max") or 0),
            step=0.05, format="%.2f", key="f_co_max",
        )

        st.markdown("**쿠팡 평균가**")
        cp_min = st.number_input(
            "최소", min_value=0, value=int(cf.get("쿠팡_평균가_min") or 0),
            step=5000, key="f_cp_min", format="%d",
        )
        cp_max = st.number_input(
            "최대 (0 = 무제한)", min_value=0, value=int(cf.get("쿠팡_평균가_max") or 0),
            step=5000, key="f_cp_max", format="%d",
        )

        st.markdown("**쿠팡 총리뷰수**")
        cr_min = st.number_input(
            "최소", min_value=0, value=int(cf.get("쿠팡_총리뷰수_min") or 0),
            step=10000, key="f_cr_min", format="%d",
        )
        cr_max = st.number_input(
            "최대 (0 = 무제한)", min_value=0, value=int(cf.get("쿠팡_총리뷰수_max") or 0),
            step=10000, key="f_cr_max", format="%d",
        )

    # 저장 / 닫기
    st.markdown("")
    sb1, sb2, sb3 = st.columns([1, 1, 5])
    with sb1:
        if st.button("💾 저장", type="primary", use_container_width=True):
            new_filters = {
                "브랜드_키워드": brand_val,
                "쇼핑성_키워드": shop_val,
                "계절성": season_val,
                "작년_검색량_min": yr_min if yr_min > 0 else None,
                "작년_검색량_max": yr_max if yr_max > 0 else None,
                "작년최대검색월": selected_months,
                "피크월검색량_min": pk_min if pk_min > 0 else None,
                "피크월검색량_max": pk_max if pk_max > 0 else None,
                "쿠팡_해외배송비율_min": co_min if co_min > 0 else None,
                "쿠팡_해외배송비율_max": co_max if co_max > 0 else None,
                "쿠팡_평균가_min": cp_min if cp_min > 0 else None,
                "쿠팡_평균가_max": cp_max if cp_max > 0 else None,
                "쿠팡_총리뷰수_min": cr_min if cr_min > 0 else None,
                "쿠팡_총리뷰수_max": cr_max if cr_max > 0 else None,
            }
            st.session_state.presets[ak] = {"name": new_name, "filters": new_filters}
            save_presets(st.session_state.presets)
            st.session_state.show_settings = False
            st.session_state.filtered_df = None
            st.success("✅ 프리셋 저장 완료!")
            st.rerun()
    with sb2:
        if st.button("❌ 닫기", use_container_width=True):
            st.session_state.show_settings = False
            st.rerun()

# ─────────────────────────────────────────────
# 분석 실행
# ─────────────────────────────────────────────
if run_clicked:
    if st.session_state.df is None:
        st.warning("⚠️ 먼저 파일을 업로드해주세요.")
    else:
        ak = st.session_state.active_preset
        flt = st.session_state.presets.get(ak, {}).get("filters", {})
        with st.spinner("🔍 분석 중…"):
            st.session_state.filtered_df = apply_filters(
                st.session_state.df, flt, st.session_state.col_map
            )

# ─────────────────────────────────────────────
# 결과 출력
# ─────────────────────────────────────────────
st.markdown("---")

if st.session_state.filtered_df is not None:
    result = st.session_state.filtered_df
    display = rename_display_cols(result, st.session_state.col_map)

    active_nm = st.session_state.presets.get(
        st.session_state.active_preset, {}
    ).get("name", st.session_state.active_preset)

    # 결과 헤더 행
    rc1, rc2, rc3, rc4 = st.columns([2.5, 3, 1, 1.2])

    with rc1:
        st.markdown(f"**📋 분석 결과** — `{active_nm}`")
        st.caption(f"총 **{len(display):,}**개 키워드 검출")

    with rc2:
        search = st.text_input(
            "🔎", value="", placeholder="결과 내 키워드 검색…",
            label_visibility="collapsed", key="tbl_search",
        )

    with rc3:
        if st.button("🔲 전체화면", use_container_width=True, key="fs"):
            st.session_state.fullscreen = not st.session_state.fullscreen
            st.rerun()

    with rc4:
        @st.cache_data
        def to_excel(dataframe):
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='openpyxl') as w:
                dataframe.to_excel(w, index=False, sheet_name='분석결과')
            return buf.getvalue()

        st.download_button(
            "📥 엑셀 다운로드",
            data=to_excel(display),
            file_name=f"분석결과_{active_nm}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    # 테이블 내 검색 적용
    view = display.copy()
    if search:
        mask = view.astype(str).apply(
            lambda x: x.str.contains(search, case=False, na=False)
        ).any(axis=1)
        view = view[mask]
        st.caption(f"🔎 검색 결과: **{len(view):,}**개")

    # 테이블 출력
    height = 800 if st.session_state.fullscreen else 500

    if st.session_state.fullscreen:
        if st.button("✕ 전체화면 닫기", key="fs_close"):
            st.session_state.fullscreen = False
            st.rerun()

    st.dataframe(view, use_container_width=True, height=height, hide_index=True)

    # 현재 적용된 필터 요약
    with st.expander("📌 현재 적용된 필터 조건", expanded=False):
        flt = st.session_state.presets.get(
            st.session_state.active_preset, {}
        ).get("filters", {})
        for k, v in flt.items():
            if v is not None and v != "전체" and v != [] and v != "" and v != 0:
                st.text(f"  • {k}: {v}")

elif st.session_state.df is not None:
    st.markdown(
        '<div class="result-box">'
        '<p style="margin-top:1rem;">프리셋을 선택하고 <b>분석 실행</b> 버튼을 눌러주세요.</p>'
        '<p style="font-size:0.9rem;">데이터가 없습니다.</p></div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        '<div class="result-box">'
        '<p style="margin-top:1rem;">파일을 업로드하고 분석 버튼을 눌러주세요.</p>'
        '<p style="font-size:0.9rem;">데이터가 없습니다.</p></div>',
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────
# 컬럼 매핑 확인 (디버그)
# ─────────────────────────────────────────────
if st.session_state.df is not None:
    with st.expander("🔧 컬럼 매핑 확인", expanded=False):
        for std, actual in sorted(st.session_state.col_map.items()):
            st.text(f"  {std}  →  {actual}")
