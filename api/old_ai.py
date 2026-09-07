import json
import os
from http.server import BaseHTTPRequestHandler

from openai import OpenAI


SYSTEM_PROMPT = """
당신은 제조현장 작업자를 지원하는 'AI 제조업 문제해결 도우미'입니다.

사용자가 제공한 설비명, 설비 종류, 알람코드, 문제 증상, 추가 상황을 바탕으로
다음 형식으로 한국어로 답변하세요.

1. 문제 상황 요약
2. 예상 원인
3. 우선 확인 사항
4. 권장 조치 방법
5. 주의사항

원칙:
- 확실하지 않은 원인은 사실처럼 단정하지 말고 '가능성', '추가 확인 필요'라고 표시합니다.
- 위험한 정비, 전기 작업, 방호장치 해제, 인터록 우회 등을 지시하지 않습니다.
- 실제 작업에서는 설비 제조사 매뉴얼, 작업표준서, 안전절차, 사업장 규정을 우선하도록 안내합니다.
- 알람코드의 정확한 의미를 확인할 자료가 없으면 임의로 특정 의미를 만들어내지 않습니다.
- 사용자가 입력한 정보가 부족하면 추가로 확인할 정보를 제안합니다.
""".strip()


class handler(BaseHTTPRequestHandler):
    def _send_json(self, status_code, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(content_length)
            data = json.loads(raw_body or b"{}")

            symptom = str(data.get("symptom", "")).strip()
            if not symptom:
                self._send_json(400, {"error": "문제 증상을 입력해주세요."})
                return

            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                self._send_json(
                    500,
                    {"error": "서버에 OPENAI_API_KEY 환경변수가 설정되어 있지 않습니다."},
                )
                return

            equipment_name = str(data.get("equipmentName", "")).strip() or "미입력"
            equipment_type = str(data.get("equipmentType", "")).strip() or "미입력"
            alarm_code = str(data.get("alarmCode", "")).strip() or "미입력"
            context = str(data.get("context", "")).strip() or "미입력"

            user_input = f"""
설비명: {equipment_name}
설비 종류: {equipment_type}
알람코드: {alarm_code}
문제 증상: {symptom}
추가 상황: {context}
""".strip()

            client = OpenAI(api_key=api_key)
            response = client.responses.create(
                model=os.getenv("OPENAI_MODEL", "gpt-5.6-luna"),
                instructions=SYSTEM_PROMPT,
                input=user_input,
            )

            result = (response.output_text or "").strip()
            if not result:
                self._send_json(502, {"error": "분석 결과를 생성하지 못했습니다."})
                return

            self._send_json(200, {"result": result})

        except json.JSONDecodeError:
            self._send_json(400, {"error": "요청 형식이 올바르지 않습니다."})
        except Exception as exc:
            print("AI API error:", repr(exc))
            self._send_json(
                500,
                {"error": "AI 서버 연결 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
            )
