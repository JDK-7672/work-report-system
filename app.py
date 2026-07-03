import streamlit as st
import pandas as pd
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

# (기존 get_sheet 함수는 유지하되, 전체 시트를 관리하도록 확장)
def get_client():
    creds_dict = dict(st.secrets["gspread"])
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return gspread.authorize(creds)

st.title("📝 2028년도 무상원조 시행계획 작성 시스템")

# 1. 시트에서 목록 가져오기 (매번 호출하지 않게 캐싱 처리)
@st.cache_data(ttl=600)
def load_data():
    client = get_client()
    sh = client.open_by_key("1cOPrHkEUYfS1tyQX_mOpPiikfN8CBhREJwS2SinTVpg")
    # '목록' 탭에서 부서와 사업을 가져옴
    df = pd.DataFrame(sh.worksheet("목록").get_all_records())
    return df

df_list = load_data()

# 2. 1단계: 부서 및 사업 선택
if 'step' not in st.session_state: st.session_state.step = 1

if st.session_state.step == 1:
    st.subheader("1단계: 부서 및 사업 선택")
    
    # 부서 목록 생성 (중복 제거)
    depts = df_list['부서명'].unique().tolist()
    selected_dept = st.selectbox("부서 선택", depts)
    
    # 선택된 부서에 맞는 사업만 필터링
    projects = df_list[df_list['부서명'] == selected_dept]['사업명'].tolist()
    selected_project = st.selectbox("사업 선택", projects)
    
    if st.button("작성하기"):
        st.session_state.selected_dept = selected_dept
        st.session_state.selected_project = selected_project
        st.session_state.step = 2
        st.rerun()

# 4. 2단계: 사업 기본정보 확인
elif st.session_state.step == 2:
    st.subheader("2단계: 사업 기본정보 확인")
    st.info(f"현재 선택된 사업: {st.session_state.selected_project} ({st.session_state.selected_dept})")
    
    with st.form("detail_form"):
        # 2열 레이아웃으로 항목 배치 (화면을 덜 길게 만들기)
        col1, col2 = st.columns(2)
        
        with col1:
            ipm_code = st.text_input("IPM사업코드")
            gukjo_code = st.text_input("국조실사업코드")
            dept_org = st.text_input("소관부처(기관)")
            unit_biz = st.text_input("관(단위사업)")
            sub_biz = st.text_input("항(세부사업)")
            detail_biz = st.text_input("목(내역사업)")
            kor_name = st.text_input("사업명(국문)")
            eng_name = st.text_input("사업명(영문)")
            
        with col2:
            start_year = st.text_input("시작연도")
            end_year = st.text_input("종료연도")
            status = st.text_input("상태구분")
            total_budget = st.text_input("총사업예산(백만원)")
            target_country = st.text_input("대상국가(* 다국가인 경우 '다국가' 입력)")
            all_countries = st.text_input("(다국가인 경우) 전체 국가명")
            region = st.text_input("사업지역")
            biz_type = st.text_input("사업유형")
            biz_field = st.text_input("사업분야")
        
        submitted = st.form_submit_button("제출 완료")
        
        if submitted:
            # 구글 시트에 저장할 데이터 리스트 (열 순서 맞추기)
            data = [
                st.session_state.selected_dept, st.session_state.selected_project,
                ipm_code, gukjo_code, dept_org, unit_biz, sub_biz, detail_biz,
                kor_name, eng_name, start_year, end_year, status, total_budget,
                target_country, all_countries, region, biz_type, biz_field
            ]
            
            # 구글 시트 저장 (append_row)
            get_sheet().append_row(data)
            
            st.success("데이터가 성공적으로 저장되었습니다!")
            st.session_state.submitted = True

    # 폼 바깥 버튼
    if st.session_state.get('submitted', False):
        if st.button("처음으로 돌아가기"):
            st.session_state.submitted = False
            st.session_state.step = 1
            st.rerun()