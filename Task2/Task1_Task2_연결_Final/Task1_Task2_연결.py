import os
import re

from Flair import KeywordExtractor
from RAG_generate import RagGenerator


def message_template(keyword, job_field, doc):
    return [ {"role": "system", 
              "content": f"""당신은 {job_field}와 {keyword} 안에 있는 각 키워드, 각 키워드와 관련된 자료 {doc}를 바탕으로, 
                             각 키워드별로 비유 문장을 생성하는 전문가입니다.
                             {keyword}를 강조하는 문장을 비유 표현을 사용하여 생성해주세요.
                             {keyword}로 1개씩 총 5개의 문장을 생성해주세요."""},
              {"role": "user", "content": f"{job_field} 직무와 {doc}을 바탕으로 비유 문장을 생성해주세요: "},
              {"role": "user", "content": f"각 {keyword}가 포함된 자기소개 문장을 비유 표현을 사용하여 '저의 {keyword} 역량은 ~입니다.' 형식으로 작성해 주세요."}
            ]

def main():
    # 개발자 입력
    api_key=" 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"
    db_path = "/path/to/db" #
    
    # user 입력
    job_field = input("직무를 입력하세요(e.g. 디자인, ICT): ")
    competency_user = input("자기소개서에 드러내고 싶은 역량을 작성해주세요: ")
    document = input("자기소개서 내용을 입력해주세요: ")

    # 키워드 추출
    extractor = KeywordExtractor()
    keywords = extractor.final_top5_keywords(competency_user, document)

    # RAG 문장 생성
    rag_generator = RagGenerator(api_key, job_field, db_path)
    rag_generator.generate_sentences_for_keywords(keywords, message_template)




if __name__ == "__main__":
    main()

