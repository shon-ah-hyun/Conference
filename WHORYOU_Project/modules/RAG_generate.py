from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
import os
import re
import openai  # 수정: openai 모듈 전체를 임포트


class RagGenerator:
    def __init__(self, api_key, job_field, vectordb_path):
        # 1. OpenAI API 키 설정
        os.environ["OPENAI_API_KEY"] = api_key

        # 2. 직무 입력
        self.job_field = job_field

        # 3. 벡터 데이터베이스가 저장된 위치
        self.db_path = vectordb_path

        # 4. 벡터 데이터베이스 객체
        self.database = self._load_database()



    def _load_database(self):   # 보조 작업으로만 쓰임
        """데이터베이스에 저장된 문서들을 불러오고, 검색기 초기화""" 
        database = Chroma(persist_directory=f"{self.db_path}\{self.job_field}",   # '/content/drive/MyDrive/컨퍼런스/rag/DB/{job_field}'
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


    def generate_sentence(self, prompt):
      client = openai.OpenAI()
      """키워드를 입력 받아서, GPT로 비유 문장을 생성"""
      """개인 api로 파인튜닝 된 모델 사용함. 필요시, 해당 모델 이름 바꿀 것"""
      response = client.chat.completions.create(
          model="ft:gpt-3.5-turbo-1106:personal:1-jobinteview-finetunemodel:AIenIBIz",
          messages=prompt,
          temperature=0 )
      response_text = response.choices[0].message.content
      return response_text
