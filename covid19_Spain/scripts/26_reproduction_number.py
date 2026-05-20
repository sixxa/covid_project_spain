from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from _common import PALETTE, load_owid, save_outputs, save_processed

SLUG = "26_reproduction_number"

_COLORS = {"Spain": PALETTE["spain"], "Poland": PALETTE["poland"]}

# Approximate wave peaks for shaded annotation bands
_WAVES = [
    ("Wave 1", "2020-03-01", "2020-06-30"),
    ("Wave 2", "2020-07-01", "2020-11-30"),
    ("Wave 3–4", "2020-12-01", "2021-07-31"),
    ("Wave 5–6", "2021-08-01", "2022-04-30"),
]


def _get_rt(df: pd.DataFrame, country: str) -> pd.DataFrame:
    sub = df[df["location"] == country].sort_values("date").copy()
    if "reproduction_rate" in sub.columns and sub["reproduction_rate"].notna().any():
        sub = sub[["date", "reproduction_rate"]].dropna()
        sub["rt_smooth"] = sub["reproduction_rate"].rolling(7, min_periods=1).mean()
    else:
        # Proxy: ratio of 7-day smoothed cases to cases 7 days prior
        sub = sub[["date", "new_cases_smoothed"]].dropna()
        shifted = sub["new_cases_smoothed"].shift(7)
        sub["rt_smooth"] = (sub["new_cases_smoothed"] / shifted.replace(0, float("nan"))).clip(0, 4)
        sub["rt_smooth"] = sub["rt_smooth"].rolling(7, min_periods=1).mean()
    sub["country"] = country
    return sub[["date", "country", "rt_smooth"]].dropna()


def main() -> None:
    df = load_owid()
    rows = []
    for country in ["Spain", "Poland"]:
        rows.append(_get_rt(df, country))

    out = pd.concat(rows, ignore_index=True)
    out["date"] = out["date"].astype(str)
    save_processed(out[["date", "country", "rt_smooth"]], SLUG)

    fig = go.Figure()

    # Wave shading
    wave_colors = ["rgba(200,200,255,0.15)", "rgba(255,200,200,0.15)",
                   "rgba(200,255,200,0.15)", "rgba(255,230,150,0.15)"]
    for (label, start, end), fill in zip(_WAVES, wave_colors):
        fig.add_vrect(x0=start, x1=end, fillcolor=fill, line_width=0,
                      annotation_text=label, annotation_position="top left",
                      annotation={"font": {"size": 10}})

    # R=1 threshold line
    fig.add_hline(y=1.0, line_dash="dash", line_color="grey", line_width=1,
                  annotation_text="R = 1", annotation_position="right")

    for country in ["Spain", "Poland"]:
        sub = out[out["country"] == country]
        fig.add_trace(go.Scatter(
            x=sub["date"], y=sub["rt_smooth"],
            mode="lines", name=country,
            line={"color": _COLORS[country], "width": 2},
        ))

    fig.update_layout(
        template="plotly_white",
        title="Effective Reproduction Number R(t): Spain vs Poland",
        font={"size": 18},
        legend={"orientation": "h", "y": -0.2},
        annotations=[{"text": "Source: Our World in Data (reproduction_rate)", "xref": "paper",
                       "yref": "paper", "x": 1, "y": -0.15, "showarrow": False,
                       "font": {"size": 11}, "xanchor": "right"}],
    )
    fig.update_yaxes(title="R(t) — 7-day smoothed")
    save_outputs(fig, SLUG)


if __name__ == "__main__":
    main()
