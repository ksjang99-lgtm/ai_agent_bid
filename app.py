import streamlit as st
from apl_Client import get_bid_pblanc_list_info_cnstwk 

import json
import re
from gemini_client import define_gemini

import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3:latest"
# MODEL_NAME ="qwen2.5:7b"


def extract_bid_qualification_with_local_llm(extracted_text: str) -> str:
    """
    입찰 공고 문서 내용을 기반으로
    - 입찰 참가자격
    - 입찰 절차
    - 입찰참가신청 및 제출서류
    를 JSON 형식으로 추출한다.
    """
    prompt = f"""
너는 프로그램에 의해 호출되는 시스템이다.
사람에게 설명하지 말고, 오직 JSON만 출력해야 한다.

아래 제공되는 텍스트는 입찰 공고 원문이다.
원문에 근거하여 다음 3개 항목을 추출하라.

- 입찰 참가자격
- 입찰 절차
- 입찰참가신청 및 제출서류

규칙:
1. 반드시 원문에 있는 내용만 사용하라.
2. 추측, 해석, 요약 설명을 하지 마라.
3. JSON 이외의 텍스트를 절대 출력하지 마라.
4. 출력은 반드시 한국어로 작성하라.
5. 값이 없는 항목은 빈 문자열("")로 출력하라.

출력 형식 (이 형식 외 출력 금지):
{{
  "입찰 참가자격": "",
  "입찰 절차": "",
  "입찰참가신청 및 제출서류": ""
}}

입찰 공고 원문:
\"\"\"
{extracted_text}
\"\"\"
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.0,
                "num_predict": 1200
            }
        },
        timeout=120
    )

    response.raise_for_status()

    raw_text = response.json()["response"].strip()
    return raw_text
    # try:
    #     return json.loads(raw_text)
    # except json.JSONDecodeError:
    #     raise ValueError(
    #         "LLM 응답이 JSON 형식이 아닙니다.\n"
    #         f"Raw response:\n{raw_text}"
    #     )



def extract_bid_qualification_with_gemini(extracted_text: str) -> dict:
    """
    추출된 입찰 공고 문서 내용을 기반으로
    입찰 참가자격 / 입찰 절차 / 입찰참가신청 및 제출서류를 JSON으로 정리
    """
    MODEL_NAME = "gemini-2.5-flash-lite"
    # MODEL_NAME = "gemini-3-flash-preview"
    model = define_gemini(MODEL_NAME)

    prompt = f"""
입찰 공고 내용입니다.
해당 내용을 바탕으로 입찰 참가자격, 입찰 절차, 입찰참가신청 및 제출서류를 정리해서 알려주세요.

규칙:
1. 반드시 전달한 문서 내용만을 근거로 작성하세요.
2. 문서에 없는 내용은 작성하지 마세요.
3. 추측, 보완, 해석을 하지 마세요.
4. 결과는 반드시 JSON 형식으로 출력하세요.
5. 각 항목의 값은 문장 형태의 텍스트로 작성하세요.
출력 양식은 JSON으로 다음 형식을 따르세요.
출력 양식:
{{
  "입찰 참가자격": "내용",
  "입찰 절차": "내용",
  "입찰참가신청 및 제출서류": "내용"
}}

입찰 공고 원문:
\"\"\"
{extracted_text}
\"\"\"
"""

    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": 0.1,
            "top_p": 0.9,
            "max_output_tokens": 1500
        }
    )
    print(f"Gemini response:{response.text}")
    return safe_json_loads(response.text)

# 입찰자격
def extract_rawText1_with_gemini(extracted_text: str) -> str:
    """
    추출된 입찰 공고 문서 내용을 기반으로
    입찰 참가자격 / 입찰 절차 / 입찰참가신청 및 제출서류를 JSON으로 정리
    """
    # MODEL_NAME = "gemini-2.5-flash-lite"
    MODEL_NAME = "gemini-3-flash-preview"
    model = define_gemini(MODEL_NAME)

    prompt = f"""
입찰 공고 내용입니다.
입찰 공고 원문의 해당 내용을 바탕으로 입찰 참가자격 정리해서 알려주세요.

규칙:
1. 반드시 전달한 문서 내용만을 근거로 작성하세요.
2. 문서에 없는 내용은 작성하지 마세요.
3. 추측, 보완, 해석을 하지 마세요.
4. 각 항목의 값은 문장 형태의 텍스트로 작성하세요.
출력 양식은  다음 형식을 절대 따르세요.
출력 양식:
입찰 참가자격

위 내용이 없을시에는 없음을 표시하세요


입찰 공고 원문:
\"\"\"
{extracted_text}
\"\"\"
"""

    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": 0.1,
            "top_p": 0.9,
            "max_output_tokens": 1500
        }
    )
    return response.text

# 입찰 절차
def extract_rawText2_with_gemini(extracted_text: str) -> str:
    """
    추출된 입찰 공고 문서 내용을 기반으로
    입찰 참가자격 / 입찰 절차 / 입찰참가신청 및 제출서류를 JSON으로 정리
    """
    # MODEL_NAME = "gemini-2.5-flash-lite"
    MODEL_NAME = "gemini-3-flash-preview"
    model = define_gemini(MODEL_NAME)

    prompt = f"""
입찰 공고 내용입니다.
입찰 공고 원문의 해당 내용을 바탕으로 입찰 절차를 정리해서 알려주세요.

규칙:
1. 반드시 전달한 문서 내용만을 근거로 작성하세요.
2. 문서에 없는 내용은 작성하지 마세요.
3. 추측, 보완, 해석을 하지 마세요.
4. 각 항목의 값은 문장 형태의 텍스트로 작성하세요.
출력 양식은  다음 형식을 절대 따르세요.
출력 양식:
입찰 절차

위 해당하는 내용이 없을시에는 없음을 표시하세요


입찰 공고 원문:
\"\"\"
{extracted_text}
\"\"\"
"""

    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": 0.1,
            "top_p": 0.9,
            "max_output_tokens": 1500
        }
    )
    return response.text


#입찰참가신청 및 제출서류
def extract_rawText3_with_gemini(extracted_text: str) -> str:
    """
    추출된 입찰 공고 문서 내용을 기반으로
    입찰 참가자격 / 입찰 절차 / 입찰참가신청 및 제출서류를 JSON으로 정리
    """
    # MODEL_NAME = "gemini-2.5-flash-lite"
    MODEL_NAME = "gemini-3-flash-preview"
    model = define_gemini(MODEL_NAME)

    prompt = f"""
입찰 공고 내용입니다.
입찰 공고 원문의 해당 내용을 바탕으로 입찰참가신청 및 제출서류를 정리해서 알려주세요.

규칙:
1. 반드시 전달한 문서 내용만을 근거로 작성하세요.
2. 문서에 없는 내용은 작성하지 마세요.
3. 추측, 보완, 해석을 하지 마세요.
4. 각 항목의 값은 문장 형태의 텍스트로 작성하세요.
출력 양식은  다음 형식을 절대 따르세요.
출력 양식:
입찰참가신청 및 제출서류

위 해당하는 내용이 없을시에는 없음을 표시하세요


입찰 공고 원문:
\"\"\"
{extracted_text}
\"\"\"
"""

    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": 0.1,
            "top_p": 0.9,
            "max_output_tokens": 1500
        }
    )
    return response.text



def safe_json_loads(text: str) -> dict:
    """
    Gemini 응답에서 JSON 블록만 추출하여 파싱
    """
    if not text:
        raise ValueError("LLM 응답이 비어 있습니다.")

    # ```json ... ``` 제거
    cleaned = re.sub(r"```json|```", "", text).strip()

    # JSON 객체 추출 (첫 { 부터 마지막 } 까지)
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        raise ValueError(f"JSON 형식을 찾을 수 없습니다.\n응답 내용:\n{cleaned}")

    return json.loads(match.group())





# 타이틀
st.title("텍스트 입력 & 작성 예제")

# 2개의 컬럼 생성 (비율 조절 가능)
col1, col2 = st.columns([3, 1])  # col1이 col2보다 넓게

with col1:
    user_input = st.text_input("R26BK01276773")

with col2:
    submit_button = st.button("작성")

# 버튼 클릭 시 입력된 텍스트 표시
if submit_button:
    data = get_bid_pblanc_list_info_cnstwk(user_input)
    st.write(f"입찰 공고 번호: {user_input}")
    print(len(data))
    for item in data:
        file_name = item["filename"]
        extracted_doc_text = item["text"]
        st.write(f"파일이름 : {file_name}")
       
        # local llm
        # result = extract_bid_qualification_with_local_llm(extracted_doc_text)
        # st.write(f"{result}")
         # st.write(f"내용 : {extracted_doc_text}")
        result = extract_bid_qualification_with_gemini(extracted_doc_text)
        for key, value in result.items():
            st.write(f"{key}")
            st.write(f"{value}")
        # "gemini-3-flash-preview
        # result = extract_rawText1_with_gemini(extracted_doc_text)
        # st.write(f"{result}")
        # result2 = extract_rawText2_with_gemini(extracted_doc_text)
        # st.write(f"{result2}")

        
        
        
    

#     # print(data)
# data = get_bid_pblanc_list_info_cnstwk("R26BK01276773")
# print(data)