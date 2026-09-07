import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from openai import OpenAI


# ---------------------------------------------------------
# FastAPI 앱 생성
# ---------------------------------------------------------
app = FastAPI(
    title="AI Factory Helper",
    description="제조업 문제해결 AI 도우미",
    version="1.0.0",
)


# ---------------------------------------------------------
# 정적 파일 연결
# 프로젝트 구조:
#
# ai-factory-helper/
# ├─ index.html
# ├─ css/
# │  └─ style.css
# ├─ js/
# │  └─ app.js
# └─ api/
#    └─ index.py
# ---------------------------------------------------------
app.mount("/css", StaticFiles(directory="css"), name="css")
app.mount("/js", StaticFiles(directory="js"), name="js")


# ---------------------------------------------------------
# 사용자 입력 데이터 모델
# ---------------------------------------------------------
class TroubleRequest(BaseModel):
    equipmentName: str = ""
    equipmentType: str = ""
    alarmCode: str = ""
    symptom: str = ""
    context: str = ""


# ---------------------------------------------------------
# AI 시스템 프롬프트
# ---------------------------------------------------------
SYSTEM_PROMPT = """
당신은 제조현장 작업자를 지원하는
'AI 제조업 문제해결 도우미'입니다.

사용자가 제공한 정보를 바탕으로
설비 문제의 원인과 확인 사항을 분석합니다.

반드시 다음 형식으로 답변하세요.

1. 문제 상황 요약
2. 예상 원인
3. 우선 확인 사항
4. 권장 조치 방법
5. 주의사항

답변 원칙:

- 확실하지 않은 사항은 사실처럼 단정하지 않습니다.
- 불확실한 경우 '가능성 있음', '추가 확인 필요'라고 표시합니다.
- 알람코드의 정확한 의미를 확인할 자료가 없다면 임의로 의미를 만들어내지 않습니다.
- 위험한 정비 작업이나 안전장치 해제를 지시하지 않습니다.
- 전기 작업, 설비 내부 작업, 인터록 우회 등을 권장하지 않습니다.
- 실제 작업에서는 설비 제조사 매뉴얼, 작업표준서, 안전절차,
  사업장 규정을 우선하도록 안내합니다.
- 사용자가 제공한 정보가 부족하면 추가로 확인해야 할 정보를 제시합니다.
""".strip()


# ---------------------------------------------------------
# HOME 화면
# ---------------------------------------------------------
@app.get("/")
def home():
    return FileResponse("index.html")


# ---------------------------------------------------------
# 서버 상태 확인용 API
# ---------------------------------------------------------
@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "AI Factory Helper"
    }


# ---------------------------------------------------------
# AI 문제 분석 API
# ---------------------------------------------------------
@app.post("/api/ai")
def analyze_problem(data: TroubleRequest):

    # 1. 필수 입력 확인
    symptom = data.symptom.strip()

    if not symptom:
        raise HTTPException(
            status_code=400,
            detail="문제 증상을 입력해주세요."
        )

    # 2. 환경변수에서 API Key 가져오기
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY 환경변수가 설정되어 있지 않습니다."
        )

    # 3. 사용자 입력 정리
    equipment_name = data.equipmentName.strip() or "미입력"
    equipment_type = data.equipmentType.strip() or "미입력"
    alarm_code = data.alarmCode.strip() or "미입력"
    context = data.context.strip() or "미입력"

    user_input = f"""
설비명: {equipment_name}
설비 종류: {equipment_type}
알람코드: {alarm_code}
문제 증상: {symptom}
추가 상황: {context}
""".strip()

    # 4. OpenAI API 호출
    try:
        client = OpenAI(api_key=api_key)

        response = client.responses.create(
            model=os.getenv(
                "OPENAI_MODEL",
                "gpt-5-mini"
            ),
            instructions=SYSTEM_PROMPT,
            input=user_input,
        )

        result = (response.output_text or "").strip()

        if not result:
            raise HTTPException(
                status_code=502,
                detail="AI 분석 결과를 생성하지 못했습니다."
            )

        # 5. 정상 결과 반환
        return {
            "success": True,
            "result": result
        }

    except HTTPException:
        raise

    except Exception as e:
        # 실제 오류는 VS Code Terminal에서 확인 가능
        print("OpenAI API Error:", repr(e))

        raise HTTPException(
            status_code=500,
            detail="AI 분석 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
        )