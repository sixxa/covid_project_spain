from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from _common import load_isciii, save_outputs, save_processed

SLUG = "13_ccaa_month_heatmap"


def main() -> None:
    df = load_isciii().dropna(subset=["fecha"]).copy()
    df["month"] = df["fecha"].dt.to_period("M").astype(str)
    agg = df.groupby(["comunidad_autonoma", "month"], as_index=False)["num_casos"].sum()
    save_processed(agg, SLUG)

    pivot = agg.pivot(index="comunidad_autonoma", columns="month", values="num_casos").fillna(0)

    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale="Reds",
        colorbar={"title": "Cases"},
        hovertemplate="Month: %{x}<br>Region: %{y}<br>Cases: %{z:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        template="plotly_white",
        title="Cases by Autonomous Community and Month",
        font={"size": 14},
        xaxis={"title": "", "tickangle": -45},
        yaxis={"title": ""},
        margin={"l": 180, "r": 30, "t": 80, "b": 120},
        height=700,
    )
    save_outputs(fig, SLUG)


if __name__ == "__main__":
    main()
