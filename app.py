from pathlib import Path
import hashlib
import cv2
import numpy as np
import streamlit as st

st.set_page_config(page_title="PACS", layout="wide")
st.title("PACS")
st.caption("교육용 의료영상 관리 및 영상처리 시스템")

# 영상 조회 상태 초기화
if "current_image" not in st.session_state:
    st.session_state.current_image = None
if "previous_image" not in st.session_state:
    st.session_state.previous_image = None

# 상단 : 영상 조회 도구 
st.subheader("영상 조회")
toolbar1, toolbar2 = st.columns([3, 1])

with toolbar1:
    st.caption("워크리스트에서 선택한 영상을 조회하고 비교")

with toolbar2:
    if st.button("영상 초기화"):
        st.session_state.current_image = None
        st.session_state.previous_image = None
        st.rerun()

st.divider()

# 왼쪽과 오른쪽 화면 구분
viewer, worklist = st.columns([1, 1])

# 왼쪽 : 영상 조회 화면
with viewer:
    st.subheader("영상 뷰어")

    current, previous = st.columns(2)

    #현재 영상
    with current:
        st.write("현재 영상")

        if st.session_state.current_image is None:
            st.info("영상 없음")
        else:
            image = cv2.imdecode(np.frombuffer(st.session_state.current_image, np.uint8), cv2.IMREAD_COLOR)
            if image is not None:
                st.image(image, channels="BGR")
            if st.button("현재 영상 닫기"):
                st.session_state.current_image = None
                st.rerun()
    # 과거 영상
    with previous:
        st.write("과거 영상")

        if st.session_state.previous_image is None:
            st.info("영상 없음")
        else:
            image = cv2.imdecode(np.frombuffer(st.session_state.previous_image, np.uint8), cv2.IMREAD_COLOR)
            if image is not None:
                st.image(image, channels="BGR")
            if st.button("과거 영상 닫기"):
                st.session_state.previous_image = None
                st.rerun()          

# 오른쪽 : 워크리스트
with worklist:
    st.subheader("워크리스트")

    search = st.text_input("검사 검색", placeholder="환자 ID 또는 검사 정보")
    st.info("환자 목록, 검사 목록 및 검색 기능 구현 예정")
    st.write("검사 영상 선택")

    file = st.file_uploader("영상 업로드", type=["png","jpg","jpeg"])
    
    if file is not None:
        raw = file.getvalue()
        if not raw:
            st.error("빈 파일")
        else:
            image = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)
            if image is None:
                st.error("이미지를 읽을 수 없음")
            else:
                st.write("미리보기")
                st.image(image, channels="BGR", width=180)
                left_button, right_button = st.columns(2)

                with left_button:
                    if st.button("현재 영상으로 열기"):
                        st.session_state.current_image = raw
                        st.rerun()
                with right_button:
                    if st.button("과거 영상으로 열기"):
                        st.session_state.previous_image = raw
                        st.rerun()
                
    st.divider()

    st.write("판독문")
    st.info("선택한 검사의 판독문 조회 기능 구현 예정")

# 하단 : 영상처리 및 검토
st.divider()

processing, review = st.columns(2)

with processing:
    st.subheader("영상처리 및 ROI 분석")
    st.info("영상처리 알고리즘, ROI 통계 및 히스토그램 구현 예정")

with review:
    st.subheader("검토 및 이력")
    st.info("담당자, 검토 상태, 메모 및 처리 이력 구현 예정")
