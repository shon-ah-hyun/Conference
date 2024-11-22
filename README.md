## **WHORYOU: All-in-One 취업 준비 솔루션**

### **프로젝트 개요**
WHORYOU는 취업 준비 과정에서 개인의 강점과 특성을 창의적으로 표현하고, 경쟁력을 강화하기 위해 개발된 **올인원 취업 준비 솔루션**입니다. 이 프로젝트는 다음 세 가지 주요 서비스를 제공합니다:
1. **자기소개서 기반 비유 문장 생성 서비스**
2. **자기소개서 소제목 생성 서비스**
3. **기업 관련 Q&A 챗봇 서비스**

NLP2팀은 이 프로젝트를 통해 사용자들이 자신을 효과적으로 "셀프 세일즈" 할 수 있도록 지원하며, 취업 시장에서 강렬한 인상을 남길 수 있도록 돕고자 합니다.

---

### **기능 소개**

#### 1️⃣ **비유 문장 생성 서비스**
- **키워드 추출**: Flair 프레임워크를 활용하여 자기소개서 및 사용자가 입력한 역량과 관련된 키워드를 추출합니다.
- **비유 문장 생성**: 추출된 키워드에 대해 직무별 벡터화된 데이터베이스와 GPT-3.5 Turbo 모델을 활용하여 창의적이고 전문적인 비유 문장을 생성합니다.
- **사용 기술**: 
  - Flair 기반 BERT 키워드 추출
  - GPT-3.5 Turbo 파인튜닝 모델
  - RAG(Vector DB) 활용

#### 2️⃣ **소제목 생성 서비스**
- **소제목 생성**: 자기소개서 내용을 분석하여 인상 깊은 소제목을 자동으로 생성합니다.
- **사용 모델**: 최적화된 Bllossom 모델

#### 3️⃣ **기업 관련 Q&A 챗봇**
- **PDF 문서 분석**: 사용자가 업로드한 기업 관련 PDF 문서를 분석하여 관련 정보를 추출합니다.
- **질문 답변 생성**: GPT-3.5 Turbo 모델을 활용하여 PDF 내용을 기반으로 한 정확한 답변을 제공합니다.
- **사용 기술**: RAG(Vector DB), GPT-3.5 Turbo

---

### **사용 방법**

#### 1. 설치 및 환경 설정
1. **Python 가상환경 생성 및 활성화**:
   ```bash
   python -m venv 2024_dna_conference
   source 2024_dna_conference/bin/activate  # macOS/Linux
   2024_dna_conference\Scripts\activate     # Windows
   ```

2. **필요 패키지 설치**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **OpenAI API 키 설정**:
   - `.env` 파일 생성 후, 아래와 같이 API 키 추가:
     ```
     OPENAI_API_KEY=sk-xxxxx
     ```

#### 2. 프로젝트 실행
```bash
streamlit run streamlit.py
```

#### 3. 주요 화면 및 기능 사용
- **비유적 표현 생성기**: 자기소개서와 역량 입력 후, 비유적 표현 생성 버튼 클릭
- **소제목 생성기**: 자기소개서를 입력하고 소제목 생성 버튼 클릭
- **기업 Q&A 챗봇**: 기업 관련 문서를 업로드한 후 질문 입력

---

### **프로젝트 구조**
```plaintext
project/
├── modules/                     # 주요 기능을 담고 있는 모듈 디렉토리
│   ├── Flair.py                 # [Service1] 키워드 추출 모듈
│   ├── RAG_generate.py          # [Service1] RAG 기반 문장 생성 모듈
│   ├── SubTask_subtitle.py      # [Service2] 소제목 생성 모듈
│   ├── SubTask_chatbot.py       # [Service3] Q&A 챗봇 관련 로직
│   └── motivational_quotes.py   # 격려 문구 모듈 (Streamlit 로딩 시)
├── .env                         # 환경 변수 설정 파일 (API 키 등)
├── MainTask_streamlit.py        # Streamlit 메인 애플리케이션
├── requirements.txt             # Python 패키지 목록
└── README.md                    # 프로젝트 설명 파일
```

---

### **기술 스택**
- **Python 3.9 이상**
- **Streamlit**: 사용자 인터페이스
- **LangChain**: RAG(Vector DB) 처리
- **OpenAI GPT-3.5 Turbo**: 비유 문장 및 챗봇 답변 생성
- **Flair**: 키워드 추출
- **Llama**: 소제목 생성

---

### **팀원**
- **팀장**: 손아현
- **팀원**: 김상욱, 신유인, 신지후, 황예은

---

### **특이 사항**
1. **BERT 및 Flair** 기반 키워드 추출을 통해 사용자 입력의 연관성을 최적화했습니다.
2. **RAG**로 사전 벡터화된 데이터베이스를 활용하여 비유 문장과 기업 Q&A 생성 성능을 개선했습니다.
3. **Bllossom** 모델을 최적화하여 소제목 생성 속도와 정확성을 향상시켰습니다.
