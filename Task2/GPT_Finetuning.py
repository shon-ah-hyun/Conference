import openai
# 환경 변수에서 API 키를 불러오기
openai_api_key = "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"
# OpenAI 클라이언트 생성
client = OpenAI(
  api_key=openai_api_key  # os.environ 대신 os.getenv로 불러온 키 사용
)
# 모델 생성 함수 정의
def finetune_generate_with_category(message, job_field, previous_response, temperature, top_p, frequency_penalty, presence_penalty):

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # 사용하는 모델 이름
        messages=message,
        temperature=temperature,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        max_tokens=100
    )
    return response.choices[0].message['content']
