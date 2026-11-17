# PACS
초급프로젝트(PBL) 텀프로젝트로 진행하는 교육용 의료영상 관리 및 영상처리 시스템입니다.

## 1. 프로젝트 소개
Python과 Streamlit을 활용해 의료영상의 등록, 조회, 영상처리 및 검토 기능을 제공하는 웹 기반 PACS 프로토타입을 개발하는 프로젝트입니다.

실제 PACS의 작업 흐름을 참고해 오른쪽 워크리스트에서 검사를 선택, 왼쪽 영상 뷰어에서 영상을 조회하거나 과거 영상과 비교할 수 있도록 구현할 예정입니다.

## 2. 초기 개발 환경 
11주차 PBL 이미지 처리 및 Streamlit 실습 코드를 기반으로 프로젝트의 초기 환경을 구성했습니다.

**"현재 구현된 내용**
1. Streamlit을 활용한 PACS 기본 웹 화면 구성
2. 왼쪽 영상 뷰어, 오른쪽 워크리스트 영역 구성
3. PNG/JPEG 이미지 업로드 및 미리보기 표시
4. 현재 영상과 과거 영상을 나란히 표시하는 비교 화면 구성
5. 버튼을 이용한 영상 열기 및 초기화 기능
6. OpenCV와 NumPy를 활용한 이미지 읽기
7. 영상처리, ROI 분석, 검토 및 이력 관리 영역 구성

현재 워크리스트는 테스트용 영상 업로드를 기반으로 동작하며, 실제 환자 검색, 검사 목록 조회 기능은 구현할 예정입니다.

또한 현재, 과거 영상은 버튼을 선택해 표시하며, 미리보기 이미지를 드래그 앤 드롭으로 여는 기능은 추후에 구현할 예정입니다.

## 3. 개발 및 실행 환경
- **Language / Package Manager:** Python 3.12, `uv`
- **Framework & Libraries:** Streamlit, OpenCV (`opencv-python-headless`), NumPy, Matplotlib/Plotly
- **Auth & Database:** Firebase Authentication, Cloud Firestore, Firebase Storage (또는 JCloud 영구 볼륨)
- **Deploy:** JCloud

## 4. 설치 및 로컬 실행 방법
1. 저장소 클론 및 의존성 설치
   ```bash
   git clone [https://github.com/awefs-svg/Term_Project_PACS.git](https://github.com/awefs-svg/Term_Project_PACS.git)
   cd Term_Project_PACS
   uv sync

## 5. 초기 기능 사용 방법
1. 오른쪽 워크리스트 영역에 PNG/JPEG 이미지를 업로드합니다.
2. 업로드한 이미지의 미리보기를 확인합니다.
3. 현재 영상으로 열기 또는 과거 영상으로 열기 버튼을 클릭합니다.
4. 왼쪽 영상 뷰어에서 두 영상을 나란히 확인합니다.
5. 영상 초기화 버튼으로 표시된 영상을 초기화할 수 있습니다.

## 5. 향후 개발 계획
- 환자 및 검사 등록, 검색, 조회 기능
- 검사별 영상 썸네일 목록 및 판독문 조회
- 미리보기 이미지 드래그 앤 드롭 기능
- 영상 확대, 축소, 이동, 초기화 및 비교 기능
- 영상처리 알고리즘 3종 이상 구현
- ROI 선택, 통계 및 히스토그램 분석
- 판독 메모, 요약 리포트 및 처리 이력, 저장 및 조회
- Firebase Authentication 및 Firestore 연동
- JCloud 배포

## 6. 참고 자료
- 초급프로젝트(PBL) 11주차 이미지 처리 및 Streamlit 실습
- 의료영상과 PACS 특강
- ChatGPT(GPT-6) => 개발 과정에서 코드 구성 참고
