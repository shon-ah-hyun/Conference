from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
import os
import openai  # 수정: openai 모듈 전체를 임포트
import re


class RagGenerator:
    def __init__(self, api_key, job_field, db_path):
        # 1. OpenAI API 키 설정
        OPENAI_API_KEY = api_key       # openai.api_key = "your_openai_api_key"
        os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
        openai.api_key = api_key  # openai.api_key 설정
        # 2. 직무 입력
        self.job_field = job_field
        # 3. 벡터 데이터베이스가 저장된 위치
        self.db_path = db_path
        # 4. 벡터 데이터베이스 객체
        self.database = self._load_database()


# def keyword_pdf(keyword, job_field)의 코드를 "아래 2개의 함수로 쪼갬"
    def _load_database(self):   # 보조 작업으로만 쓰임
        """데이터베이스에 저장된 문서들을 불러오고, 검색기 초기화""" 
        database = Chroma(persist_directory=f"{self.db_path}/{self.job_field}",   # '/content/drive/MyDrive/컨퍼런스/rag/DB/{job_field}'
                            embedding_function=OpenAIEmbeddings())
        
        retriever = database.as_retriever(search_type="similarity", search_kwargs={"k": 3})
        return retriever


    def retrieve_documents(self, keyword):
        """주어진 키워드와 관련된 문서를 검색하고, 텍스트 형태로 반환"""
        qa_chain = RetrievalQA.from_chain_type(
            llm=ChatOpenAI(temperature=0, 
                           model="gpt-3.5-turbo"),
            chain_type="stuff",
            retriever=self.database,
            return_source_documents=True)

        result = qa_chain.invoke(keyword)
        docs = [source.page_content for source in result['source_documents']]
        doc = re.sub(r"\\n|\n|\"|○", "", str(docs))
        return doc


# def finetune_generate(job_field, keywords)의 함수 재구성
    def generate_sentence(self, message):
      client = openai.OpenAI()
      """키워드를 기반으로 비유 문장을 생성"""
      response = client.chat.completions.create(
          model="ft:gpt-3.5-turbo-1106:personal:1-jobinteview-finetunemodel:AIenIBIz",
          messages=message,
          temperature=0 )
      response_text = response.choices[0].message.content
      return response_text
