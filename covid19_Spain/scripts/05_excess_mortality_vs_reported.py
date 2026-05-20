from __future__ import annotations

import plotly.graph_objects as go

from _common import apply_layout, load_owid, save_outputs, save_processed

SLUG = "05_excess_mortality"


def main() -> None:
    df = load_owid()
    es = df[df["location"] == "Spain"][["date", "new_deaths", "excess_mortality"]].dropna()
    es["excess_proxy"] = es["excess_mortality"]
    out = es[["date", "new_deaths", "excess_proxy"]]
    save_processed(out, SLUG)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=out["date"], y=out["new_deaths"], mode="lines", name="Reported COVID deaths", line={"color": "#AA151B"}))
    fig.add_trace(go.Scatter(x=out["date"], y=out["excess_proxy"], mode="lines", name="Excess mortality proxy", line={"color": "#4D4D4D"}))
    fig = apply_layout(fig, "Spain: Excess Mortality vs Reported COVID-19 Deaths", "Daily deaths")
    save_outputs(fig, SLUG)


if __name__ == "__main__":
    main()
