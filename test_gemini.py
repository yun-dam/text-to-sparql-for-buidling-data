import vertexai
from vertexai.generative_models import GenerativeModel, Part

# 1. 프로젝트 정보 초기화
PROJECT_ID = "cs224v-yundamko"  # 👈 본인의 GCP 프로젝트 ID로 변경
LOCATION = "us-central1"     # 👈 사용 가능한 리전 (예: us-central1)

vertexai.init(project=PROJECT_ID, location=LOCATION)

# 2. Gemini 모델 로드
# 사용 가능한 모델 확인 (예: gemini-1.5-pro-001, gemini-1.0-pro)
model = GenerativeModel(model_name="publishers/google/models/gemini-2.5-flash-lite")

# 3. 프롬프트 전송 및 응답 받기
prompt = "VS Code에서 Google Cloud 크레딧을 사용해 Gemini API를 호출하는 방법을 알려줘."
response = model.generate_content(prompt)

# 4. 결과 출력
print(response.text)