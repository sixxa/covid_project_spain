from __future__ import annotations

import json

import pandas as pd
import plotly.express as px

from _common import DATA_RAW, apply_layout, load_isciii, save_outputs, save_processed

SLUG = "12_choropleth_waves"


# ISCIII province-level data runs Jan 2020 – Mar 2022, so the buckets cover that span.
def wave_label(date: pd.Timestamp) -> str:
    if date < pd.Timestamp("2020-07-01"):
        return "2020 H1 (first wave)"
    if date < pd.Timestamp("2021-01-01"):
        return "2020 H2"
    if date < pd.Timestamp("2021-07-01"):
        return "2021 H1"
    if date < pd.Timestamp("2022-01-01"):
        return "2021 H2 (Delta)"
    return "2022 (Omicron)"


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
    fig.update_layout(margin={"b": 160})
    # Reposition animation controls so they stay within the iframe viewport.
    # Put play/pause to the left of the slider on a row below, and hide the
    # slider's currentvalue label (it overlapped the play/pause buttons).
    if fig.layout.updatemenus:
        fig.layout.updatemenus[0].update(dict(
            x=0.0, xanchor="left", y=-0.18, yanchor="top",
        ))
    if fig.layout.sliders:
        fig.layout.sliders[0].update(dict(
            x=0.08, len=0.88, y=-0.05, yanchor="top",
            currentvalue=dict(visible=False),
            pad=dict(t=20, b=10),
        ))
    save_outputs(fig, SLUG)


if __name__ == "__main__":
    main()
