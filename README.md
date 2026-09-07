# AI Factory Helper

제조현장 작업자가 설비 문제를 입력하면 AI가 문제 상황을 분석하고,
예상 원인과 우선 확인 사항, 권장 조치 방법, 주의사항을 정리해 주는 PoC 웹 서비스입니다.

## 주요 기능

- 설비명, 설비 종류, 알람코드, 문제 증상, 추가 상황 입력
- OpenAI Responses API를 이용한 제조설비 문제 분석
- 필수 입력 검증, API 오류, 응답 지연 처리
- PC와 모바일을 지원하는 반응형 화면
- FastAPI 기반 백엔드와 정적 HTML/CSS/JavaScript 프론트엔드

## 기술 스택

- Frontend: HTML, CSS, JavaScript
- Backend: Python, FastAPI, Uvicorn
- AI: OpenAI Responses API
- Package management: `requirements.txt`, `pyproject.toml`

## 프로젝트 구조

```text
ai-factory-helper/
├── index.html          # 웹 페이지
├── css/style.css       # 화면 스타일
├── js/app.js           # 폼 처리 및 API 호출
├── api/index.py        # FastAPI 앱 및 AI 분석 API
├── requirements.txt    # 실행 의존성
├── pyproject.toml      # 프로젝트 메타데이터
└── README.md
```

## 시작하기

### 1. 의존성 설치

Python 3.12 이상을 준비한 뒤 프로젝트 루트에서 가상환경을 만들고 의존성을 설치합니다.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

PowerShell에서 스크립트 실행이 제한되면 가상환경을 활성화하지 않고
`.\.venv\Scripts\python.exe -m pip install -r requirements.txt`처럼 실행해도 됩니다.

### 2. 환경 변수 설정

API 키는 소스 코드에 작성하지 않습니다. 실행 전에 환경 변수를 설정합니다.

```powershell
$env:OPENAI_API_KEY = "본인의_API_KEY"
$env:OPENAI_MODEL = "gpt-5-mini"
```

`OPENAI_MODEL`은 선택 사항이며, 지정하지 않으면 `gpt-5-mini`를 사용합니다.

### 3. 개발 서버 실행

프로젝트 루트에서 다음 명령을 실행합니다.

```powershell
python -m uvicorn api.index:app --reload
```

브라우저에서 `http://127.0.0.1:8000`으로 접속합니다.

> `index.html`을 파일로 직접 열면 FastAPI의 `/api/ai` 엔드포인트에 연결할 수 없습니다.

## API

### `GET /api/health`

서버 상태를 확인합니다.

```json
{
	"status": "ok",
	"service": "AI Factory Helper"
}
```

### `POST /api/ai`

문제 분석을 요청합니다. `symptom`은 필수이며 나머지 필드는 선택 사항입니다.

```json
{
	"equipmentName": "CNC-05",
	"equipmentType": "CNC 선반",
	"alarmCode": "2045",
	"symptom": "Tool 교환 직후 설비가 정지했습니다.",
	"context": "가공 중 Tool 교환 직후 발생"
}
```

정상 응답은 다음과 같은 형태입니다.

```json
{
	"success": true,
	"result": "AI 분석 결과"
}
```

서버 실행 후 FastAPI 자동 문서는 `http://127.0.0.1:8000/docs`에서 확인할 수 있습니다.

## 테스트 시나리오

1. 위 예시 입력을 작성합니다.
2. `AI 문제 분석하기`를 클릭합니다.
3. 분석 결과에 문제 상황 요약, 예상 원인, 우선 확인 사항, 권장 조치 방법, 주의사항이 표시되는지 확인합니다.
4. 증상을 비운 상태로 제출했을 때 검증 메시지가 표시되는지 확인합니다.
5. `GET /api/health`가 정상 응답하는지 확인합니다.

## 안전 주의사항

AI 분석 결과는 참고용입니다. 실제 작업에서는 설비 제조사 매뉴얼,
작업표준서, 안전절차와 사업장 규정을 우선 적용해야 합니다.
전기 작업, 설비 내부 작업, 안전장치 해제 또는 인터록 우회는 안내 결과와 관계없이
권한을 가진 담당자와 정해진 안전 절차에 따라 수행해야 합니다.
