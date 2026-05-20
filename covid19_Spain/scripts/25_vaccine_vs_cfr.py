from __future__ import annotations

import numpy as np
import plotly.express as px

from _common import load_owid, save_outputs, save_processed

SLUG = "25_vaccine_vs_cfr"


def main() -> None:
    df = load_owid()
    sp = df[df["location"] == "Spain"][["date", "new_deaths_smoothed", "new_cases_smoothed", "people_vaccinated_per_hundred"]].dropna().copy()
    sp["cfr_proxy"] = sp["new_deaths_smoothed"] / sp["new_cases_smoothed"].clip(lower=1)
    sp["month"] = sp["date"].dt.to_period("M").astype(str)
    monthly = sp.groupby("month", as_index=False)[["people_vaccinated_per_hundred", "cfr_proxy"]].mean()
    save_processed(monthly, SLUG)
    fig = px.scatter(
        monthly,
        x="people_vaccinated_per_hundred",
        y="cfr_proxy",
        color="month",
        trendline="ols",
        title="Spain: Vaccination Coverage vs CFR Proxy",
    )
    fig.update_layout(template="plotly_white", font={"size": 16})
    fig.update_xaxes(title="People vaccinated per hundred")
    fig.update_yaxes(title="CFR proxy")
    save_outputs(fig, SLUG)


if __name__ == "__main__":
    main()
