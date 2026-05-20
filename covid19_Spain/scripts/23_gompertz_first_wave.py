from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.optimize import curve_fit

from _common import load_owid, save_outputs, save_processed

SLUG = "23_gompertz_first_wave"


def gompertz(x: np.ndarray, a: float, b: float, c: float) -> np.ndarray:
    return a * np.exp(-b * np.exp(-c * x))


def main() -> None:
    df = load_owid()
    sp = df[df["location"] == "Spain"][["date", "total_cases"]].dropna()
    wave = sp[(sp["date"] >= "2020-03-01") & (sp["date"] <= "2020-05-31")].copy()
    wave["x"] = np.arange(len(wave))
    params, _ = curve_fit(gompertz, wave["x"].values, wave["total_cases"].values, p0=[wave["total_cases"].max() * 1.2, 5, 0.1], maxfev=20000)
    wave["fit"] = gompertz(wave["x"].values, *params)
    out = wave[["date", "total_cases", "fit"]]
    save_processed(out, SLUG)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=out["date"], y=out["total_cases"], mode="lines", name="Observed cumulative cases", line={"color": "#AA151B"}))
    fig.add_trace(go.Scatter(x=out["date"], y=out["fit"], mode="lines", name="Gompertz fit", line={"color": "#4D4D4D"}))
    fig.update_layout(template="plotly_white", title="Gompertz Fit on Spain First Wave (Mar-May 2020)", font={"size": 18})
    fig.update_yaxes(title="Cumulative cases")
    save_outputs(fig, SLUG)


if __name__ == "__main__":
    main()
