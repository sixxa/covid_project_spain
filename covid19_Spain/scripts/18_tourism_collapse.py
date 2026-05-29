from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from _common import DATA_RAW, require_nonempty, save_outputs, save_processed

SLUG = "18_tourism_collapse"


def _load_real() -> pd.DataFrame:
    """Real Eurostat tour_occ_arnat: total nights (all residencies) in all accommodation, Spain."""
    df = pd.read_csv(DATA_RAW / "eurostat_tourism.csv")
    mask = (
        (df["geo"] == "ES")
        & (df["c_resid"] == "TOTAL")          # all residencies (domestic + foreign)
        & (df["nace_r2"] == "I551-I553")        # hotels + holiday + camping
        & (df["unit"] == "NR")                  # absolute number of nights (not % change)
    )
    df = df[mask].dropna(subset=["TIME_PERIOD", "OBS_VALUE"])
    df["year"] = pd.to_numeric(df["TIME_PERIOD"].astype(str).str[:4], errors="coerce")
    df = df.dropna(subset=["year"]).sort_values("year")
    df["arrivals_millions"] = df["OBS_VALUE"] / 1_000_000
    return df[["year", "arrivals_millions"]].drop_duplicates("year")


def main() -> None:
    out = require_nonempty(_load_real(), "Eurostat tourism")
    out = out.rename(columns={"year": "date"}).copy()
    out["date"] = out["date"].astype(int).astype(str)
    source = "Eurostat tour_occ_arnat"
    title = "Spain: Total Tourist Nights in All Accommodation (2019–2024)"

    save_processed(out, SLUG)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=out["date"], y=out["arrivals_millions"],
        marker_color="#AA151B", name="Tourist nights (millions)",
    ))
    fig.update_layout(
        template="plotly_white",
        title=title,
        font={"size": 18},
        margin={"l": 60, "r": 30, "t": 80, "b": 90},
        annotations=[{"text": f"Source: {source}", "xref": "paper", "yref": "paper",
                       "x": 0, "y": -0.14, "showarrow": False, "font": {"size": 11}, "xanchor": "left"}],
    )
    fig.update_yaxes(title="Tourist nights (millions)")
    save_outputs(fig, SLUG)


if __name__ == "__main__":
    main()
