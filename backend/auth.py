import requests
import streamlit as st

# 시연용 계정 이메일에 따른 역할(Role) 자동 매핑 (또는 Firestore users 컬렉션 연동)
ROLE_MAP = {
    "uploader@pacs.com": "등록 담당자",
    "reviewer@pacs.com": "검토 담당자",
}

def login_with_email(email: str, password: str) -> dict:
    """Firebase Auth REST API로 이메일/비밀번호 로그인 수행"""
    api_key = st.secrets["FIREBASE_WEB_API_KEY"]
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True,
    }
    res = requests.post(url, json=payload, timeout=10)
    data = res.json()

    if res.status_code != 200:
        error_msg = data.get("error", {}).get("message", "로그인 실패")
        raise ValueError(f"로그인 오류: {error_msg}")

    user_email = data["email"]
    # 기본 역할 배정 (uploader가 포함되면 등록 담당자, 그 외는 검토 담당자)
    role = ROLE_MAP.get(user_email, "등록 담당자" if "uploader" in user_email else "검토 담당자")

    return {
        "uid": data["localId"],
        "email": user_email,
        "role": role,
        "id_token": data["idToken"],
    }

def check_permission(user: dict | None, allowed_roles: list[str]) -> bool:
    """백엔드 데이터 접근 전 로그인 및 역할 권한 검증 (안내문 3p 필수)"""
    if not user:
        return False
    return user.get("role") in allowed_roles