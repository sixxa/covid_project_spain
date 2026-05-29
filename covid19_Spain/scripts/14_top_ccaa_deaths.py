from __future__ import annotations

import plotly.express as px

from _common import load_isciii, save_outputs, save_processed

SLUG = "14_top_ccaa_deaths"


def main() -> None:
    df = load_isciii()
    agg = (
        df.groupby("comunidad_autonoma", as_index=False)["num_def"]
        .sum()
        .rename(columns={"num_def": "deaths"})
        .sort_values("deaths", ascending=False)
        .head(10)
    )
    out = agg[["comunidad_autonoma", "deaths"]]
    save_processed(out, SLUG)
    fig = px.bar(
        out.sort_values("deaths"), x="deaths", y="comunidad_autonoma", orientation="h",
        color="deaths", color_continuous_scale="Reds",
        title="Top 10 Autonomous Communities by Reported COVID-19 Deaths (ISCIII, 2020–Mar 2022)",
    )
    fig.update_layout(template="plotly_white", font={"size": 18}, coloraxis_showscale=False)
    fig.update_xaxes(title="Reported deaths")
    fig.update_yaxes(title="")
    save_outputs(fig, SLUG)


if __name__ == "__main__":
    main()
