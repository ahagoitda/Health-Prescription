# 병역준비 건강처방 AI (MVP)

**2026년 병무청·방위사업청·질병관리청 합동 공공데이터·AI 활용 경진대회 출품용 MVP**

## 🎯 핵심 컨셉
- **이름**: 병역준비 건강처방 AI
- **문제**: 20대 남성 비만 유병률 43.9% (2023). 병역 신체등급 기준 강화로 건강 미달 사례 증가
- **솔루션**: KNHANES(국민건강영양조사) 원시자료 기반 **국가 평균 대비 위치 진단** + **병역 영향 고려 prescriptive 주간 개선 로드맵** 제공
- **차별점**: 단순 예측이 아닌 "국민 평균 대비 내 위치 + 병역 신체등급 영향 연계 처방"

## ✅ MVP 필수 포함 요소
- ✅ 질병관리청 KNHANES 제9기 데이터 기반 benchmark 명시 (UI + 설명)
- ✅ 병역 신체등급 영향 언급 + disclaimer
- ✅ Prescriptive(처방형) 구체적 주간 계획 (운동·영양·습관)
- ✅ 퍼센타일 / Top 위험요인 / 차트 시각화
- ✅ "참고용이며 실제 병역판정과 무관" 명확 disclaimer

## 🛠 기술 스택
- **Streamlit** (추천 이유: 2주 내 데이터 중심 MVP 제작 최적)
- Python + pandas + plotly
- Rule-based + 간단 통계 (퍼센타일, 위험 우선순위화)
- 완전 클라이언트/로컬 실행 가능

## 🚀 로컬 실행
```bash
cd knhanes-health-mvp
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
streamlit run app.py
```

## 🌐 배포 (Streamlit Cloud 추천)
1. GitHub에 이 repo 업로드
2. [share.streamlit.io](https://share.streamlit.io) 접속 → GitHub 연결
3. Main file: `app.py`
4. 배포 완료 (무료, 커스텀 도메인 가능)

**대안 배포**:
- Hugging Face Spaces (Streamlit)
- Railway / Render (Docker)

## 📊 데이터 출처
- **주요 데이터**: 질병관리청 국민건강영양조사(KNHANES) 제9기 (2022~2024)
- 20대 남성 비만 유병률 43.9% 등 실제 발표 통계 반영
- **MVP에서는 요약 benchmark를 하드코딩** (실제 대회 제출 시 data.go.kr 원시자료 다운로드하여 분석 명시 예정)
- 출처: https://knhanes.kdca.go.kr / https://data.go.kr

## ⚠️ 중요 Disclaimer (앱 내 모든 화면 표시)
> 본 서비스는 **참고용** 입니다. 제공되는 모든 결과(퍼센타일, 위험 분석, 주간 계획, 병역 영향 언급)는 **실제 병역판정 결과와 무관**하며 법적·의학적 효력이 없습니다. 
> 정확한 신체등급 판정은 병무청 병역판정검사소에서 받으십시오.

## 📁 프로젝트 구조
```
knhanes-health-mvp/
├── app.py                 # 메인 Streamlit 앱 (전체 MVP)
├── requirements.txt
├── README.md
├── .streamlit/
│   └── config.toml        # 테마 설정 (네이비+청록)
└── ( 추가) images/         # 필요시 로고 등
```

## 🏆 대회 제출 팁 - 독창성 극대화 포인트

**이미 있는 것과 차별화하는 방법 (독창성 20점 핵심)**

일반적인 BMI 계산기 / 건강 앱 / 'The 건강보험' 앱과 다른 점:

1. **KNHANES 직접 benchmark 사용**  
   - 단순 평균이 아닌 "같은 연령대 국민 중 상위 몇 %인지" 퍼센타일로 제시
   - 일반 앱들은 WHO나 자사 데이터만 쓰름. 우리는 질병관리청 공식 조사 데이터 사용 명시

2. **병역 신체등급 공식 규칙과 직결**  
   - 병역판정 신체검사 등 검사규칙 별표 2 (신장·체중 기준)를 실제로 반영
   - 최근 개정(BMI 40 이상이 되어야 4급 가능성 높아짐) 내용까지 반영
   - "현재 이 지표면 예상 등급 구간" + 개선 시 변화까지 보여줌

3. **Prescriptive(처방형) + 이유까지**  
   - "운동 하세요" 가 아닌 "KNHANES에서 주 X회 운동 집단이 BMI Y 낮았다"는 근거 + 구체 주간 액션

**제출 시 강조 문구 추천**
> "기존 서비스는 일반 건강관리. 본 서비스는 KNHANES 국가 대표 데이터를 benchmark로 삼아, 병역 신체등급 영향까지 고려한 prescriptive 개선 로드맵을 제공하는 유일한 접근입니다."

- **공공데이터 활용 (30점)**: UI 상단/결과에 "KNHANES 기반" 배너 + 설명 강조
- **AI 기술 (30점)**: Rule-based + 통계 비교 + prescriptive 로직 명확히 기술 (README + 앱 내)
- **독창성 (20점)**: 위 3가지 차별점을 스크린샷 + 설명서에 명확히
- **발전 가능성 (20점)**: B2C(입대 예정자) + B2B(병역준비학원, 지자체 청년정책, 보험 wellness)