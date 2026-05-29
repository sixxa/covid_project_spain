from __future__ import annotations

import plotly.graph_objects as go

from _common import apply_layout, load_owid, save_outputs, save_processed

SLUG = "05_excess_mortality"


def main() -> None:
    df = load_owid()
    # Compare like with like: cumulative ESTIMATED excess deaths vs cumulative REPORTED
    # COVID deaths (both absolute counts). The gap is the undercount.
    es = df[df["location"] == "Spain"][
        ["date", "total_deaths", "excess_mortality_cumulative_absolute"]
    ].copy()
    reported = es[["date", "total_deaths"]].dropna()
    excess = es[["date", "excess_mortality_cumulative_absolute"]].dropna()
    save_processed(
        es.dropna(subset=["total_deaths", "excess_mortality_cumulative_absolute"], how="all"),
        SLUG,
    )
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=reported["date"], y=reported["total_deaths"], mode="lines",
                             name="Reported COVID deaths (cumulative)", line={"color": "#AA151B"}))
    fig.add_trace(go.Scatter(x=excess["date"], y=excess["excess_mortality_cumulative_absolute"],
                             mode="lines", name="Estimated excess deaths (cumulative)",
                             line={"color": "#4D4D4D"}))
    fig = apply_layout(fig, "Spain: Excess Mortality vs Reported COVID-19 Deaths", "Cumulative deaths")
    save_outputs(fig, SLUG)


if __name__ == "__main__":
    main()
