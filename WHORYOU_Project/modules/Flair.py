from konlpy.tag import Okt
from flair.embeddings import TransformerDocumentEmbeddings
from flair.data import Sentence
import torch

class KeywordExtractor:
    def __init__(self):
        # Okt 형태소 분석기 로드
        self.okt = Okt()
        # 불용어 리스트 정의
        self.stop_words = [
        '이', '그', '저', '그리고', '하지만', '그래서', '또는', '즉', '때문에', '그러나', '그러므로',
        '게다가', '및', '의', '가', '을', '를', '에', '과', '도', '에서', '하다', '이다',
        '않다', '없다', '않고', '있는', '같이', '같은', '한', '안', '중', '더', '너무', '잘', '다',
        '보다', '합니다', '하세요', '합니다', '그런', '위해', '어떻게', '무엇', '나', '우리', '저희',
        '할', '하여', '하면서', '해야', '하고', '되다', '된다', '되는', '된', '될', '하게', '한테',
        '그렇다', '있습니다', '있어', '있다', '였습니다', '이었다', '이러한', '또', '위', '아래',
        '여기', '저기', '거기', '처럼', '이외', '뿐', '각', '모든', '모두', '통해', '뒤', '앞',
        '같다', '라는', '하는', '이런', '이번', '전', '후', '및', '안', '밖', '의해', '만', '까지',
        '무슨', '좀', '좀더', '할지', '아닌'
        ]
        # Flair Transformer 임베딩 모델 로드 (BERT 모델 사용)
        self.embedding_model = TransformerDocumentEmbeddings('bert-base-multilingual-cased')

    def preprocess_text(self, text):
        """전처리"""
        nouns = self.okt.nouns(text)  # 명사 추출
        filtered_nouns = [word for word in nouns if word not in self.stop_words]  # 불용어 제거
        return ' '.join(filtered_nouns)


    def embed_text(self, text):
        """문장을 Flair의 Sentence 객체로 변환 후 임베딩"""
        sentence = Sentence(text)
        self.embedding_model.embed(sentence)
        return sentence.embedding


    def compute_similarity(self, competency_user, keywords):
        """핵심 역량 문장을 Flair Sentence로 변환하고 임베딩"""
        keyword_embedding = self.embed_text(competency_user)

        related_keywords = []
        for kw, score in keywords:
            # 추출된 키워드를 Flair Sentence로 변환하고 임베딩
            kw_embedding = self.embed_text(kw)
            # 유사도 계산 (코사인 유사도)
            similarity = torch.nn.functional.cosine_similarity(keyword_embedding, kw_embedding, dim=0)
            if similarity > 0.5:  # 유사도가 0.5 이상인 키워드만 선택
                related_keywords.append((kw, similarity.item()))

        # 유사도 기준으로 정렬
        related_keywords = sorted(related_keywords, key=lambda x: x[1], reverse=True)
        return related_keywords[:5]  # 상위 5개 추출


    def extract_keywords(self, document):
        """키워드 후보를 임의로 생성"""
        processed_text = self.preprocess_text(document)

        keywords = [(word, 0.0) for word in set(processed_text.split())]
        return keywords
    

    def final_top5_keywords(self, competency_user, keywords):
        """최종 반환 코드"""
        top_related_keywords = self.compute_similarity(competency_user, keywords)
        return top_related_keywords