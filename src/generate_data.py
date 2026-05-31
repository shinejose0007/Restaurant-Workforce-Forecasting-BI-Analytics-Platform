"""Generate synthetic restaurant operations data.

The generated data is not real customer data. It is designed to simulate realistic
patterns for revenue, orders, staffing, labor cost, weather, holidays and promotions.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass

import numpy as np
import pandas as pd

try:
    from src.config import RAW_DATA_PATH, RANDOM_SEED
except ModuleNotFoundError:
    from config import RAW_DATA_PATH, RANDOM_SEED


@dataclass
class GenerationConfig:
    n_restaurants: int = 60
    start_date: str = "2024-01-01"
    end_date: str = "2024-12-31"
    seed: int = RANDOM_SEED


def _weather_for_season(month: int, rng: np.random.Generator) -> tuple[str, float]:
    if month in [12, 1, 2]:
        temp = rng.normal(4, 5)
        weather = rng.choice(["sunny", "cloudy", "rainy", "snowy"], p=[0.20, 0.42, 0.28, 0.10])
    elif month in [3, 4, 5]:
        temp = rng.normal(13, 5)
        weather = rng.choice(["sunny", "cloudy", "rainy"], p=[0.42, 0.38, 0.20])
    elif month in [6, 7, 8]:
        temp = rng.normal(23, 5)
        weather = rng.choice(["sunny", "cloudy", "rainy"], p=[0.60, 0.25, 0.15])
    else:
        temp = rng.normal(12, 5)
        weather = rng.choice(["sunny", "cloudy", "rainy"], p=[0.32, 0.45, 0.23])
    return weather, round(float(temp), 1)


def generate_restaurant_data(config: GenerationConfig) -> pd.DataFrame:
    rng = np.random.default_rng(config.seed)
    dates = pd.date_range(config.start_date, config.end_date, freq="D")
    cities = ["Karlsruhe", "Darmstadt", "Mannheim", "Stuttgart", "Frankfurt", "Heidelberg", "Freiburg"]
    restaurant_types = ["fast_food", "casual_dining", "coffee_shop", "delivery_focused", "family_restaurant"]

    restaurant_rows = []
    for i in range(1, config.n_restaurants + 1):
        restaurant_rows.append({
            "restaurant_id": f"R{i:04d}",
            "city": rng.choice(cities),
            "restaurant_type": rng.choice(restaurant_types, p=[0.34, 0.22, 0.18, 0.14, 0.12]),
            "base_daily_orders": int(np.clip(rng.normal(210, 55), 70, 420)),
            "avg_order_value_base": float(np.clip(rng.normal(13.5, 2.5), 7.5, 25)),
            "hourly_wage": float(np.clip(rng.normal(15.5, 2.5), 12, 24)),
            "base_productivity": float(np.clip(rng.normal(82, 14), 45, 125)),
        })
    restaurants = pd.DataFrame(restaurant_rows)

    rows = []
    public_holidays = set(pd.to_datetime([
        "2024-01-01", "2024-03-29", "2024-04-01", "2024-05-01", "2024-05-09",
        "2024-05-20", "2024-10-03", "2024-12-25", "2024-12-26"
    ]))

    for _, rest in restaurants.iterrows():
        trend = rng.normal(0.0006, 0.00035)
        restaurant_random_effect = rng.normal(1.0, 0.10)
        for day_idx, date in enumerate(dates):
            weekday = date.weekday()
            month = date.month
            is_weekend = weekday >= 5
            is_holiday = date in public_holidays
            weather, temperature = _weather_for_season(month, rng)
            promotion_active = rng.random() < (0.10 if not is_weekend else 0.16)

            weekday_factor = [0.88, 0.92, 0.98, 1.03, 1.18, 1.32, 1.12][weekday]
            season_factor = 1.0 + 0.10 * np.sin((month - 1) / 12 * 2 * np.pi)
            weather_factor = {"sunny": 1.05, "cloudy": 0.98, "rainy": 0.93, "snowy": 0.82}.get(weather, 1.0)
            holiday_factor = 0.76 if is_holiday else 1.0
            promo_factor = 1.18 if promotion_active else 1.0
            trend_factor = 1 + trend * day_idx

            expected_orders = rest["base_daily_orders"] * weekday_factor * season_factor * weather_factor * holiday_factor * promo_factor * trend_factor * restaurant_random_effect
            orders = int(max(20, rng.normal(expected_orders, expected_orders * 0.11)))
            avg_order_value = max(5.5, rng.normal(rest["avg_order_value_base"], 1.3))
            revenue = round(orders * avg_order_value, 2)

            delivery_share = float(np.clip(rng.normal(0.32 if rest["restaurant_type"] == "delivery_focused" else 0.22, 0.08), 0.05, 0.70))
            delivery_orders = int(orders * delivery_share)
            dine_in_orders = orders - delivery_orders

            staff_hours_expected = revenue / rest["base_productivity"]
            staff_hours = float(max(12, rng.normal(staff_hours_expected, max(3, staff_hours_expected * 0.10))))
            labor_cost = round(staff_hours * rest["hourly_wage"], 2)
            productivity_per_hour = round(revenue / staff_hours, 2)
            personnel_cost_ratio = round(labor_cost / revenue, 4) if revenue else np.nan

            rows.append({
                "date": date.date().isoformat(),
                "restaurant_id": rest["restaurant_id"],
                "city": rest["city"],
                "restaurant_type": rest["restaurant_type"],
                "weekday": weekday,
                "weekday_name": date.day_name(),
                "month": month,
                "is_weekend": int(is_weekend),
                "is_holiday": int(is_holiday),
                "weather": weather,
                "temperature": temperature,
                "promotion_active": int(promotion_active),
                "orders": orders,
                "delivery_orders": delivery_orders,
                "dine_in_orders": dine_in_orders,
                "avg_order_value": round(avg_order_value, 2),
                "revenue": revenue,
                "staff_hours": round(staff_hours, 2),
                "hourly_wage": round(rest["hourly_wage"], 2),
                "labor_cost": labor_cost,
                "productivity_per_hour": productivity_per_hour,
                "personnel_cost_ratio": personnel_cost_ratio,
            })

    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--restaurants", type=int, default=60, help="Number of restaurants to simulate")
    parser.add_argument("--start", default="2024-01-01")
    parser.add_argument("--end", default="2024-12-31")
    args = parser.parse_args()

    config = GenerationConfig(n_restaurants=args.restaurants, start_date=args.start, end_date=args.end)
    df = generate_restaurant_data(config)
    RAW_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(RAW_DATA_PATH, index=False)
    print(f"Generated {len(df):,} rows at {RAW_DATA_PATH}")


if __name__ == "__main__":
    main()
