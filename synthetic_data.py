"""
합성 샘플 데이터 생성 모듈
================================

실제 KNHANES(국민건강영양조사) 원자료는 개인정보/이용승인 이슈가 있어
본 MVP에서는 질병관리청이 공개한 연령대별 요약 통계(평균·표준편차)에
근사하도록 '합성(synthetic) 샘플 데이터'를 생성해 시연한다.

- 목적: 국가 평균 대비 개인 건강 벤치마크 시연
- 근거: KNHANES 공표 요약통계 범위를 참고한 근사값 (실제 원자료 아님)
- 재현성: numpy 시드 고정으로 항상 동일한 데이터 생성

방위사업청 연계 시나리오용 '국방 웨어러블' 시계열도 함께 생성한다.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# 재현 가능한 데이터를 위해 시드 고정
_SEED = 20260706


# KNHANES 공표 요약통계에 근사한 연령대별 파라미터 (남성 기준, 근사값)
# 참고: 실제 원자료가 아닌, 공개 통계 범위를 참고한 근사치이다.
_AGE_GROUP_PARAMS = {
    "18-24": {
        "height": (173.5, 6.0),   # cm (평균, 표준편차)
        "weight": (72.0, 12.5),   # kg
        "sbp": (118.0, 11.0),     # 수축기 혈압 mmHg
        "waist": (81.0, 9.5),     # 허리둘레 cm
        "n": 900,
    },
    "25-29": {
        "height": (174.0, 6.0),
        "weight": (75.5, 13.0),
        "sbp": (120.0, 11.5),
        "waist": (84.0, 10.0),
        "n": 800,
    },
    "30-39": {
        "height": (173.0, 6.2),
        "weight": (77.0, 13.5),
        "sbp": (122.0, 12.0),
        "waist": (86.5, 10.5),
        "n": 1000,
    },
}


def generate_population() -> pd.DataFrame:
    """연령대별 합성 인구 표본을 생성해 하나의 DataFrame으로 반환한다."""
    rng = np.random.default_rng(_SEED)
    frames = []

    for age_group, p in _AGE_GROUP_PARAMS.items():
        n = p["n"]
        height = rng.normal(*p["height"], n)
        # 체중은 키와 양의 상관을 갖도록 약간의 상관 부여
        weight = rng.normal(*p["weight"], n) + (height - p["height"][0]) * 0.35
        sbp = rng.normal(*p["sbp"], n)
        waist = rng.normal(*p["waist"], n) + (weight - p["weight"][0]) * 0.25

        height = np.clip(height, 150, 196)
        weight = np.clip(weight, 42, 140)
        sbp = np.clip(sbp, 95, 175)
        waist = np.clip(waist, 62, 125)

        bmi = weight / (height / 100) ** 2

        frames.append(
            pd.DataFrame(
                {
                    "age_group": age_group,
                    "height": height.round(1),
                    "weight": weight.round(1),
                    "bmi": bmi.round(1),
                    "sbp": sbp.round(0),
                    "waist": waist.round(1),
                }
            )
        )

    return pd.concat(frames, ignore_index=True)


def benchmark_stats(pop: pd.DataFrame, age_group: str) -> dict:
    """특정 연령대의 지표별 평균/표준편차/백분위 기준을 반환한다."""
    sub = pop[pop["age_group"] == age_group]
    stats = {}
    for col in ["bmi", "sbp", "waist", "weight"]:
        stats[col] = {
            "mean": float(sub[col].mean()),
            "std": float(sub[col].std()),
            "p25": float(sub[col].quantile(0.25)),
            "p50": float(sub[col].quantile(0.50)),
            "p75": float(sub[col].quantile(0.75)),
        }
    return stats


def percentile_of(pop: pd.DataFrame, age_group: str, col: str, value: float) -> float:
    """같은 연령대 표본 대비 사용자 값이 몇 백분위인지 반환한다 (0-100)."""
    sub = pop[pop["age_group"] == age_group][col]
    return float((sub < value).mean() * 100)


def generate_wearable(days: int = 14, fitness_level: str = "보통") -> pd.DataFrame:
    """
    방위사업청 연계 시나리오용 '국방 웨어러블' 합성 시계열 생성.

    입영 전 청년(또는 현역 병사)이 착용한 웨어러블에서 수집될 법한
    일일 걸음 수 / 안정시 심박 / 수면시간 / 활동칼로리를 근사 생성한다.
    """
    rng = np.random.default_rng(_SEED + 7)

    base = {
        "낮음": {"steps": 4500, "rhr": 78, "sleep": 6.2, "kcal": 1900},
        "보통": {"steps": 7500, "rhr": 70, "sleep": 6.8, "kcal": 2250},
        "우수": {"steps": 11000, "rhr": 60, "sleep": 7.4, "kcal": 2650},
    }[fitness_level]

    dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=days)
    steps = rng.normal(base["steps"], base["steps"] * 0.18, days).clip(1500, 22000)
    rhr = rng.normal(base["rhr"], 4.0, days).clip(48, 95)
    sleep = rng.normal(base["sleep"], 0.7, days).clip(3.5, 9.5)
    kcal = rng.normal(base["kcal"], 220, days).clip(1400, 3600)

    return pd.DataFrame(
        {
            "date": dates,
            "steps": steps.round(0).astype(int),
            "resting_hr": rhr.round(0).astype(int),
            "sleep_hours": sleep.round(1),
            "active_kcal": kcal.round(0).astype(int),
        }
    )
