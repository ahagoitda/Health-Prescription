"""
건강 지표 계산 · 신체등급(참고용) 추정 · 맞춤 처방 로직
=========================================================

⚠️ 중요 면책
  본 모듈의 신체등급은 병역판정 신체검사의 '체격(BMI)' 기준만을 단순화해
  근사한 '참고용' 값이다. 실제 병역판정은 시력·질환·정신건강 등 수백 개
  항목을 종합해 병무청 병역판정검사에서 결정되며, 본 결과와 무관하다.
"""

from __future__ import annotations


def bmi(height_cm: float, weight_kg: float) -> float:
    """BMI 계산."""
    if height_cm <= 0:
        return 0.0
    return round(weight_kg / (height_cm / 100) ** 2, 1)


def bmi_category(value: float) -> str:
    """대한비만학회 기준 BMI 분류(성인)."""
    if value < 18.5:
        return "저체중"
    if value < 23:
        return "정상"
    if value < 25:
        return "비만 전단계"
    if value < 30:
        return "1단계 비만"
    if value < 35:
        return "2단계 비만"
    return "3단계 비만"


# 병역판정 신체검사 규칙(체격 기준)을 단순화한 BMI→신체등급 근사 매핑.
# 근거: 병역판정 신체검사 등의 검사규칙 별표(신장·체중에 따른 판정) 공개본 참고.
# ⚠️ BMI 단일 기준 근사이며 실제 종합판정과 다를 수 있음.
def estimate_physical_grade(value: float) -> dict:
    """
    BMI 기반 신체등급(참고용)을 추정한다.
    반환: {"grade": int, "label": str, "note": str}
    """
    if value < 14.0:
        g, label = 5, "5급 (전시근로역, 참고용)"
    elif value < 16.0:
        g, label = 4, "4급 (보충역, 참고용)"
    elif value < 17.0:
        g, label = 3, "3급 (현역, 참고용)"
    elif value < 18.5:
        g, label = 2, "2급 (현역, 참고용)"
    elif value < 25.0:
        g, label = 1, "1급 (현역, 참고용)"
    elif value < 30.0:
        g, label = 2, "2급 (현역, 참고용)"
    elif value < 33.0:
        g, label = 3, "3급 (현역, 참고용)"
    elif value < 40.0:
        g, label = 4, "4급 (보충역, 참고용)"
    else:
        g, label = 4, "4급 (보충역, 참고용)"

    note = "BMI 18.5~24.9 구간이 신체등급상 가장 안정적입니다."
    if g != 1:
        note = "정상 BMI(18.5~24.9)에 근접하면 체격 항목 등급이 개선될 수 있습니다."

    return {"grade": g, "label": label, "note": note}


def blood_pressure_flag(sbp: float) -> str:
    """수축기 혈압 간이 분류."""
    if sbp < 120:
        return "정상"
    if sbp < 130:
        return "주의 (정상 상단)"
    if sbp < 140:
        return "고혈압 전단계"
    return "고혈압 의심 (진료 권장)"


def target_weight_range(height_cm: float) -> tuple[float, float]:
    """BMI 18.5~24.9에 해당하는 목표 체중 범위(kg)."""
    h = height_cm / 100
    return round(18.5 * h * h, 1), round(24.9 * h * h, 1)


def build_weekly_plan(
    height_cm: float,
    weight_kg: float,
    months_to_enlist: int,
    fitness_level: str,
) -> dict:
    """
    입영까지 남은 개월 수와 현재 상태를 반영한 주간 건강 처방을 생성한다.
    반환: {"phase": str, "summary": str, "weekly": list[dict], "military_prep": list[str]}
    """
    b = bmi(height_cm, weight_kg)
    lo, hi = target_weight_range(height_cm)

    # 감량/증량/유지 방향 결정
    if weight_kg > hi:
        direction = "감량"
        gap = round(weight_kg - hi, 1)
        goal = f"목표 체중 상한 {hi}kg 대비 약 {gap}kg 감량 권장"
    elif weight_kg < lo:
        direction = "증량"
        gap = round(lo - weight_kg, 1)
        goal = f"목표 체중 하한 {lo}kg 대비 약 {gap}kg 증량 권장"
    else:
        direction = "유지"
        goal = f"현재 정상 BMI({b}) — 체력 향상 중심 유지"

    # 입영까지 기간에 따른 페이즈
    if months_to_enlist <= 2:
        phase = "임박기 (D-8주 이내)"
        intensity = "부상 위험을 낮추고 컨디션을 끌어올리는 데 집중"
    elif months_to_enlist <= 6:
        phase = "집중기 (D-6개월)"
        intensity = "체성분 개선 + 기초 군 체력(팔굽혀펴기·달리기) 향상"
    else:
        phase = "준비기 (D-6개월 이상)"
        intensity = "생활습관 교정과 유산소 기반 다지기부터 단계적으로"

    # 주간 운동 강도 (fitness_level 반영)
    cardio = {"낮음": "빠르게 걷기 20분", "보통": "가볍게 달리기 25분", "우수": "인터벌 러닝 30분"}[fitness_level]
    strength = {"낮음": "맨몸 스쿼트·무릎 푸시업 2세트", "보통": "스쿼트·푸시업 3세트", "우수": "복합 근력 4세트"}[fitness_level]

    weekly = [
        {"day": "월", "focus": "유산소", "detail": cardio},
        {"day": "화", "focus": "근력(상체)", "detail": strength + " + 플랭크"},
        {"day": "수", "focus": "회복", "detail": "스트레칭·가벼운 걷기 15분"},
        {"day": "목", "focus": "유산소", "detail": cardio},
        {"day": "금", "focus": "근력(하체)", "detail": "런지·스쿼트 3세트 + 코어"},
        {"day": "토", "focus": "군 체력 대비", "detail": "3km 달리기 기록 측정, 팔굽혀펴기 최대 반복"},
        {"day": "일", "focus": "휴식", "detail": "충분한 수면(7시간+), 수분 섭취"},
    ]

    military_prep = [
        "팔굽혀펴기: 2분 내 최대 반복 (주 1회 기록 갱신 목표)",
        "윗몸일으키기: 2분 내 최대 반복",
        "3km 달리기: 목표 페이스 관리 (기초 체력 지표)",
        "규칙적 수면·금주로 입영 전 컨디션 안정화",
    ]

    return {
        "phase": phase,
        "direction": direction,
        "goal": goal,
        "summary": f"{phase} · {intensity}. {goal}.",
        "weekly": weekly,
        "military_prep": military_prep,
    }
