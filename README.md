# AI Factory Helper

제조현장 작업자가 설비 문제를 입력하면 AI가 문제 상황을 분석하고
예상 원인, 우선 확인 사항, 권장 조치 방법, 주의사항을 제공하는 PoC 웹 서비스입니다.

## 1. 주요 기능

- 설비명 / 설비 종류 / 알람코드 / 문제 증상 / 추가 상황 입력
- AI 제조설비 문제 분석
- 입력 오류 / API 오류 / 응답 지연 처리
- PC / 모바일 반응형 UI
- Vercel Serverless Functions(Python) 기반 백엔드

## 2. 화면 구성

1. HOME
2. AI 문제해결
3. 분석결과
4. ABOUT

## 3. 기술 스택

- Front-End: HTML, CSS, JavaScript
- Back-End: Python, Vercel Serverless Functions
- AI: OpenAI Responses API
- Deploy: GitHub + Vercel

## 4. 프로젝트 구조

```text
ai-factory-helper/
├── index.html
├── css/
│   └── style.css
├── js/
│   └── app.js
├── api/
│   └── ai.py
├── requirements.txt
├── README.md
└── .gitignore
```

## 5. 환경 변수

API 키는 코드에 직접 작성하지 않습니다.

Vercel 프로젝트 환경변수에 아래 값을 등록합니다.

```text
OPENAI_API_KEY=본인의_API_KEY
OPENAI_MODEL=gpt-5.6-luna
```

`OPENAI_MODEL`은 선택 사항입니다. 설정하지 않으면 예제 코드의 기본 모델을 사용합니다.

## 6. 로컬 실행

Vercel CLI를 사용하는 방법이 가장 간단합니다.

```bash
npm install -g vercel
vercel dev
```

실행 후 터미널에 표시되는 로컬 주소로 접속합니다.

> 단순히 `index.html`만 브라우저에서 열면 `/api/ai` 서버리스 함수가 실행되지 않습니다.

## 7. GitHub 업로드

```bash
git init
git add .
git commit -m "Initial project setup"
git branch -M main
git remote add origin <GitHub 저장소 주소>
git push -u origin main
```

기능 단위로 커밋하는 것을 권장합니다.

예:
- Add home page
- Add troubleshooting form
- Add responsive design
- Add AI API backend
- Connect frontend to AI API
- Add error handling
- Update README

## 8. Vercel 배포

1. GitHub에 프로젝트를 Push합니다.
2. Vercel에서 GitHub Repository를 Import합니다.
3. Project Settings → Environment Variables에 `OPENAI_API_KEY`를 등록합니다.
4. Deploy합니다.
5. 배포 URL에서 메뉴, 반응형 화면, AI 기능을 테스트합니다.

## 9. 테스트 예시

- 설비명: CNC-05
- 설비 종류: CNC 선반
- 알람코드: 2045
- 문제 증상: Tool 교환 직후 설비가 정지했습니다.
- 추가 상황: 가공 중 Tool 교환 직후 발생

## 10. 주의사항

AI 분석 결과는 참고용입니다. 실제 작업 시 설비 제조사 매뉴얼,
작업표준서, 안전절차와 사업장 규정을 우선 적용해야 합니다.
