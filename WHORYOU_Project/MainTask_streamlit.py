import os
import time
import streamlit as st
from modules.Flair import KeywordExtractor
from modules.RAG_generate import RagGenerator
from modules.SubTask_chatbot import get_text, get_text_chunks, get_vectorstore, get_conversation_chain
from modules.SubTask_subtitle import generate_subtitle_with_llama
from modules.motivational_quotes import get_motivational_quotes


# API 키 직접 지정
openai_api_key = os.getenv("OPENAI_API_KEY")  # .env 파일이나 시스템 환경 변수에서 키를 불러옴


# GPT 프롬프트 템플릿
def message_template(keyword, job_field, doc):
    prompt = [ {"role": "system",
              "content": f"""당신은 {job_field}와 {keyword} 안에 있는 각 키워드, 각 키워드와 관련된 자료 {doc}를 바탕으로,
                             각 키워드별로 비유 문장을 생성하는 전문가입니다.
                             {keyword}를 강조하는 문장을 비유 표현을 사용하여 생성해주세요.
                             {keyword}로 1개씩 총 5개의 문장을 생성해주세요."""},
              {"role": "user", "content": f"{job_field} 직무와 {doc}을 바탕으로 비유 문장을 생성해주세요: "},
              {"role": "user", "content": f"각 {keyword}가 포함된 자기소개 문장을 비유 표현을 사용하여 '저의 {keyword} 역량은 ~입니다.' 형식으로 작성해 주세요."}
            ]
    return prompt


def main():
    # 페이지 설정
    st.set_page_config(page_title="Text2Metaphor", page_icon=":books:")
    # 헤더 표시
    st.markdown("<h1 style='font-size: 120px;'>WHORYOU?</h1>", unsafe_allow_html= True)
    st.markdown("<h2 style='font-size: 40px;'>ALL IN ONE - 취업 준비 솔루션</h2>", unsafe_allow_html= True)
    
    # 각 직무군에 대한 로컬 경로 사전 설정
    base_path = os.path.abspath(".") # 현재 디렉토리 기준으로 절대 경로
    job_paths = {
        "ICT": os.path.join(base_path, "Job_vectorDB", "ICT"),
        "디자인": os.path.join(base_path, "Job_vectorDB", "design"),
    }

    # 기능 선택
    options = st.multiselect("원하는 기능을 모두 선택하세요", ["비유적 표현 생성기", "소제목 생성기","챗봇"], default=st.session_state.selected_options)
    st.session_state.selected_options = options

    # 기능 선택이 되지 않았을 때, 기본값 설정
    if 'selected_options' not in st.session_state:
        st.session_state.selected_options = []
            # URL을 사용하여 배경 이미지 설정
        image_url = "https://i.imgur.com/jgazRgN.png"  # 사용하고자 하는 이미지의 URL로 변경
        st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("{image_url}");
            background-size: 30%;  /* 이미지 크기를 50%로 조정 */
            background-position: center 80%; 
            background-repeat: no-repeat;
        }}
        </style>
        """,
        unsafe_allow_html=True
        )

    # [Service1]
    if "비유적 표현 생성기" in st.session_state.selected_options:
        st.write("")
        st.write("")
        st.subheader("Generator_자기소개 : 비유적 표현 생성기.")

        # [Service1] 1. 직무 입력 받기
        job_field = st.sidebar.selectbox("직무군 선택", list(job_paths.keys()))
        
        # [Service1] 2. 핵심역량, 자기소개서 입력 받기
        if job_field:
            core_competency = st.text_input("핵심역량을 입력하세요", "예: 커뮤니케이션, 리더십 등")
            introduction_text = st.text_area("자기소개서 내용을 입력하세요", "여기에 자기소개서 내용을 입력하세요.", height=250)
            
            # [Service1] 3. 비유적 표현 생성 시작
            if st.button("비유적 표현 생성"):
                message_placeholder = st.empty()

                # 로딩하는 동안 격려 문구 표시  # from motivational_quotes import get_motivational_quotes
                quotes = get_motivational_quotes()
                for quote in quotes:
                    message_placeholder.text(quote)
                    time.sleep(3)  # 3초 동안 해당 문구 표시
                
                # [Service1] 3. 키워드 추출 및 문서 생성 코드
                '''3-1. 키워드 추출''' # from Flair import KeywordExtractor
                keyword_extractor = KeywordExtractor()
                keywords = keyword_extractor.extract_keywords(introduction_text)
                if keywords:  # 키워드가 있는지 확인
                    top_related_keywords = keyword_extractor.final_top5_keywords(core_competency, keywords)
                else:
                    top_related_keywords = []
                    st.write("추출된 키워드가 없습니다.")
                
                '''3-2. RAG 문서 생성''' # from RAG_generate import RagGenerator
                # rag_generator = RagGenerator(api_key, job_field, vectordb_path)
                # vectordb_path 경로 설정 (Job_vectorDB 폴더)
                vectordb_path = job_paths[job_field]
                openai_api_key = "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"  
                rag_generator = RagGenerator(openai_api_key, job_field, vectordb_path)

                # 로딩 문구 지우기
                message_placeholder.empty()
                
                '''3-3. 비유적 표현 생성 및 출력'''
                for keyword, _ in top_related_keywords:
                    doc = rag_generator.retrieve_documents(keyword)
                    prompt = message_template(keyword, job_field, doc)
                    sentence = rag_generator.generate_sentence(prompt)
    
                    # 강조된 박스 형태로 출력
                    st.markdown(
                        f"""
                        <div style="
                            border: 1px solid #4CAF50;
                            padding: 10px;
                            border-radius: 5px;
                            background-color: #f9f9f9;
                            margin-top: 10px;">
                            <strong style="color: #388E3C;">{keyword}:</strong> {sentence}
                            </div>
                            """,
                        unsafe_allow_html=True
                                )
        # 컴포넌트 간 간격 추가
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")

    
    # [Service2]
    if "소제목 생성기" in options:
        st.write("")
        st.write("")
        st.subheader("Generator_자소서 : 소제목 생성")
        user_input = st.text_area("자기소개서 입력:", "여기에 자기소개서 내용을 입력하세요.")
        
        if st.button("소제목 생성"):
            if user_input:
                message_placeholder = st.empty()
                # 로딩하는 동안 격려 문구 표시  # from motivational_quotes import get_motivational_quotes
                quotes = get_motivational_quotes()
                try:
                    for quote in quotes:
                        message_placeholder.text(quote)
                        time.sleep(3)  # 3초 동안 해당 문구 표시
                        
                        # Llama 모델을 사용하여 소제목 생성
                        subtitle = generate_subtitle_with_llama(user_input)
                        st.success("소제목 생성 완료!")
                finally:
                    # 완료 시 문구를 지우기
                    message_placeholder.empty()
                
                st.markdown( f"""
                            <div style="
                                border: 1px solid #ccc;
                                padding: 10px;
                                border-radius: 5px;
                                background-color: #f9f9f9;
                                margin-top: 10px;">
                                <strong>생성된 소제목:<br/></strong> {subtitle}
                            </div>
                            """,
                            unsafe_allow_html=True )
            else:
                st.warning("자기소개서 내용을 입력하세요.")

        # 컴포넌트 간 간격 추가
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
    
    
    # [Service3]
    if "챗봇" in options:
        st.write("")
        st.write("")
        st.subheader("Chatbot_Helper :  기업에 대해 궁금해?")
        st.markdown("<h1 style='font-size: 15px;'>기업 맞춤 정보 제공</h1>", unsafe_allow_html= True)
        st.markdown("<h2 style='font-size: 15px;'>기업 관련 문서 (pdf, dox 등)을 입력해서, 원하는 정보만 받아보세요! </h2>", unsafe_allow_html= True)
        st.markdown("<h3 style='font-size: 15px;'>문서를 upload하면 Chatbot이 나타납니다 ^^ </h3>", unsafe_allow_html= True)

        # Streamlit의 상태 관리 (세션 초기화)
        if "conversation" not in st.session_state:
            st.session_state.conversation = None
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = None
        if "processComplete" not in st.session_state:
            st.session_state.processComplete = None

        # 파일 업로드 섹션 (사이드바에서 파일 업로드)
        with st.sidebar:
            uploaded_files = st.file_uploader("파일 업로드", type=['pdf', 'docx'], accept_multiple_files=True)
            process = st.button("Process")

        if process:
            # 파일 처리
            files_text = get_text(uploaded_files)
            text_chunks = get_text_chunks(files_text)
            vetorestore = get_vectorstore(text_chunks)
            
            # 대화 체인 초기화
            st.session_state.conversation = get_conversation_chain(vetorestore, openai_api_key)
            st.session_state.processComplete = True

        # 챗봇이 초기화된 경우 대화 기능 활성화
        if st.session_state.processComplete:
            if 'messages' not in st.session_state:
                st.session_state['messages'] = [{"role": "assistant", "content": "기업과 직무 정보를 입력하고, 면접 질문을 생성해보세요!"}]

            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
            
            # 사용자 입력을 받는 입력창
            if query := st.chat_input("질문을 입력해주세요."):
                # 사용자 메시지를 대화 이력에 추가
                st.session_state.messages.append({"role": "user", "content": query})
                with st.chat_message("user"):  
                    st.markdown(query)
                
                # 응답 처리
                with st.chat_message("assistant"):
                    chain = st.session_state.conversation
                    with st.spinner("Thinking..."):
                        result = chain({"question": query})
                        response = result['answer']
                        source_documents = result['source_documents']

                        st.markdown(response)
                        with st.expander("참고 문서 확인"):
                            for doc in source_documents:
                                st.markdown(doc.metadata['source'], help=doc.page_content)
                
                # 응답을 대화 이력에 추가
                st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == '__main__':
    # !pip install llama-cpp-python
    # !pip install loguru
    # !pip install transformers
    # !pip install streamlit
    # !pip install flair konlpy
    # !pip install pypdf
    # !pip install langchain-chroma
    # !pip install langchain-community
    # !pip install tiktoken
    # !pip install openai
    main() 
    # python -m venv 2024_dna_conference
    # 2024_dna_conference\Scripts\activate
    # pip install -r requirements.txt


