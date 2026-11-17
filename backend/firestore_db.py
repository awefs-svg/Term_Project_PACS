from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st

def get_db():
    """Firebase Admin SDK 초기화 및 Firestore 클라이언트 반환"""
    if not firebase_admin._apps:
        cred_dict = dict(st.secrets["firebase_service_account"])
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
    return firestore.client()

def create_case(case_id: str, exam_type: str, image_path: str, user: dict):
    """신규 모의 케이스 등록 (등록 담당자 권한 필요)"""
    if user.get("role") != "등록 담당자":
        raise PermissionError("케이스 등록 권한이 없습니다. (등록 담당자 전용)")

    db = get_db()
    doc_ref = db.collection("cases").document(case_id)
    if doc_ref.get().exists:
        raise ValueError(f"이미 존재하는 케이스 ID입니다: {case_id}")

    doc_ref.set({
        "case_id": case_id,
        "exam_type": exam_type,
        "image_path": image_path,
        "status": "접수",  # 접수 -> 검토 중 -> 완료
        "uploader": user["email"],
        "reviewer": None,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })

def get_cases(keyword: str = "", status_filter: str = "전체") -> list[dict]:
    """케이스 목록 조회 및 검색/상태 필터링"""
    db = get_db()
    docs = db.collection("cases").order_by("created_at", direction=firestore.Query.DESCENDING).stream()
    results = []
    for doc in docs:
        item = doc.to_dict()
        if status_filter != "전체" and item.get("status") != status_filter:
            continue
        if keyword and (keyword.lower() not in item.get("case_id", "").lower() and keyword.lower() not in item.get("exam_type", "").lower()):
            continue
        results.append(item)
    return results

def update_case_review(case_id: str, new_status: str, memo: str, user: dict):
    """검토 상태 변경 및 판독 메모 저장 (검토 담당자 권한 및 상태 전이 규칙 검증)"""
    if user.get("role") != "검토 담당자":
        raise PermissionError("검토 상태 변경 및 메모 작성 권한이 없습니다. (검토 담당자 전용)")

    db = get_db()
    doc_ref = db.collection("cases").document(case_id)
    snap = doc_ref.get()
    if not snap.exists:
        raise ValueError("존재하지 않는 케이스입니다.")

    current_status = snap.to_dict().get("status")
    # 상태 전이 규칙: 완료된 건은 '검토 중(재검토)'으로만 전환 가능
    if current_status == "완료" and new_status == "접수":
        raise ValueError("완료된 케이스는 접수 상태로 되돌릴 수 없습니다.")

    doc_ref.update({
        "status": new_status,
        "reviewer": user["email"],
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })

    if memo.strip():
        db.collection("cases").document(case_id).collection("reviews").add({
            "memo": memo,
            "author": user["email"],
            "status_at_time": new_status,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })

def get_case_reviews(case_id: str) -> list[dict]:
    """특정 케이스의 검토 메모 및 이력 조회"""
    db = get_db()
    docs = (
        db.collection("cases")
        .document(case_id)
        .collection("reviews")
        .order_by("created_at", direction=firestore.Query.DESCENDING)
        .stream()
    )
    return [d.to_dict() for d in docs]