from __future__ import annotations

import pandas as pd
import plotly.express as px

from _common import load_owid, save_outputs, save_processed

SLUG = "16_wave_decomposition"


def wave(dt: pd.Timestamp) -> str:
    if dt < pd.Timestamp("2021-01-01"):
        return "Wave_1_2020"
    if dt < pd.Timestamp("2022-01-01"):
        return "Wave_2_2021"
    if dt < pd.Timestamp("2023-01-01"):
        return "Wave_3_2022"
    return "Wave_4_2023_2024"


def main() -> None:
    df = load_owid()
    sp = df[df["location"] == "Spain"][["date", "new_cases_smoothed"]].dropna()
    sp["wave"] = sp["date"].map(wave)
    agg = sp.groupby("wave", as_index=False)["new_cases_smoothed"].sum().rename(columns={"new_cases_smoothed": "cases"})
    save_processed(agg, SLUG)
    fig = px.pie(agg, values="cases", names="wave", title="Spain Cases by Pandemic Wave")
    fig.update_layout(template="plotly_white", font={"size": 18})
    save_outputs(fig, SLUG)


if __name__ == "__main__":
    main()
