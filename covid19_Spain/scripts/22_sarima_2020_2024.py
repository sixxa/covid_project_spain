from __future__ import annotations

from typing import Tuple

import pandas as pd
import plotly.graph_objects as go
from statsmodels.tsa.statespace.sarimax import SARIMAX

from _common import load_owid, save_outputs, save_processed

SLUG = "22_sarima_2020_2024"


def fit_forecast(
    series: pd.Series, end_train: str, horizon_days: int
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    train = series.loc[:end_train]
    model = SARIMAX(
        train, order=(1, 1, 1), seasonal_order=(1, 0, 1, 7),
        enforce_stationarity=False, enforce_invertibility=False,
    )
    fitted = model.fit(disp=False)
    pred = fitted.get_forecast(steps=horizon_days)
    ci = pred.conf_int()
    return pd.Series(pred.predicted_mean.values), pd.Series(ci.iloc[:, 0].values), pd.Series(ci.iloc[:, 1].values)


def main() -> None:
    df = load_owid()
    sp = (
        df[df["location"] == "Spain"][["date", "new_cases_smoothed"]]
        .dropna()
        .set_index("date")
        .asfreq("D")
        .ffill()
    )
    idx = pd.date_range("2025-01-01", "2025-12-31", freq="D")
    pt_short, lo_short, hi_short = fit_forecast(sp["new_cases_smoothed"], "2022-12-31", len(idx))
    pt_full, lo_full, hi_full = fit_forecast(sp["new_cases_smoothed"], "2024-12-31", len(idx))

    out = pd.DataFrame({
        "date": idx,
        "forecast_train_2022": pt_short.values,
        "ci_lower_2022": lo_short.values,
        "ci_upper_2022": hi_short.values,
        "forecast_train_2024": pt_full.values,
        "ci_lower_2024": lo_full.values,
        "ci_upper_2024": hi_full.values,
    })
    save_processed(out, SLUG)

    color_short = "#AA151B"
    color_full = "#4D4D4D"

    fig = go.Figure()
    # CI bands first
    fig.add_trace(go.Scatter(
        x=list(idx) + list(idx[::-1]),
        y=list(hi_short.values) + list(lo_short.values[::-1]),
        fill="toself", fillcolor="rgba(170,21,27,0.12)",
        line={"color": "rgba(0,0,0,0)"},
        name="95% CI (2022 window)", showlegend=True,
    ))
    fig.add_trace(go.Scatter(
        x=list(idx) + list(idx[::-1]),
        y=list(hi_full.values) + list(lo_full.values[::-1]),
        fill="toself", fillcolor="rgba(77,77,77,0.12)",
        line={"color": "rgba(0,0,0,0)"},
        name="95% CI (2024 window)", showlegend=True,
    ))
    fig.add_trace(go.Scatter(
        x=out["date"], y=out["forecast_train_2022"],
        name="Train window: 2020–2022", line={"color": color_short, "width": 2},
    ))
    fig.add_trace(go.Scatter(
        x=out["date"], y=out["forecast_train_2024"],
        name="Train window: 2020–2024", line={"color": color_full, "width": 2},
    ))
    fig.update_layout(
        template="plotly_white",
        title="SARIMA 2025 Forecast: Sensitivity to Training Window",
        font={"size": 18},
        legend={"orientation": "h", "y": -0.2},
    )
    fig.update_yaxes(title="Predicted daily cases")
    save_outputs(fig, SLUG)


if __name__ == "__main__":
    main()
