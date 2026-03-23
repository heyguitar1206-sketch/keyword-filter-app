import streamlit as st
import pandas as pd
import io

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
if "presets" not in st.session_state:
    st.session_state.presets = {
        0: {"name": "시즌소싱 26년 봄", "신규진입": "전체", "브랜드": "아님",
            "시즌성": "있음", "작년검색량_min": 0, "작년검색량_max": 9999999,
            "월검색량_min": 2000, "월검색량_max": 30000},
        1: {"name": "비시즌 가구", "신규진입": "전체", "브랜드": "아님",
            "시즌성": "없음", "작년검색량_min": 0, "작년검색량_max": 9999999,
            "월검색량_min": 1000, "월검색량_max": 50000},
        2: {"name": "프리셋 3", "신규진입": "전체", "브랜드": "전체",
            "시즌성": "전체", "작년검색량_min": 0, "작년검색량_max": 9999999,
            "월검색량_min": 0, "월검색량_max": 9999999},
        3: {"name": "프리셋 4", "신규진입": "전체", "브랜드": "전체",
            "시즌성": "전체", "작년검색량_min": 0, "작년검색량_max": 9999999,
            "월검색량_min": 0, "월검색량_max": 9999999},
        4: {"name": "프리셋 5", "신규진입": "전체", "브랜드": "전체",
            "시즌성": "전체", "작년검색량_min": 0, "작년검색량_max": 9999999,
            "월검색량_min": 0, "월검색량_max": 9999999},
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
    raw = pd.read_excel(io.BytesIO(file_bytes), sheet_name="all", header=[0, 1, 2])
    new_cols = []
    for col in raw.columns:
        parts = [str(c).strip() for c in col if str(c).strip() not in ("nan", "")]
        new_cols.append("_".join(dict.fromkeys(parts)))
    raw.columns = new_cols
    return raw

def find_col(df, keywords):
    for col in df.columns:
        if all(kw in col for kw in keywords):
            return col
    return None

def get_col_map(df):
    return {
        "신규진입":         find_col(df, ["신규진입"]),
        "키워드":           find_col(df, ["키워드"]),
        "카테고리":         find_col(df, ["카테고리"]),
        "브랜드":           find_col(df, ["브랜드"]),
        "쇼핑성":           find_col(df, ["쇼핑성"]),
        "경쟁률":           find_col(df, ["경쟁률"]),
        "최근1개월검색량":  find_col(df, ["최근", "1개월", "검색량"]),
        "예상1개월검색량":  find_col(df, ["예상", "1개월", "검색량"]),
        "작년검색량":       find_col(df, ["작년", "검색량"]),
        "계절성":           find_col(df, ["계절성"]),
        "네이버상품수":     find_col(df, ["네이버", "상품수"]),
        "네이버평균가":     find_col(df, ["네이버", "평균가"]),
        "네이버경쟁강도":   find_col(df, ["경쟁강도"]),
        "쿠팡평균가":       find_col(df, ["쿠팡", "평균가"]),
        "쿠팡총리뷰수":     find_col(df, ["쿠팡", "총리뷰수"]),
        "쿠팡로켓배송비율": find_col(df, ["로켓배송비율"]),
    }

def apply_preset(df, col_map, preset):
    fdf = df.copy()
    if preset["신규진입"] != "전체" and col_map.get("신규진입"):
        val = "O" if preset["신규진입"] == "O" else "X"
        fdf = fdf[fdf[col_map["신규진입"]].astype(str).str.strip() == val]
    if preset["브랜드"] != "전체" and col_map.get("브랜드"):
        val = "O" if preset["브랜드"] == "맞음" else "X"
        fdf = fdf[fdf[col_map["브랜드"]].astype(str).str.strip() == val]
    if preset["시즌성"] != "전체" and col_map.get("계절성"):
        fdf = fdf[fdf[col_map["계절성"]].astype(str).str.strip() == preset["시즌성"]]
    if col_map.get("작년검색량"):
        fdf[col_map["작년검색량"]] = pd.to_numeric(fdf[col_map["작년검색량"]], errors="coerce")
        fdf = fdf[(fdf[col_map["작년검색량"]] >= preset["작년검색량_min"]) &
                  (fdf[col_map["작년검색량"]] <= preset["작년검색량_max"])]
    if col_map.get("최근1개월검색량"):
        fdf[col_map["최근1개월검색량"]] = pd.to_numeric(fdf[col_map["최근1개월검색량"]], errors="coerce")
        fdf = fdf[(fdf[col_map["최근1개월검색량"]] >= preset["월검색량_min"]) &
                  (fdf[col_map["최근1개월검색량"]] <= preset["월검색량_max"])]
    return fdf.reset_index(drop=True)

def build_display_df(fdf, col_map):
    mapping = {
        "키워드": "키워드", "카테고리": "카테고리", "브랜드": "브랜드",
        "쇼핑성": "쇼핑성", "경쟁률": "경쟁률",
        "최근1개월검색량": "최근1개월 검색량", "예상1개월검색량": "예상1개월 검색량",
        "작년검색량": "작년 검색량", "계절성": "계절성",
        "네이버상품수": "네이버 상품수", "네이버평균가": "네이버 평균가",
        "네이버경쟁강도": "경쟁강도", "쿠팡평균가": "쿠팡 평균가",
        "쿠팡총리뷰수": "쿠팡 총리뷰", "쿠팡로켓배송비율": "로켓배송비율",
    }
    display_cols = {}
    for key, label in mapping.items():
        if col_map.get(key) and col_map[key] in fdf.columns:
            display_cols[col_map[key]] = label
    return fdf[list(display_cols.keys())].rename(columns=display_cols)

# ── 타이틀 ──
st.markdown("""
<div class="main-title">키워드 <span>분석 도구</span></div>
<div class="sub-title">쇼핑성 키워드 선별 및 데이터 전략 분석 도구</div>
""", unsafe_allow_html=True)

# ── 파일 업로드 ──
st.markdown('<div class="card">', unsafe_allow_html=True)
uploaded = st.file_uploader("📂 분석할 파일을 업로드하세요 (.xlsx)", type=["xlsx"])
if uploaded:
    file_bytes = uploaded.read()
    st.session_state.df = load_excel(file_bytes)
    st.success(f"✅ 파일 로드 완료! 총 **{len(st.session_state.df):,}개** 키워드")
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
            btn_type = "primary" if st.session_state.active_preset == i else "secondary"
            if st.button(label, key=f"preset_btn_{i}", type=btn_type, use_container_width=True):
                st.session_state.active_preset = i
                st.rerun()

with col_setting:
    st.markdown("&nbsp;")
    if st.button("⚙️ 설정", use_container_width=True):
        st.session_state.show_preset_modal = True
        st.rerun()

with col_run:
    st.markdown("&nbsp;")
    run_clicked = st.button("🔍 분석 실행", type="primary", use_container_width=True)
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
            new_name = st.text_input("프리셋 이름", value=p["name"], key=f"name_{i}")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<div class="field-label">신규진입키워드</div>', unsafe_allow_html=True)
                new_진입 = st.selectbox("", ["전체", "O", "X"],
                    index=["전체","O","X"].index(p["신규진입"]),
                    key=f"진입_{i}", label_visibility="collapsed")

                st.markdown('<div class="field-label">시즌성(계절성)</div>', unsafe_allow_html=True)
                new_시즌 = st.selectbox("", ["전체", "있음", "없음"],
                    index=["전체","있음","없음"].index(p["시즌성"]),
                    key=f"시즌_{i}", label_visibility="collapsed")

            with col2:
                st.markdown('<div class="field-label">브랜드키워드</div>', unsafe_allow_html=True)
                new_브랜드 = st.selectbox("", ["전체", "맞음", "아님"],
                    index=["전체","맞음","아님"].index(p["브랜드"]),
                    key=f"브랜드_{i}", label_visibility="collapsed")

                st.markdown('<div class="field-label">작년 검색량 범위</div>', unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    new_작년_min = st.number_input("최소", value=p["작년검색량_min"],
                        min_value=0, key=f"작년min_{i}")
                with c2:
                    new_작년_max = st.number_input("최대", value=p["작년검색량_max"],
                        min_value=0, key=f"작년max_{i}")

            st.markdown('<div class="field-label">월검색량 범위</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                new_월_min = st.number_input("최소", value=p["월검색량_min"],
                    min_value=0, key=f"월min_{i}")
            with c2:
                new_월_max = st.number_input("최대", value=p["월검색량_max"],
                    min_value=0, key=f"월max_{i}")

            st.markdown("<br>", unsafe_allow_html=True)
            s1, s2 = st.columns(2)
            with s1:
                if st.button("💾 설정 저장 및 적용", key=f"save_{i}",
                             type="primary", use_container_width=True):
                    st.session_state.presets[i] = {
                        "name": new_name, "신규진입": new_진입,
                        "브랜드": new_브랜드, "시즌성": new_시즌,
                        "작년검색량_min": int(new_작년_min),
                        "작년검색량_max": int(new_작년_max),
                        "월검색량_min": int(new_월_min),
                        "월검색량_max": int(new_월_max),
                    }
                    st.session_state.active_preset = i
                    st.session_state.show_preset_modal = False
                    st.success(f"✅ [{new_name}] 저장 완료!")
                    st.rerun()
            with s2:
                if st.button("취소", key=f"cancel_{i}", use_container_width=True):
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
    preset_name = st.session_state.presets[st.session_state.active_preset]["name"]

    st.markdown('<div class="card">', unsafe_allow_html=True)
    r1, r2 = st.columns([3, 1])
    with r1:
        st.markdown(
            f'<div class="result-count">📊 [{preset_name}] 결과: <b>{count:,}개</b> 키워드</div>',
            unsafe_allow_html=True)
    with r2:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            result.to_excel(writer, index=False, sheet_name="필터결과")
        st.download_button(
            label="⬇️ 엑셀 다운로드",
            data=buffer.getvalue(),
            file_name=f"키워드분석_{preset_name}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True)

    st.dataframe(
        result,
        use_container_width=True,
        height=600,
        column_config={
            "키워드":           st.column_config.TextColumn("🔑 키워드", width="medium"),
            "카테고리":         st.column_config.TextColumn("📂 카테고리", width="large"),
            "경쟁률":           st.column_config.NumberColumn("⚡ 경쟁률", format="%.2f"),
            "최근1개월 검색량": st.column_config.NumberColumn("📈 1개월 검색량", format="%d"),
            "작년 검색량":      st.column_config.NumberColumn("📅 작년 검색량", format="%d"),
            "네이버 평균가":    st.column_config.NumberColumn("💰 네이버 평균가", format="₩%d"),
            "쿠팡 평균가":      st.column_config.NumberColumn("🛒 쿠팡 평균가", format="₩%d"),
            "로켓배송비율":     st.column_config.ProgressColumn(
                "🚀 로켓배송", min_value=0, max_value=1, format="%.0%%"),
        })
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center; padding:40px; color:#bbb;">
        <div style="font-size:48px;">📂</div>
        <div style="font-size:16px; margin-top:12px;">파일을 업로드하고 분석 버튼을 눌러주세요.</div>
        <div style="font-size:13px; margin-top:6px; color:#ccc;">데이터가 없습니다.</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
