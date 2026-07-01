"""
병역준비 건강처방 AI — MVP
================================================
2026 병무청·방위사업청·질병관리청 합동 공공데이터·AI 활용 경진대회 출품작

세 주관기관을 하나의 스토리로 연결한다:
  • 질병관리청(KDCA/KNHANES): 국민건강영양조사 기반 '국가 평균 대비 내 건강' 벤치마크
  • 병무청(MMA): 입영까지 기간을 반영한 '병역준비 맞춤 건강 처방'
  • 방위사업청(DAPA): '국방 웨어러블' 헬스 데이터로 이어지는 확장 시나리오

⚠️ 본 앱은 참고용 MVP이며, 실제 병역판정 및 의료 진단과 무관합니다.
"""

import plotly.graph_objects as go
import streamlit as st

from health_logic import (
    blood_pressure_flag,
    bmi,
    bmi_category,
    build_weekly_plan,
    estimate_physical_grade,
    target_weight_range,
)
from synthetic_data import (
    benchmark_stats,
    generate_population,
    generate_wearable,
    percentile_of,
)

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="병역준비 건강처방 AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://knhanes.kdca.go.kr",
        "Report a bug": None,
        "About": "질병관리청 KNHANES 근사 합성데이터 기반 | 참고용 MVP | 실제 병역판정과 무관",
    },
)

TEAL = "#0D9488"
GRAY = "#94A3B8"


@st.cache_data
def load_population():
    return generate_population()


def age_to_group(age: int) -> str:
    if age < 25:
        return "18-24"
    if age < 30:
        return "25-29"
    return "30-39"


# ==================== SIDEBAR: 입력 ====================
def sidebar_inputs():
    st.sidebar.header("🧍 내 정보 입력")
    age = st.sidebar.slider("나이", 18, 39, 21)
    height = st.sidebar.number_input("키 (cm)", 150.0, 200.0, 174.0, 0.5)
    weight = st.sidebar.number_input("몸무게 (kg)", 40.0, 150.0, 74.0, 0.5)
    sbp = st.sidebar.number_input("수축기 혈압 (mmHg)", 90, 180, 120, 1)
    months = st.sidebar.slider("입영까지 남은 개월 수", 0, 24, 8)
    fitness = st.sidebar.select_slider(
        "현재 체력 수준", options=["낮음", "보통", "우수"], value="보통"
    )
    return dict(age=age, height=height, weight=weight, sbp=sbp, months=months, fitness=fitness)


# ==================== 탭 1: 내 건강 진단 ====================
def tab_diagnosis(inp, pop):
    ag = age_to_group(inp["age"])
    b = bmi(inp["height"], inp["weight"])
    cat = bmi_category(b)
    stats = benchmark_stats(pop, ag)
    grade = estimate_physical_grade(b)

    st.subheader(f"🩺 내 건강 진단  ·  {ag}세 연령대 기준")

    c1, c2, c3, c4 = st.columns(4)
    bmi_pct = percentile_of(pop, ag, "bmi", b)
    c1.metric("BMI", f"{b}", f"{cat}")
    c2.metric("BMI 백분위", f"{bmi_pct:.0f}%",
              help="같은 연령대에서 나보다 낮은 사람의 비율")
    c3.metric("혈압 상태", blood_pressure_flag(inp["sbp"]))
    c4.metric("신체등급(참고용)", grade["label"].split()[0], help=grade["note"])

    st.divider()

    # 국가 평균 대비 벤치마크 차트
    left, right = st.columns([3, 2])
    with left:
        st.markdown("**국가 평균 대비 내 지표 (KNHANES 근사)**")
        metrics = {"BMI": ("bmi", b), "혈압(수축기)": ("sbp", inp["sbp"]),
                   "체중(kg)": ("weight", inp["weight"])}
        fig = go.Figure()
        labels = list(metrics.keys())
        mine = [metrics[k][1] for k in labels]
        avg = [stats[metrics[k][0]]["mean"] for k in labels]
        fig.add_trace(go.Bar(y=labels, x=avg, name="국가 평균", orientation="h",
                             marker_color=GRAY))
        fig.add_trace(go.Bar(y=labels, x=mine, name="나", orientation="h",
                             marker_color=TEAL))
        fig.update_layout(barmode="group", height=280,
                          margin=dict(l=10, r=10, t=10, b=10),
                          legend=dict(orientation="h", y=1.15))
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.markdown("**BMI 분포 속 내 위치**")
        sub = pop[pop["age_group"] == ag]["bmi"]
        hist = go.Figure()
        hist.add_trace(go.Histogram(x=sub, nbinsx=30, marker_color=GRAY, name="또래 분포"))
        hist.add_vline(x=b, line_color=TEAL, line_width=3,
                       annotation_text="나", annotation_position="top")
        hist.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10),
                           showlegend=False)
        st.plotly_chart(hist, use_container_width=True)

    lo, hi = target_weight_range(inp["height"])
    st.info(f"💡 키 {inp['height']}cm 기준 정상 BMI 목표 체중: **{lo}~{hi}kg**  ·  {grade['note']}")

    st.caption("⚠️ 신체등급은 BMI(체격) 기준만 단순화한 참고값입니다. "
               "실제 병역판정은 시력·질환 등 수백 항목을 병무청이 종합 판정하며 본 결과와 무관합니다.")


# ==================== 탭 2: 맞춤 처방 ====================
def tab_prescription(inp):
    st.subheader("📅 병역준비 맞춤 건강 처방")
    plan = build_weekly_plan(inp["height"], inp["weight"], inp["months"], inp["fitness"])

    c1, c2, c3 = st.columns(3)
    c1.metric("현재 페이즈", plan["phase"])
    c2.metric("처방 방향", plan["direction"])
    c3.metric("입영까지", f"D-{inp['months']*30}일" if inp["months"] else "입영 임박")

    st.success(f"🎯 {plan['summary']}")

    st.markdown("**주간 운동 플랜**")
    import pandas as pd
    df = pd.DataFrame(plan["weekly"]).rename(
        columns={"day": "요일", "focus": "focus", "detail": "내용"})
    df.columns = ["요일", "집중", "내용"]
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("**군 체력검정 대비 체크리스트**")
    for item in plan["military_prep"]:
        st.checkbox(item, key=f"prep_{item}")


# ==================== 탭 3: 국방 웨어러블 (방사청 연계) ====================
def tab_wearable(inp):
    st.subheader("⌚ 국방 웨어러블 헬스 데이터 (방위사업청 연계 시나리오)")
    st.markdown(
        "방위사업청이 추진하는 **국방 스마트/웨어러블 R&D** 관점에서, 입영 전 청년의 "
        "웨어러블 데이터가 입대 후 **병사 건강관리·전투체력 모니터링 체계**로 자연스럽게 "
        "이어질 수 있음을 보여주는 확장 시나리오입니다. (아래는 합성 시연 데이터)"
    )
    wear = generate_wearable(days=14, fitness_level=inp["fitness"])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("평균 걸음 수", f"{wear['steps'].mean():,.0f}")
    c2.metric("평균 안정시 심박", f"{wear['resting_hr'].mean():.0f} bpm")
    c3.metric("평균 수면", f"{wear['sleep_hours'].mean():.1f} h")
    c4.metric("평균 활동칼로리", f"{wear['active_kcal'].mean():,.0f} kcal")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=wear["date"], y=wear["steps"], name="걸음 수",
                             line=dict(color=TEAL)))
    fig.add_trace(go.Scatter(x=wear["date"], y=wear["active_kcal"], name="활동칼로리",
                             yaxis="y2", line=dict(color=GRAY)))
    fig.update_layout(
        height=320, margin=dict(l=10, r=10, t=30, b=10),
        yaxis=dict(title="걸음 수"),
        yaxis2=dict(title="활동칼로리", overlaying="y", side="right"),
        legend=dict(orientation="h", y=1.15),
        title="최근 14일 활동 추이",
    )
    st.plotly_chart(fig, use_container_width=True)

    avg_hr = wear["resting_hr"].mean()
    if avg_hr > 72:
        st.warning("안정시 심박이 다소 높습니다. 유산소 운동 빈도를 늘리면 심폐 지구력 개선에 도움이 됩니다.")
    else:
        st.info("안정시 심박이 양호합니다. 현재 활동 수준을 유지하세요.")

    st.caption("⚠️ 웨어러블 수치는 방사청 연계 가능성을 시연하기 위한 합성 데이터입니다.")


# ==================== 탭 4: 데이터·근거 ====================
def tab_about():
    st.subheader("ℹ️ 데이터 출처 · 방법론 · 면책")
    st.markdown(
        """
### 세 주관기관 연계 구조
| 기관 | 역할 | 본 앱에서의 반영 |
|------|------|------------------|
| **질병관리청** | 국민건강영양조사(KNHANES) | 연령대별 국가 평균 대비 건강 벤치마크 |
| **병무청** | 병역판정·입영 관리 | 입영까지 기간 반영 맞춤 건강 처방, 체격등급(참고용) |
| **방위사업청** | 국방 R&D·스마트국방 | 국방 웨어러블 헬스 데이터 확장 시나리오 |

### 데이터
- **합성(synthetic) 샘플 데이터** 사용. 질병관리청이 공개한 연령대별 요약통계
  (평균·표준편차) 범위를 참고해 근사 생성했으며, **KNHANES 원자료가 아닙니다.**
- 재현성을 위해 난수 시드를 고정했습니다.
- 실서비스화 시 KNHANES 이용승인 원자료 또는 공공데이터포털 API로 대체 가능합니다.

### 신체등급 산출 방법 (참고용)
- 병역판정 신체검사의 **체격(BMI) 기준**만 단순화해 매핑한 근사값입니다.
- 실제 병역판정은 시력·청력·질환·정신건강 등 **수백 개 항목**을 병무청이
  종합 판정하며, **본 앱 결과와 무관합니다.**

### ⚠️ 면책
본 앱은 경진대회 출품용 참고 MVP입니다. 의료 진단이나 병역판정을 대체하지 않으며,
건강 관련 결정은 반드시 의료진 및 병무청 공식 절차를 따르시기 바랍니다.
        """
    )


# ==================== MAIN ====================
def main():
    st.title("🛡️ 병역준비 건강처방 AI")
    st.caption("질병관리청 · 병무청 · 방위사업청 합동 공공데이터·AI 활용 경진대회 출품작 (참고용 MVP)")

    pop = load_population()
    inp = sidebar_inputs()

    t1, t2, t3, t4 = st.tabs(["🩺 내 건강 진단", "📅 맞춤 처방", "⌚ 국방 웨어러블", "ℹ️ 데이터·근거"])
    with t1:
        tab_diagnosis(inp, pop)
    with t2:
        tab_prescription(inp)
    with t3:
        tab_wearable(inp)
    with t4:
        tab_about()


if __name__ == "__main__":
    main()
