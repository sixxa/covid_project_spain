from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from _common import PALETTE, load_owid, save_outputs, save_processed

SLUG = "27_cfr_by_wave"

_COLORS = {"Spain": PALETTE["spain"], "Poland": PALETTE["poland"]}

_WAVE_PERIODS = [
    ("Wave 1\n(Mar–Jun 2020)", "2020-03-01", "2020-06-30"),
    ("Wave 2\n(Jul–Nov 2020)", "2020-07-01", "2020-11-30"),
    ("Waves 3–4\n(Dec 2020–Jul 2021)", "2020-12-01", "2021-07-31"),
    ("Waves 5–6\n(Aug 2021–Apr 2022)", "2021-08-01", "2022-04-30"),
    ("Endemic\n(May 2022–2024)", "2022-05-01", "2024-12-31"),
]


def compute_wave_cfr(df: pd.DataFrame, country: str) -> pd.DataFrame:
    sub = df[df["location"] == country][["date", "new_deaths_smoothed", "new_cases_smoothed"]].dropna()
    records = []
    for label, start, end in _WAVE_PERIODS:
        mask = (sub["date"] >= start) & (sub["date"] <= end)
        period = sub[mask]
        total_cases = period["new_cases_smoothed"].sum()
        total_deaths = period["new_deaths_smoothed"].sum()
        cfr = (total_deaths / total_cases * 100) if total_cases > 0 else 0
        records.append({"wave": label.replace("\n", " "), "country": country, "cfr_pct": round(cfr, 3)})
    return pd.DataFrame(records)


def main() -> None:
    df = load_owid()
    parts = [compute_wave_cfr(df, c) for c in ["Spain", "Poland"]]
    out = pd.concat(parts, ignore_index=True)
    save_processed(out, SLUG)

    fig = go.Figure()
    wave_labels = [w[0].replace("\n", " ") for w in _WAVE_PERIODS]
    for country in ["Spain", "Poland"]:
        sub = out[out["country"] == country]
        sub = sub.set_index("wave").reindex(wave_labels).reset_index()
        fig.add_trace(go.Bar(
            x=sub["wave"], y=sub["cfr_pct"],
            name=country, marker_color=_COLORS[country],
        ))

    fig.update_layout(
        template="plotly_white",
        title="Case Fatality Rate by Wave: Spain vs Poland",
        barmode="group",
        font={"size": 16},
        legend={"orientation": "h", "y": -0.25},
        annotations=[{"text": "Source: Our World in Data · CFR = deaths / cases (smoothed totals per wave)",
                       "xref": "paper", "yref": "paper", "x": 1, "y": -0.2,
                       "showarrow": False, "font": {"size": 11}, "xanchor": "right"}],
    )
    fig.update_yaxes(title="CFR (%)")
    fig.update_xaxes(title="")
    save_outputs(fig, SLUG)


if __name__ == "__main__":
    main()
