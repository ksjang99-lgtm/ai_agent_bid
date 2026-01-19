import google.generativeai as genai

# 1. API 키 설정
genai.configure(api_key="AIzaSyDz0vJtORhCFZ5uURQ7mDvPy3RJ8deP7YY")
# 사용 가능한 모델 목록 출력
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)

# 2. 모델 초기화 (Gemini 1.5 Flash 선택)
model = genai.GenerativeModel('gemini-3-flash-preview')

# 3. 답변 생성
response = model.generate_content("인공지능의 미래에 대해 한 줄로 요약해줘.")

print(response.text)