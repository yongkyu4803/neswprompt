# 뉴스 요약 프롬프트 생성기 - Streamlit 버전

이 프로젝트는 뉴스 요약 프롬프트를 생성하는 Streamlit 애플리케이션입니다. 사용자가 JSON 형식의 뉴스 데이터를 입력하면, 해당 데이터를 기반으로 프롬프트를 생성하고 다양한 형식으로 출력합니다.

## 기능

- JSON 형식의 뉴스 데이터 파싱
- 맞춤형 프롬프트 생성 (주제, 날짜, 분야 등 커스터마이징 가능)
- SNS용 포맷 출력
- 구글 시트용 포맷 출력 및 CSV 다운로드
- 뉴스 항목 카드뷰 표시

## 설치 및 실행 방법

1. 필요한 패키지 설치:

```bash
pip install -r requirements.txt
```

2. Streamlit 앱 실행:

```bash
streamlit run prompt_generator_streamlit.py
```

3. 웹 브라우저에서 앱 접속 (기본 URL: http://localhost:8501)

## 사용 방법

1. 사이드바의 "JSON 입력" 영역에 뉴스 데이터를 JSON 형식으로 입력합니다.
2. "JSON 파싱" 버튼을 클릭하여 데이터를 파싱합니다.
3. 프롬프트 생성 섹션에서 필요한 설정을 조정합니다 (주제, 날짜, 분야 등).
4. "프롬프트 생성" 버튼을 클릭하여 프롬프트를 생성합니다.
5. 생성된 프롬프트를 복사하여 사용합니다.
6. "SNS용 포맷 보기" 또는 "구글시트용 포맷 보기" 버튼을 클릭하여 다양한 형식으로 데이터를 확인합니다.

## JSON 데이터 형식

입력 JSON 데이터는 다음 형식을 따라야 합니다:

```json
[
  {
    "title": "기사 제목",
    "link": "기사 URL",
    "media": "언론사명",
    "pubDate": "YYYY-MM-DD",
    "summary": "기사 요약 (3-4문장)",
    "one_sentence_summary": "한 문장 요약"
  },
  ...
]
```

## 배포 정보

이 애플리케이션은 Streamlit Cloud 또는 다른 서버에 배포하여 사용할 수 있습니다. Streamlit Cloud에 배포하는 방법:

1. GitHub에 코드를 업로드합니다.
2. [Streamlit Sharing](https://streamlit.io/sharing)에 가입합니다.
3. 새 앱을 생성하고 GitHub 저장소를 연결합니다.
4. 메인 파일 경로를 `progen_streamlit.py`로 설정합니다. 