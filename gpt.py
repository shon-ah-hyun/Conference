import os
import streamlit as st
import tiktoken
from loguru import logger

from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI

from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import Docx2txtLoader
from langchain.document_loaders import UnstructuredPowerPointLoader

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings

from langchain.memory import ConversationBufferMemory
from langchain.vectorstores import FAISS

from langchain.callbacks import get_openai_callback
from langchain.memory import StreamlitChatMessageHistory
from llama_cpp import Llama

llm = Llama.from_pretrained(
    repo_id="Kimsangwook/llama3_bllossom_gguf_q5",
    filename="llama3_bllossom_gguf_q5.gguf",
)

# API 키 직접 지정
openai_api_key = "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"  # 직접 지정한 API 키 사용

# DB 처리를 위한 사전 코드 정의
def tiktoken_len(text):
    tokenizer = tiktoken.get_encoding("cl100k_base")
    tokens = tokenizer.encode(text)
    return len(tokens)

def get_text(docs):
    doc_list = []
    
    for doc in docs:
        file_name = doc.name
        with open(file_name, "wb") as file:
            file.write(doc.getvalue())
            logger.info(f"Uploaded {file_name}")
        if '.pdf' in doc.name:
            loader = PyPDFLoader(file_name)
            documents = loader.load_and_split()
        elif '.docx' in doc.name:
            loader = Docx2txtLoader(file_name)
            documents = loader.load_and_split()
        elif '.pptx' in doc.name:
            loader = UnstructuredPowerPointLoader(file_name)
            documents = loader.load_and_split()

        doc_list.extend(documents)
    return doc_list

# local에서 불러오는 코드
def load_local_documents(folder_path):
    doc_list = []
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if file_name.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
        elif file_name.endswith(".docx"):
            loader = Docx2txtLoader(file_path)
        elif file_name.endswith(".pptx"):
            loader = UnstructuredPowerPointLoader(file_path)
        else:
            continue
        documents = loader.load_and_split()
        doc_list.extend(documents)
        logger.info(f"Loaded {file_name}")
    return doc_list

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=900,
        chunk_overlap=100,
        length_function=tiktoken_len
    )
    chunks = text_splitter.split_documents(text)
    return chunks

def get_vectorstore(text_chunks):
    embeddings = HuggingFaceEmbeddings(
        model_name="jhgan/ko-sroberta-multitask",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )  
    vectordb = FAISS.from_documents(text_chunks, embeddings)
    return vectordb

def get_conversation_chain(vetorestore, openai_api_key):
    llm = ChatOpenAI(openai_api_key=openai_api_key, model_name='gpt-3.5-turbo', temperature=0)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm, 
        chain_type="stuff", 
        retriever=vetorestore.as_retriever(search_type='mmr', vervose=True), 
        memory=ConversationBufferMemory(memory_key='chat_history', return_messages=True, output_key='answer'),
        get_chat_history=lambda h: h,
        return_source_documents=True,
        verbose=True
    )
    return conversation_chain

def main():
    st.set_page_config(page_title="Text2Metaphor", page_icon=":books:")
    st.title("Text2Metaphor: 자소서와 면접을 위한 인상적인 표현 생성기")
    # 각 직무군에 대한 로컬 경로 사전 설정
    job_paths = {
        "ICT": "C:\김상욱\conference\streamlit\ICT",
        "디자인": "C:\김상욱\conference\streamlit\디자인",
        "마케팅": "path/to/marketing_documents",
        "개발": "path/to/dev_documents",
        "운영": "path/to/operations_documents",
        "영업": "path/to/sales_documents",
        "인사": "path/to/hr_documents",
    }
    options = st.multiselect("원하는 기능을 선택하세요", ["비유적 표현 생성기", "소제목 생성기", "챗봇"])

    if "비유적 표현 생성기" in options:
        st.subheader("Generator_자기소개 : 비유적 표현 생성기.")
        selected_job = st.sidebar.selectbox("직무군 선택", list(job_paths.keys()))

        if selected_job:
            folder_path = job_paths[selected_job]
            documents = load_local_documents(folder_path)

            text_chunks = get_text_chunks(documents)
            vetorestore = get_vectorstore(text_chunks)
            conversation_chain = get_conversation_chain(vetorestore, openai_api_key)

    if "소제목 생성기" in options:
        st.subheader("Generator_자소서 : 소제목 생성")

    if "챗봇" in options:
        st.subheader("Chatbot_Helper : 회사에 대해 궁금해?")

        if "conversation" not in st.session_state:
            st.session_state.conversation = None
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = None
        if "processComplete" not in st.session_state:
            st.session_state.processComplete = None

        with st.sidebar:
            uploaded_files = st.file_uploader("파일 업로드", type=['pdf', 'docx'], accept_multiple_files=True)
            process = st.button("Process")
        
        if process:
            files_text = get_text(uploaded_files)
            text_chunks = get_text_chunks(files_text)
            vetorestore = get_vectorstore(text_chunks)

            st.session_state.conversation = get_conversation_chain(vetorestore, openai_api_key)
            st.session_state.processComplete = True

        if st.session_state.processComplete:
            if 'messages' not in st.session_state:
                st.session_state['messages'] = [{"role": "assistant", "content": "기업과 직무 정보를 입력하고, 면접 질문을 생성해보세요!"}]

            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            if query := st.chat_input("질문을 입력해주세요."):
                st.session_state.messages.append({"role": "user", "content": query})
                with st.chat_message("user"):
                    st.markdown(query)

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

                st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == '__main__':
    main()
