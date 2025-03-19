import streamlit as st
import json
import datetime
import pandas as pd
from datetime import date
import base64

# 페이지 설정
st.set_page_config(
    page_title="뉴스 요약 프롬프트 생성기",
    page_icon="📰",
    layout="centered",
)

# HTML 복사 기능 구현 - iframe 내부에서 실행할 HTML 코드
def get_copy_button_html(text, button_text="📋 복사"):
    # HTML과 JavaScript 코드를 base64로 인코딩하여 data URL로 사용
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Copy to Clipboard</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                margin: 0;
                padding: 0;
                display: flex;
                align-items: center;
                justify-content: center;
                height: 40px;
                width: 100%;
            }}
            button {{
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 12px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 14px;
                margin: 4px 2px;
                cursor: pointer;
                border-radius: 4px;
                transition: all 0.3s;
                width: 100%;
            }}
            button:hover {{
                background-color: #45a049;
            }}
            .success {{
                background-color: #2196F3;
            }}
        </style>
    </head>
    <body>
        <textarea id="textToCopy" style="position: absolute; left: -9999px;">{text}</textarea>
        <button id="copyButton" onclick="copyToClipboard()">{button_text}</button>
        
        <script>
            function copyToClipboard() {{
                const textToCopy = document.getElementById("textToCopy");
                textToCopy.select();
                document.execCommand("copy");
                
                const copyButton = document.getElementById("copyButton");
                const originalText = copyButton.textContent;
                
                copyButton.textContent = "✓ 복사됨";
                copyButton.classList.add("success");
                
                setTimeout(function() {{
                    copyButton.textContent = originalText;
                    copyButton.classList.remove("success");
                }}, 2000);
            }}
        </script>
    </body>
    </html>
    """
    
    # base64로 인코딩 (UTF-8)
    encoded_html = base64.b64encode(html_code.encode('utf-8')).decode('utf-8')
    
    # iframe 사용하여 HTML 데이터 URL 불러오기
    return f'<iframe src="data:text/html;base64,{encoded_html}" height="50" width="100%" frameBorder="0" scrolling="no"></iframe>'

# CSS 스타일 적용 (줄간격은 기본값 유지)
st.markdown("""
<style>
    .main-header {
        font-size: 2.2em;
        font-weight: bold;
        margin-bottom: 0.8em;
        text-align: center;
        color: #1E88E5;
        padding: 0.5em 0;
    }
    .section-header {
        font-size: 1.2em;
        font-weight: bold;
        margin-top: 1em;
        margin-bottom: 0.5em;
        padding-top: 0.5em;
        border-top: 1px solid #eee;
    }
    .copy-success {
        color: #28a745;
        font-weight: bold;
    }
    .prompt-textarea {
        font-family: monospace;
    }
    .card {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 1em;
        margin-bottom: 0.8em;
    }
    .card-header {
        font-weight: bold;
        font-size: 1.1em;
        margin-bottom: 0.5em;
    }
    .footer {
        text-align: center;
        margin-top: 1.5em;
        font-size: 0.8em;
        color: #6c757d;
    }
    /* 사용법 안내 스타일 */
    .usage-guide {
        border-left: 5px solid #2196F3;
        padding: 0.8em;
        margin-bottom: 1.5em;
        border-radius: 0 4px 4px 0;
        border: 1px solid #2196F3;
        border-left-width: 5px;
    }
    .usage-guide h3 {
        margin-top: 0;
        color: #0c63e4;
        font-size: 1em;
    }
    .usage-guide ol {
        margin-bottom: 0;
        padding-left: 1.5em;
    }
    .usage-guide li {
        margin-bottom: 0.2em;
    }
    /* 모바일 최적화 스타일 */
    .stButton>button {
        width: 100%;
    }
    .stTextInput>div>div>input {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# 헤더
st.markdown("<div class='main-header'>뉴스 요약 프롬프트 생성기</div>", unsafe_allow_html=True)

# 사용법 안내 추가
st.markdown("""
<div class="usage-guide">
    <h3>🔍 사용 방법</h3>
    <ol>
        <li>검색주제 등 필요사항을 입력하고 프롬프트를 생성합니다.</li>
        <li>생성한 프롬프트를 생성형 AI에 넣고 실행합니다.</li>
        <li>실행된 결과를 복사해서 JSON 입력창에 넣습니다.</li>
        <li>결과를 생성하고 SNS, 스프레드 시트에 저장하면 됩니다.</li>
    </ol>
</div>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if 'parsed_data' not in st.session_state:
    st.session_state.parsed_data = []
    
if 'copy_status' not in st.session_state:
    st.session_state.copy_status = ""

# 샘플 데이터
sample_data = [
    {
        "title": "금융당국 보험개혁종합방안 5대 전략, 74개 과제 추진",
        "link": "https://www.intn.co.kr/news/articleView.html?idxno=2042335",
        "media": "일간NTN",
        "pubDate": "2025-03-18",
        "summary": "금융당국은 보험산업의 신뢰회복과 혁신을 위해 5대 전략과 74개 과제를 담은 보험개혁종합방안을 발표했습니다. 주요 내용으로는 소비자 중심 제도 개혁, 노후지원 5종 세트 도입, 판매채널의 책임 강화, 보험사의 장기적 경영문화 구축, 인구·기술·기후 변화에 대응하는 성장동력 마련 등이 포함되어 있습니다.",
        "one_sentence_summary": "금융당국이 보험산업의 신뢰회복과 혁신을 위한 5대 전략과 74개 과제를 담은 보험개혁종합방안을 발표했습니다."
    },
    {
        "title": "금융당국, 보험개혁 본격 시동…보험료 절감, 보장기간 확대 등",
        "link": "https://www.korea.kr/news/policyNewsView.do?newsId=148940674",
        "media": "정책브리핑",
        "pubDate": "2025-03-18",
        "summary": "금융위원회는 보험산업이 국민의 든든한 동반자로 발돋움할 수 있도록 5대 전략과 74개 과제를 담은 '보험개혁종합방안'을 발표했습니다. 주요 내용으로는 사망보험금 유동화, 고령자 보험계약대출 우대금리 제공, 고령·유병력자 실손보험 가입 및 보장 연령 확대 등이 포함되어 있습니다.",
        "one_sentence_summary": "금융위원회가 보험산업의 신뢰회복과 혁신을 위한 5대 전략과 74개 과제를 담은 '보험개혁종합방안'을 발표했습니다."
    }
]

# 1. 프롬프트 입력 섹션
st.markdown("<div class='section-header'>1. 프롬프트 입력 사항</div>", unsafe_allow_html=True)

# 주제 입력
topic = st.text_input("주제", value="" if not st.session_state.parsed_data else st.session_state.parsed_data[0]["title"].split(',')[0])

# 날짜 선택
today = date.today()
default_date = today.strftime("%Y-%m-%d")
if st.session_state.parsed_data:
    if "pubDate" in st.session_state.parsed_data[0]:
        pub_date = st.session_state.parsed_data[0]["pubDate"]
        if pub_date:
            default_date = pub_date
prompt_date = st.date_input("발표 날짜", value=datetime.datetime.strptime(default_date, "%Y-%m-%d"))

# 기사 수 선택
count = st.number_input("찾을 기사 수", min_value=1, max_value=10, value=len(st.session_state.parsed_data) if st.session_state.parsed_data else 3)

# 주제 분야
field = st.text_input("주제 분야", value="금융위원회와 금융감독원", help="예: 금융위원회와 금융감독원, 국방부와 방위사업청")

# 관련 분야 상세
sector = st.text_input("관련 분야 상세", value="금융 정책", help="예: 금융 정책, 방위산업")

# 미디어 유형
media = st.text_input("미디어 유형", value="중앙언론사 및 경제전문매체", help="예: 중앙언론사 및 경제전문매체, 국방/군사 전문매체")

# 예시 연도
year = st.text_input("예시 연도", value="2025", help="날짜 예시에 사용될 연도")

# 프롬프트 생성 함수
def generate_prompt(data, user_inputs):
    if not data:
        return ""
    
    # 주제와 날짜 추출 (첫 번째 항목 기준)
    topic = user_inputs["topic"] or data[0]["title"].split(',')[0]
    date_str = user_inputs["date"]
    count = user_inputs["count"]
    field = user_inputs["field"]
    sector = user_inputs["sector"]
    media = user_inputs["media"]
    year = user_inputs["year"]
    
    # 프롬프트 템플릿
    prompt = f"""다음은 대한민국 {field}의 주요 {sector} 관련 보도자료, 입법예고 등 입니다. 관련된 최근 뉴스 기사를 {count}개 찾아주세요: "{topic}"

보도자료 발표날짜: {date_str}
검색 기준 날짜: {date_str}
검색 범위: 최근 1개월 이내
중요도: 높음 ({sector} 관련)
- 제시된 제목과 유사도 높으면서도 다양한 관점이 제시될 수 있는 기사로 검색
- 한국에서 주목도가 높은 {media} 중심의 기사를 검색

각 기사에 대해 다음 정보를 제공해주세요:
- 제목 (title): 정확한 기사 제목
- 언론사 (media): 언론사 이름
- 발행일 (pubDate): 반드시 "YYYY-MM-DD" 형식으로 작성 (예: "{year}-03-19")
- 링크 (link): 기사 원문 URL
- 요약 (summary): 3-4문장으로 기사 내용 요약
- 한 문장 요약 (one_sentence_summary): 핵심 내용을 한 문장으로 요약
- 코드박스에 넣어서 반환

반드시 다음과 같은 JSON 형식으로 응답해주세요:
[
  {{
    "title": "기사 제목",
    "link": "https://example.com/article1",
    "media": "언론사명",
    "pubDate": "{year}-03-19",
    "summary": "기사 내용 요약 (3-4문장)",
    "one_sentence_summary": "기사 내용을 한 문장으로 요약"
  }},
  ...
]

JSON 형식이 정확해야 시스템에서 처리할 수 있습니다. 각 필드명과 형식을 정확히 지켜주세요.
특히 날짜(pubDate) 형식은 반드시 YYYY-MM-DD 형식이어야 합니다."""
    
    return prompt

# 2. 프롬프트 생성 섹션
st.markdown("<div class='section-header'>2. 프롬프트 생성</div>", unsafe_allow_html=True)

# 프롬프트 생성 버튼
if st.button("프롬프트 생성", key="generate_prompt"):
    if 'parsed_data' in st.session_state and len(st.session_state.parsed_data) > 0:
        user_inputs = {
            "topic": topic,
            "date": prompt_date.strftime("%Y-%m-%d"),
            "count": count,
            "field": field,
            "sector": sector,
            "media": media,
            "year": year
        }
        
        prompt = generate_prompt(st.session_state.parsed_data, user_inputs)
        st.session_state.prompt = prompt
    else:
        # 샘플 데이터 사용
        user_inputs = {
            "topic": topic,
            "date": prompt_date.strftime("%Y-%m-%d"),
            "count": count,
            "field": field,
            "sector": sector,
            "media": media,
            "year": year
        }
        
        prompt = generate_prompt(sample_data, user_inputs)
        st.session_state.prompt = prompt

# 프롬프트 표시 및 복사 기능
if 'prompt' in st.session_state:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-header'>생성된 프롬프트</div>", unsafe_allow_html=True)
    st.text_area("", st.session_state.prompt, height=300, key="prompt_text")
    
    # 복사 버튼을 iframe 내에 구현
    st.markdown(get_copy_button_html(st.session_state.prompt, "📋 프롬프트 복사"), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# 3. JSON 입력 섹션
st.markdown("<div class='section-header'>3. 결과(JSON형식) 입력 및 생성</div>", unsafe_allow_html=True)

# 기본 샘플 데이터 제공
default_json = json.dumps(sample_data, indent=2, ensure_ascii=False)
st.markdown("아래 항목은 샘플입니다. **전체선택+삭제** 후, 생성형 AI에서 가져온 JSON 데이터를 붙여넣으세요.", unsafe_allow_html=True)
st.markdown("입력후 아래 버튼을 눌러야 결과를 확인할 수 있습니다.", unsafe_allow_html=True)
json_input = st.text_area("", value=default_json, height=300)
st.markdown("</div>", unsafe_allow_html=True)

# JSON 파싱 버튼
if st.button("결과 생성", key="parse_json"):
    try:
        parsed_data = json.loads(json_input)
        if isinstance(parsed_data, list) and len(parsed_data) > 0:
            st.session_state.parsed_data = parsed_data
            st.success("(결과(JSON) 파싱 성공!")
        else:
            st.error("유효한 JSON 배열이 아닙니다.")
    except Exception as e:
        st.error(f"JSON 파싱 오류: {str(e)}")

# 4. 결과 표시 섹션
if st.session_state.parsed_data:
    st.markdown("<div class='section-header'>4. 결과 보기</div>", unsafe_allow_html=True)
    
    # SNS용 및 구글시트용 변환 기능    
    # SNS용 복사 포맷 함수
    def format_for_sns(data):
        result = ""
        for index, item in enumerate(data):
            result += f"{index + 1}. {item.get('title', '제목 없음')}\n"
            result += f"{item.get('media', '-')} / {item.get('pubDate', '-')}\n"
            if item.get('link'):
                result += f"🔗 {item.get('link')}\n"
            result += f"🔹 {item.get('one_sentence_summary', '-')}\n"
            result += "\n"
        return result
    
    # 구글시트용 복사 포맷 함수
    def format_for_sheet(data):
        # DataFrame 생성 (일련번호 컬럼 제거)
        df = pd.DataFrame([
            {
                '제목': item.get('title', '제목 없음'),
                '언론사': item.get('media', '-'),
                '발행일': item.get('pubDate', '-'),
                '링크': item.get('link', '-'),
                '한 문장 요약': item.get('one_sentence_summary', '-'),
                '요약': item.get('summary', '-')
            } for item in data
        ])
        return df
    
    # 변환 버튼들
    col1, col2 = st.columns(2)
    
    # 버튼 컨테이너 및 버튼 자체의 CSS 수정 (텍스트 길이에 영향받지 않고 50% 영역 채우기)
    st.markdown("""
    <style>
    /* 각 컬럼을 50% 영역으로 지정 */
    div[data-testid="column"] {
        margin: 0 !important;
        padding: 0 !important;
        flex: 1 1 50% !important;
        max-width: 50% !important;
        min-width: 0 !important;
    }
    /* 버튼 컨테이너의 여백 제거 */
    div[data-testid="stButton"] {
        width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    /* 버튼 자체: 고정 최소 높이, 줄바꿈 방지 및 말줄임 처리 */
    div[data-testid="stButton"] button {
        width: 100% !important;
        min-height: 50px !important;
        white-space: nowrap !important;
        overflow: hidden;
        text-overflow: ellipsis;
        box-sizing: border-box;
        margin: 0 !important;
    }
    /* SNS 버튼 스타일 */
    div[data-testid="stButton"]:first-child button {
        background-color: #FFFDE7 !important;
        color: #333333 !important;
    }
    /* 구글시트 버튼 스타일 */
    div[data-testid="stButton"]:nth-child(2) button {
        background-color: #FFF3E0 !important;
        color: #333333 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    with col1:
        if st.button("SNS에 공유할 수 있는 형식으로 변환", key="format_sns", 
                    help="클릭하면 SNS에 게시할 수 있는 형식으로 변환합니다"):
            st.session_state.sns_format = format_for_sns(st.session_state.parsed_data)
    
    with col2:
        if st.button("엑셀 또는 구글 스프레드시트 형식으로 변환", key="format_sheet", 
                   help="클릭하면 스프레드시트에 붙여넣을 수 있는 형식으로 변환합니다"):
            st.session_state.sheet_format = format_for_sheet(st.session_state.parsed_data)
    
    # SNS 형식 표시 및 복사 기능
    if 'sns_format' in st.session_state:
        st.text_area("", st.session_state.sns_format, height=200, key="sns_text")
        
        # SNS 포맷 복사 버튼
        st.markdown(get_copy_button_html(st.session_state.sns_format, "📋 SNS 포맷 복사"), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 구글시트 형식 표시 및 복사 기능
    if 'sheet_format' in st.session_state:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-header'>구글시트용 포맷</div>", unsafe_allow_html=True)
        st.dataframe(st.session_state.sheet_format)
        
        # CSV로 변환하여 다운로드 버튼 제공
        csv = st.session_state.sheet_format.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="CSV 다운로드",
            data=csv,
            file_name="news_summary.csv",
            mime="text/csv",
        )
        
        # 구글시트 포맷을 CSV 문자열로 복사하기 위한 버튼
        sheet_csv = st.session_state.sheet_format.to_csv(index=False)
        st.markdown(get_copy_button_html(sheet_csv, "📋 CSV 데이터 복사"), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 토글 제목 스타일 적용
    st.markdown("""
    <style>
    div.st-emotion-cache-1l269u5 > label {
        font-size: 1.2em !important;
        font-weight: bold !important;
    }
    div.st-emotion-cache-1nzw9oi p {
        font-size: 0.85em !important;
    }
    
    /* 폴백 스타일 - 배포 환경에서 클래스가 다를 경우 대비 */
    .streamlit-expanderHeader {
        font-size: 1.2em !important;
        font-weight: bold !important;
    }
    .streamlit-expanderContent {
        font-size: 0.85em !important;
    }
    
    /* details/summary 기반 선택자 - 일부 환경에서 작동 */
    details > summary {
        font-size: 1.2em !important;
        font-weight: bold !important;
    }
    details > div {
        font-size: 0.85em !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    for i, item in enumerate(st.session_state.parsed_data):
        expander_title = f"{i+1}. {item.get('title', '제목 없음')}"
        with st.expander(expander_title, expanded=i==0):
            st.markdown(f"**언론사:** {item.get('media', '-')} | **발행일:** {item.get('pubDate', '-')}")
            st.markdown(f"**링크:** [{item.get('link', '-')}]({item.get('link', '#')})")
            st.markdown(f"**한 문장 요약:** {item.get('one_sentence_summary', '-')}")
            st.markdown(f"**요약:** {item.get('summary', '-')}")
            
            # 개별 뉴스 항목 복사 버튼
            item_json = json.dumps(item, ensure_ascii=False, indent=2)
            st.markdown(get_copy_button_html(item_json, "📋 이 항목 복사"), unsafe_allow_html=True)

# 푸터
st.markdown("""
<div class="footer">
    © 2025 뉴스 요약 프롬프트 생성기 - Made by GQ 💡
</div>
""", unsafe_allow_html=True)
