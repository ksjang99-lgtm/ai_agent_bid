import os
from dotenv import load_dotenv
import google.generativeai as genai


load_dotenv()  # .env 로드

def define_gemini(model_name: str = "gemini-2.5-flash-lite"):
    """
    .env 의 GOOGLE_API_KEY 를 사용하여 Gemini client 생성
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY 가 .env 또는 환경변수에 설정되어 있지 않습니다.")

    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name)
