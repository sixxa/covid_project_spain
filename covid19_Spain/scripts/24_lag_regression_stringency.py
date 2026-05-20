from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
from sklearn.linear_model import LinearRegression

from _common import PALETTE, load_owid, save_outputs, save_processed

SLUG = "24_lag_regression_stringency"


def collect_country(df: pd.DataFrame, country: str, lag_days: int = 14) -> pd.DataFrame:
    c = df[df["location"] == country][["date", "new_cases_smoothed", "stringency_index"]].dropna().copy()
    c["case_growth"] = np.log1p(c["new_cases_smoothed"]).diff()
    c["stringency_lagged"] = c["stringency_index"].shift(lag_days)
    c["country"] = country
    return c.dropna()


def main() -> None:
    owid = load_owid()
    data = pd.concat([collect_country(owid, "Spain"), collect_country(owid, "Poland")], ignore_index=True)
    model = LinearRegression().fit(data[["stringency_lagged"]], data["case_growth"])
    data["predicted"] = model.predict(data[["stringency_lagged"]])
    out = data[["date", "country", "stringency_lagged", "case_growth", "predicted"]]
    save_processed(out, SLUG)
    fig = px.scatter(
        out,
        x="stringency_lagged",
        y="case_growth",
        color="country",
        trendline="ols",
        color_discrete_map={"Spain": PALETTE["spain"], "Poland": PALETTE["poland"]},
        title="Lag Regression: Stringency (t-14) vs Case Growth",
    )
    fig.update_layout(template="plotly_white", font={"size": 18})
    fig.update_xaxes(title="Stringency index lagged 14 days")
    fig.update_yaxes(title="log(1+cases) growth")
    save_outputs(fig, SLUG)


if __name__ == "__main__":
    main()
