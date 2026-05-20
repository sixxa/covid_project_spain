from __future__ import annotations

import json

import pandas as pd
import plotly.express as px

from _common import DATA_RAW, apply_layout, load_isciii, save_outputs, save_processed

SLUG = "12_choropleth_waves"


def wave_label(date: pd.Timestamp) -> str:
    if date < pd.Timestamp("2021-01-01"):
        return "Wave_2020"
    if date < pd.Timestamp("2022-01-01"):
        return "Wave_2021"
    if date < pd.Timestamp("2023-01-01"):
        return "Wave_2022"
    return "Wave_2023_2024"


def main() -> None:
    df = load_isciii().dropna(subset=["fecha"]).copy()
    df["wave"] = df["fecha"].map(wave_label)
    agg = (
        df.groupby(["comunidad_autonoma", "wave"], as_index=False)["num_casos"]
        .sum()
        .rename(columns={"num_casos": "cases"})
    )
    save_processed(agg, SLUG)

    geojson = json.loads((DATA_RAW / "spain_ccaa.geojson").read_text(encoding="utf-8"))
    fig = px.choropleth_map(
        agg,
        geojson=geojson,
        locations="comunidad_autonoma",
        featureidkey="properties.name",
        color="cases",
        animation_frame="wave",
        color_continuous_scale="Reds",
        center={"lat": 40.2, "lon": -3.5},
        zoom=4.3,
    )
    fig = apply_layout(fig, "Spain Regional Case Burden by Pandemic Wave", "Cases")
    fig.update_layout(margin={"b": 140})
    # Reposition animation controls so they stay within the iframe viewport
    if fig.layout.updatemenus:
        fig.layout.updatemenus[0].update(dict(x=0.05, xanchor="left", y=0, yanchor="top"))
    if fig.layout.sliders:
        fig.layout.sliders[0].update(dict(x=0.1, len=0.85, y=0, yanchor="top"))
    save_outputs(fig, SLUG)


if __name__ == "__main__":
    main()
