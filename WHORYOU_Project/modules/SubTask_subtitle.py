from llama_cpp import Llama


# 소제목 생성기에 사용될 모델
llm = Llama.from_pretrained(
    repo_id="Kimsangwook/llama3_bllossom_gguf_q5",
    filename="llama3_bllossom_gguf_q5.gguf",
)


def generate_subtitle_with_llama(text):
    """
    소제목을 생성합니다.
    """
    PROMPT = "System: 입력받은 자기소개서에 대해서 인상 깊은 소제목을 한줄로 생성해줘."
    messages = [
        {"role": "system", "content": PROMPT},
        {"role": "user", "content": text}
    ]
    
    # Llama 모델을 사용하여 소제목 생성
    response = llm.create_chat_completion(messages=messages)
    # 답변 텍스트만 추출
    answer = response['choices'][0]['message']['content']
    return answer.split("\n")[0]
