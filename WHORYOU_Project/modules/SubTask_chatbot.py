import os
from langchain.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.document_loaders import PyPDFLoader, Docx2txtLoader, UnstructuredPowerPointLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from loguru import logger
import tiktoken


# (1) tiktoken length function
def tiktoken_len(text):
    tokenizer = tiktoken.get_encoding("cl100k_base")
    tokens = tokenizer.encode(text)
    return len(tokens)


# (2) Extract text from uploaded documents
def get_text(docs):
    """
    업로드된 문서에서 텍스트를 추출합니다.
    """
    doc_list = []
    for doc in docs:
        file_name = doc.name
        with open(file_name, "wb") as file:
            file.write(doc.getvalue())
            logger.info(f"Uploaded {file_name}")
        if '.pdf' in doc.name:
            loader = PyPDFLoader(file_name)
        elif '.docx' in doc.name:
            loader = Docx2txtLoader(file_name)
        elif '.pptx' in doc.name:
            loader = UnstructuredPowerPointLoader(file_name)
        else:
            logger.warning(f"Unsupported file format: {doc.name}")
            continue

        documents = loader.load_and_split()
        doc_list.extend(documents)
    return doc_list


# (3) Chunk text for processing
def get_text_chunks(text_docs):
    """
    문서를 작은 텍스트 청크로 나눕니다.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=900,
        chunk_overlap=100,
        length_function=tiktoken_len
    )
    chunks = text_splitter.split_documents(text_docs)
    return chunks


# (4) Create a vectorstore
def get_vectorstore(text_chunks):
    """
    텍스트 청크에서 벡터 스토어 생성합니다.
    """
    embeddings = HuggingFaceEmbeddings(
        model_name="jhgan/ko-sroberta-multitask",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )  
    vectordb = FAISS.from_documents(text_chunks, embeddings)
    return vectordb


# (5) Generate conversation chain
def get_conversation_chain(vectorstore, openai_api_key):
    """
    Conversational Chain 생성
    """
    llm = ChatOpenAI(openai_api_key=openai_api_key, model_name='gpt-3.5-turbo', temperature=0)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm, 
        chain_type="stuff", 
        retriever=vectorstore.as_retriever(search_type='mmr'), 
        memory=ConversationBufferMemory(memory_key='chat_history', return_messages=True, output_key='answer'),
        get_chat_history=lambda h: h,
        return_source_documents=True,
        verbose=True
    )
    return conversation_chain
