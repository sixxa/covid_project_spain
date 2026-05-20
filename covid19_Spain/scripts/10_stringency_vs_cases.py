from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from _common import load_owid, load_oxcgrt, save_outputs, save_processed

SLUG = "10_stringency_vs_cases"


def main() -> None:
    owid = load_owid()
    cases = owid[owid["location"].isin(["Spain", "Poland"])][["date", "location", "new_cases_smoothed"]]
    oxcgrt = load_oxcgrt()
    oxc = oxcgrt[oxcgrt["CountryName"].isin(["Spain", "Poland"])][["Date", "CountryName", "StringencyIndex"]].rename(columns={"Date": "date", "CountryName": "location"})
    merged = pd.merge(cases, oxc, on=["date", "location"], how="inner").dropna()
    save_processed(merged, SLUG)

    sp = merged[merged["location"] == "Spain"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=sp["date"], y=sp["new_cases_smoothed"], name="Spain cases (smoothed)", line={"color": "#AA151B"}))
    fig.add_trace(go.Scatter(x=sp["date"], y=sp["StringencyIndex"], name="Spain stringency", yaxis="y2", line={"color": "#4D4D4D"}))
    fig.update_layout(
        template="plotly_white",
        title="Spain: Cases vs Stringency Index",
        font={"size": 18},
        yaxis={"title": "Cases"},
        yaxis2={"title": "Stringency", "overlaying": "y", "side": "right"},
    )
    save_outputs(fig, SLUG)


if __name__ == "__main__":
    main()
