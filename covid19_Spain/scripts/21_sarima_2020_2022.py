from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from statsmodels.tsa.statespace.sarimax import SARIMAX

from _common import load_owid, save_outputs, save_processed

SLUG = "21_sarima_2020_2022"


def main() -> None:
    df = load_owid()
    sp = (
        df[df["location"] == "Spain"][["date", "new_cases_smoothed"]]
        .dropna()
        .set_index("date")
        .asfreq("D")
        .ffill()
    )
    train = sp.loc[:"2022-12-31", "new_cases_smoothed"]
    model = SARIMAX(
        train, order=(1, 1, 1), seasonal_order=(1, 0, 1, 7),
        enforce_stationarity=False, enforce_invertibility=False,
    )
    fitted = model.fit(disp=False)

    forecast_idx = pd.date_range("2023-01-01", "2024-12-31", freq="D")
    pred = fitted.get_forecast(steps=len(forecast_idx))
    ci = pred.conf_int()
    lower = ci.iloc[:, 0].values
    upper = ci.iloc[:, 1].values

    out = pd.DataFrame({
        "date": forecast_idx,
        "prediction": pred.predicted_mean.values,
        "actual": sp.loc[forecast_idx, "new_cases_smoothed"].values,
        "ci_lower": lower,
        "ci_upper": upper,
    })
    save_processed(out, SLUG)

    fig = go.Figure()
    # Confidence band (drawn first so lines appear on top)
    fig.add_trace(go.Scatter(
        x=list(forecast_idx) + list(forecast_idx[::-1]),
        y=list(upper) + list(lower[::-1]),
        fill="toself", fillcolor="rgba(77,77,77,0.15)",
        line={"color": "rgba(0,0,0,0)"},
        name="95% CI", showlegend=True,
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
        title="SARIMA Forecast: Train 2020–2022, Predict 2023–2024",
        font={"size": 18},
        legend={"orientation": "h", "y": -0.2},
    )
    fig.update_yaxes(title="Daily cases (smoothed)")
    save_outputs(fig, SLUG)


if __name__ == "__main__":
    main()
