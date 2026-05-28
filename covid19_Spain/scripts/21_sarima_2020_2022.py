from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from prophet import Prophet

from _common import load_owid, save_outputs, save_processed

SLUG = "21_sarima_2020_2022"


def main() -> None:
    df = load_owid()
    sp = (
        df[df["location"] == "Spain"][["date", "new_cases_smoothed"]]
        .dropna()
        .rename(columns={"date": "ds", "new_cases_smoothed": "y"})
    )
    sp["ds"] = pd.to_datetime(sp["ds"])
    sp["floor"] = 0.0
    sp["cap"] = sp["y"].max() * 2

    train = sp[sp["ds"] <= "2022-12-31"].copy()

    model = Prophet(
        growth="logistic",
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        interval_width=0.95,
    )
    model.fit(train)

    future = pd.date_range("2023-01-01", "2024-12-31", freq="D")
    future_df = pd.DataFrame({"ds": future})
    future_df["floor"] = 0.0
    future_df["cap"] = train["cap"].iloc[0]

    forecast = model.predict(future_df)

    actual = sp[sp["ds"].between("2023-01-01", "2024-12-31")].set_index("ds")["y"]

    out = pd.DataFrame({
        "date": future,
        "prediction": forecast["yhat"].clip(lower=0).values,
        "ci_lower": forecast["yhat_lower"].clip(lower=0).values,
        "ci_upper": forecast["yhat_upper"].clip(lower=0).values,
        "actual": actual.reindex(future).values,
    })
    save_processed(out, SLUG)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(future) + list(future[::-1]),
        y=list(out["ci_upper"]) + list(out["ci_lower"][::-1]),
        fill="toself", fillcolor="rgba(77,77,77,0.15)",
        line={"color": "rgba(0,0,0,0)"},
        name="95% CI",
    ))
    fig.add_trace(go.Scatter(
        x=out["date"], y=out["actual"],
        mode="lines", name="Actual", line={"color": "#AA151B", "width": 2},
    ))
    fig.add_trace(go.Scatter(
        x=out["date"], y=out["prediction"],
        mode="lines", name="Forecast (trained to 2022)", line={"color": "#4D4D4D", "width": 2},
    ))
    fig.update_layout(
        template="plotly_white",
        title="Prophet Forecast: Train 2020–2022, Predict 2023–2024",
        font={"size": 18},
        legend={"orientation": "h", "y": -0.2},
    )
    fig.update_yaxes(title="Daily cases (smoothed)", rangemode="tozero")
    save_outputs(fig, SLUG)


if __name__ == "__main__":
    main()
