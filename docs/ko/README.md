# 수학 모델링 다중 에이전트 논문 생성 시스템

[![Stars](https://img.shields.io/github/stars/Linference/math_model?style=social)](https://github.com/Linference/math_model/stargazers)
[![Version](https://img.shields.io/badge/version-v2.2-6f42c1)](https://github.com/Linference/math_model/blob/main/skill/CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python)
![LaTeX](https://img.shields.io/badge/LaTeX-xelatex-008080?logo=latex)
![Claude Code](https://img.shields.io/badge/Claude_Code-v2.2-D97757)
![CUMCM / MCM / HiMCM](https://img.shields.io/badge/CUMCM_|_MCM_|_HiMCM-e74c3c)

---

[中文](../../README.md) · [English](../en/README.md) · [日本語](../ja/README.md) · **한국어** ← 현재

---

**v2.2** — 다중 에이전트 적대적 협업 + 9개 독립 QA 게이트 + 안티패턴 하드 블록 + 휴먼인더루프 체크포인트 + 교차 단계 상태 관리. 21권의 참조 매뉴얼, 6권의 알고리즘 쿡북, 중영일 구문 은행, 안티패턴 지식 베이스, 환경 진단 스크립트.

대회 문제 PDF를 넣으면 문제 분석 → 방법 선택 → 웹 데이터 수집 → Python 해결 → 시각화 → LaTeX 논문 컴파일 → 3역할 병렬 적대적 검토 → 최종 PDF까지 자동 실행. CUMCM(중국), MCM/ICM(미국), HiMCM을 지원합니다.

---

## 빠른 시작

### 사전 요구사항

- **Node.js** ≥ v18 — [nodejs.org](https://nodejs.org/)
- **Claude Code**: `npm install -g @anthropic-ai/claude-code`

### 설치

```bash
git clone https://github.com/Linference/math_model.git ~/.claude/skills/math-modeling
```

또는 [Releases](https://github.com/Linference/math_model/releases)에서 ZIP 다운로드.

### 실행

```bash
claude
/math-modeling
[대회 문제 붙여넣기 또는 PDF 드래그]
```

---

## 7단계 파이프라인

| 단계 | 작업 | 산출물 |
|:--:|------|------|
| 0 | 프로젝트 스캐폴딩 | 표준 디렉토리 구조 |
| 1 | 심층 문제 분석 | 구조화된 분석 보고서 (2000자 이상) |
| 2 | 방법 선택 + ML/DL 결정 | 모델링 계획 + 차트 체크리스트 |
| 3 | 웹 데이터 수집 | CSV 파일 + SOURCES.md |
| 4 | Python 구현 | 실행 가능한 스크립트 + 수치 결과 |
| 5 | 시각화 (16가지 차트 유형) | 고품질 그림 (300 DPI) |
| 6 | LaTeX 작성 + 컴파일 | 논문 초안 |
| 7 | 3역할 적대적 검토 | 최종 PDF (점수 ≥ 7.5/10) |

## 8개 서브 에이전트

| 에이전트 | 역할 |
|------|------|
| `mm-problem-analyst` | 문제 분석: 질문 분해, 제약 조건 및 함정 발견 |
| `mm-modeler` | 방법 선택: ML/DL 결정, 차트 계획 |
| `mm-data-hunter` | 데이터: Wikipedia/GitHub/Kaggle/sklearn 검색 |
| `mm-coder` | 구현: Python 해결 + 시각화 |
| `mm-writer` | 작성: LaTeX 템플릿 작성, 검토 의견 반영 |
| `mm-reviewer` | 검토: 5차원 채점, 약점 발견 |
| `mm-verifier` | 검증: 수치, 단위, 경계 조건 교차 확인 |
| `mm-reasoner` | 추론: 공식 유도 감사, 증명 간격 보완 |

## 적대적 검토

세 명의 검토자 역할이 동일한 논문을 병렬 평가 — 검토자(모델링 품질), 검증자(수치 정확성), 추론자(수학적 엄격성). 작성자가 각 지적사항을 수정하고 세 명이 재채점. 평균 점수 ≥ 7.5 또는 최대 4라운드까지 반복.

## 품질 게이트 (v2.2)

9개 독립 Subagent QA 게이트 + 안티패턴 하드 블록 + 휴먼인더루프 체크포인트로 각 단계의 출력 품질을 보장합니다.

---

## 프로젝트 구조

```
math_model/
├── README.md
├── samples/                      # 완전한 예제 프로젝트
│   ├── 2024_CUMCM_A/             # CUMCM 문제 A
│   └── 2025_HiMCM_Problem_B/     # HiMCM 문제 B
└── skill/                        # 스킬 설치 패키지
    ├── SKILL.md                  # 메인 스킬 정의
    ├── references/               # 15개 매뉴얼 + 6개 쿡북
    ├── scripts/                  # 헬퍼 스크립트
    ├── templates/                # LaTeX 템플릿 (중/영)
    └── workflows/                # 검토 워크플로우
```

---

## 샘플 프로젝트

### 2024 CUMCM A — 벤치 드래곤 운동

223개 벤치 섹션이 아르키메데스 나선을 따라 이동하는 궤적을 모델링하고 충돌을 감지하며 방향 전환 경로를 최적화합니다. 기술: 현 길이 제약 이진 탐색, SAT 충돌 감지, 제약 비선형 최적화.

### 2025 HiMCM B — 슈퍼볼 지속 가능한 개최지 선정

NFL을 위한 환경 요소 전용 개최지 선정 모델을 구축하고, 19개 역사적 도시 + 3개 후보 도시를 평가, 올림픽으로 확장합니다. 기술: AHP + TOPSIS 2계층 의사 결정, Scope 1/2/3 탄소 배출 분석, 민감도 분석.

---

## 변경 이력

### v2.2.0 — 심층 수정 (현재)
- **버그 수정**: 점수 집계를 단순 평균에서 역할×차원 가중치 행렬 + 하드 캡 + 이상치 중재로 업그레이드
- **안티패턴 하드 블록 (A1/A2/A3)**: 코드/작성/전체 차원 안티패턴 스캔, High 적중 시 수정 필수
- **데이터 품질 게이트 (D1)**: 3단계에서 결측치 + 이상치 + 다중 소스 정렬 검사 추가
- **휴먼인더루프 체크포인트**: 1/4/6단계 후 일시 중지, 사용자 확인
- 게이트를 5개에서 9개로 확장

### v2.0.0 — 아키텍처 업그레이드
- 독립 Subagent QA 프로토콜 (5개 게이트)
- 교차 단계 상태 관리

---

## 라이선스

MIT
