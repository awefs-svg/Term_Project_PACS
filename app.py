from pathlib import Path
import cv2
import numpy as np
import streamlit as st

from backend.auth import login_with_email
from backend.firestore_db import (
    create_case,
    get_cases,
    update_case_review,
    get_case_reviews,
)

st.set_page_config(page_title="PACS", layout="wide")

# 영구 저장 디렉토리 생성
IMAGE_DIR = Path("data/images")
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

# 세션 상태 초기화
if "user" not in st.session_state:
    st.session_state.user = None
if "current_image" not in st.session_state:
    st.session_state.current_image = None
if "previous_image" not in st.session_state:
    st.session_state.previous_image = None
if "selected_case" not in st.session_state:
    st.session_state.selected_case = None

# ==========================================
# 0. 로그인 화면 (Firebase Authentication)
# ==========================================
if st.session_state.user is None:
    st.title("PACS 로그인")
    st.caption("교육용 의료영상 관리 및 영상처리 시스템 (모의 케이스 전용)")

    with st.form("login_form"):
        email = st.text_input("이메일", placeholder="uploader@pacs.com 또는 reviewer@pacs.com")
        password = st.text_input("비밀번호", type="password")
        submitted = st.form_submit_button("로그인")

        if submitted:
            try:
                st.session_state.user = login_with_email(email, password)
                st.success("로그인 성공!")
                st.rerun()
            except Exception as e:
                st.error(str(e))
    st.stop()

# ==========================================
# 로그인 이후 메인 PACS 화면
# ==========================================
user = st.session_state.user

header_col1, header_col2 = st.columns([4, 1])
with header_col1:
    st.title("PACS")
    st.caption("교육용 의료영상 관리 및 영상처리 시스템")
with header_col2:
    st.write(f"👤 **{user['email']}**")
    st.caption(f"역할: `{user['role']}`")
    if st.button("로그아웃"):
        st.session_state.user = None
        st.session_state.selected_case = None
        st.rerun()

# 상단 : 영상 조회 도구
st.subheader("영상 조회")
toolbar1, toolbar2 = st.columns([3, 1])
with toolbar1:
    if st.session_state.selected_case:
        c = st.session_state.selected_case
        st.caption(f"선택된 케이스: **{c['case_id']}** ({c['exam_type']}) | 상태: **{c['status']}**")
    else:
        st.caption("워크리스트에서 케이스를 선택하거나 영상을 열어 비교하세요.")
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

# 오른쪽 : 워크리스트 (Firestore 연동)
with worklist:
    st.subheader("워크리스트")

    # 1) 케이스 검색 및 상태 필터
    s_col1, s_col2 = st.columns([2, 1])
    with s_col1:
        search = st.text_input("검사 검색", placeholder="모의 케이스 ID 또는 검사 구분")
    with s_col2:
        status_filter = st.selectbox("상태 필터", ["전체", "접수", "검토 중", "완료"])

    try:
        cases = get_cases(keyword=search, status_filter=status_filter)
    except Exception as e:
        st.error(f"Firestore 조회 오류: {e}")
        cases = []

    if not cases:
        st.info("등록된 모의 케이스가 없습니다.")
    else:
        for case in cases:
            with st.container(border=True):
                c1, c2, c3 = st.columns([2, 1, 1])
                c1.write(f"**{case['case_id']}** · {case['exam_type']} (`{case['status']}`)")
                if c2.button("현재 영상 열기", key=f"cur_{case['case_id']}"):
                    img_path = Path(case["image_path"])
                    if img_path.exists():
                        st.session_state.current_image = img_path.read_bytes()
                        st.session_state.selected_case = case
                        st.rerun()
                    else:
                        st.error("원본 이미지 파일을 찾을 수 없습니다.")
                if c3.button("과거 영상 열기", key=f"prev_{case['case_id']}"):
                    img_path = Path(case["image_path"])
                    if img_path.exists():
                        st.session_state.previous_image = img_path.read_bytes()
                        st.rerun()

    st.divider()

    # 2) 신규 케이스 및 영상 등록 (등록 담당자 전용)
    with st.expander("➕ 신규 모의 케이스 등록 (등록 담당자 전용)", expanded=(user["role"] == "등록 담당자")):
        new_case_id = st.text_input("모의 케이스 ID", placeholder="예: CASE-2026-001")
        new_exam_type = st.text_input("검사 구분", placeholder="예: Chest X-ray (모의)")
        file = st.file_uploader("영상 업로드", type=["png", "jpg", "jpeg"])

        if file is not None:
            raw = file.getvalue()
            image = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR) if raw else None
            if image is None:
                st.error("유효하지 않은 이미지 파일입니다.")
            else:
                st.image(image, channels="BGR", width=160)
                if st.button("케이스 및 영상 DB 저장"):
                    if not new_case_id.strip() or not new_exam_type.strip():
                        st.warning("케이스 ID와 검사 구분을 모두 입력하세요.")
                    else:
                        try:
                            save_path = IMAGE_DIR / f"{new_case_id}_{file.name}"
                            save_path.write_bytes(raw)
                            create_case(new_case_id.strip(), new_exam_type.strip(), str(save_path), user)
                            st.success(f"케이스({new_case_id})가 Firestore에 저장되었습니다.")
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))

# 하단 : 영상처리 및 검토
st.divider()
processing, review = st.columns(2)

with processing:
    st.subheader("영상처리 및 ROI 분석")
    st.info("다음 단계: 알고리즘 3종(CLAHE, Gaussian, Canny) 및 ROI 히스토그램 구현 영역")

with review:
    st.subheader("검토 및 이력")
    if st.session_state.selected_case is None:
        st.info("워크리스트에서 '현재 영상 열기'로 케이스를 선택하면 검토 및 이력이 표시됩니다.")
    else:
        sel = st.session_state.selected_case
        st.write(f"대상 케이스: **{sel['case_id']}** (현재 상태: `{sel['status']}`)")

        next_status = st.selectbox("변경할 상태", ["접수", "검토 중", "완료"], index=["접수", "검토 중", "완료"].index(sel["status"]))
        memo_input = st.text_area("검토 메모 / 판독 요약", placeholder="영상 소견 및 처리 결과를 입력하세요.")

        if st.button("검토 상태 및 메모 저장"):
            try:
                update_case_review(sel["case_id"], next_status, memo_input, user)
                st.session_state.selected_case["status"] = next_status
                st.success("검토 기록이 Firestore에 저장되었습니다.")
                st.rerun()
            except Exception as e:
                st.error(str(e))

        st.write("**검토 이력**")
        reviews = get_case_reviews(sel["case_id"])
        if not reviews:
            st.caption("아직 작성된 검토 메모가 없습니다.")
        else:
            for r in reviews:
                st.markdown(f"- `[{r['created_at']}]` **{r['author']}** ({r['status_at_time']}): {r['memo']}")