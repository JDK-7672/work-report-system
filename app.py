import streamlit as st
import json
from oauth2client.service_account import ServiceAccountCredentials
import gspread

def get_sheet():
    # 1. 스트림릿 비밀 설정에서 JSON 가져오기
    json_data = st.secrets["GSPREAD_JSON"]
    creds_dict = json.loads(json_data)
    
    # 2. 인증 설정
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    
    # 3. 시트 연결
    sheet = client.open_by_key("1cOPrHkEUYfS1tyQX_mOpPiikfN8CBhREJwS2SinTVpg").sheet1
    return sheet

# 2. 초기 상태 설정
if 'step' not in st.session_state:
    st.session_state.step = 1

st.title("📊 부서별 업무 보고 시스템")

# 부서-사업 매핑
dept_project_map = {
    "ㄱ부서": ["베트남 A사업"],
    "ㄴ부서": ["인도네시아 B사업"],
    "ㄷ부서": ["필리핀 C사업"]
}

# 3. 1단계: 부서 및 사업 선택
if st.session_state.step == 1:
    st.subheader("1단계: 부서 및 사업 선택")
    selected_dept = st.selectbox("부서 선택", list(dept_project_map.keys()))
    selected_project = st.selectbox("사업 선택", dept_project_map[selected_dept])
    
    if st.button("작성하기"):
        st.session_state.selected_dept = selected_dept
        st.session_state.selected_project = selected_project
        st.session_state.step = 2
        st.rerun()

# 4. 2단계: 세부 정보 입력
elif st.session_state.step == 2:
    st.subheader(f"2단계: {st.session_state.selected_dept} - {st.session_state.selected_project} 업무 보고")
    
    with st.form("detail_form"):
        manager = st.text_input("담당자 성명")
        week = st.text_input("보고 주차")
        achievement = st.text_area("금주 주요 실적")
        progress = st.slider("진행률(%)", 0, 100, 50)
        risk = st.text_area("주요 현안/리스크")
        plan = st.text_area("차주 주요 계획")
        
        submitted = st.form_submit_button("제출 완료")
        
        if submitted:
            data = [week, st.session_state.selected_dept, st.session_state.selected_project, 
                    manager, achievement, progress, risk, plan]
            get_sheet().append_row(data)
            st.success("제출이 완료되었습니다!")
            st.session_state.submitted = True # 제출 완료 상태 저장

    # 폼 바깥으로 이동: "처음으로 돌아가기" 버튼
    if st.session_state.get('submitted', False):
        if st.button("처음으로 돌아가기"):
            st.session_state.submitted = False # 상태 초기화
            st.session_state.step = 1
            st.rerun()