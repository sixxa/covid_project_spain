from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from _common import DATA_RAW, PALETTE, require_nonempty, save_outputs, save_processed

SLUG = "19_unemployment_es_pl"

_GEO_NAMES = {"ES": "Spain", "PL": "Poland"}
_COLORS = {"Spain": PALETTE["spain"], "Poland": PALETTE["poland"]}


def _load_real() -> pd.DataFrame:
    """Real Eurostat une_rt_m: monthly seasonally-adjusted total unemployment rate."""
    df = pd.read_csv(DATA_RAW / "eurostat_unemployment.csv")
    df["date"] = pd.to_datetime(df["TIME_PERIOD"], format="%Y-%m", errors="coerce")
    mask = (
        df["geo"].isin(["ES", "PL"])
        & (df["unit"] == "PC_ACT")    # % of active population
        & (df["sex"] == "T")          # total
        & (df["age"] == "TOTAL")
        & (df["s_adj"] == "SA")       # seasonally adjusted
    )
    df = df[mask].dropna(subset=["date", "OBS_VALUE"])
    df["country"] = df["geo"].map(_GEO_NAMES)
    return df.sort_values("date")[["date", "country", "OBS_VALUE"]].rename(
        columns={"OBS_VALUE": "unemployment_rate"}
    )


def main() -> None:
    out = require_nonempty(_load_real(), "Eurostat unemployment").copy()
    source = "Eurostat une_rt_m"
    title = "Unemployment Rate: Spain vs Poland (2019–2024)"

    out["date"] = out["date"].astype(str)
    save_processed(out, SLUG)

    fig = go.Figure()
    for country in ["Spain", "Poland"]:
        sub = out[out["country"] == country]
        fig.add_trace(go.Scatter(
            x=sub["date"], y=sub["unemployment_rate"],
            mode="lines", name=country,
            line={"color": _COLORS[country], "width": 2},
        ))
    fig.update_layout(
        template="plotly_white",
        title=title,
        font={"size": 18},
        legend={"orientation": "h", "yanchor": "top", "y": -0.18,
                "xanchor": "left", "x": 0},
        margin={"l": 60, "r": 30, "t": 80, "b": 130},
        annotations=[{"text": f"Source: {source}", "xref": "paper", "yref": "paper",
                       "x": 0, "y": -0.32, "showarrow": False, "font": {"size": 11}, "xanchor": "left"}],
    )
    fig.update_yaxes(title="Unemployment rate (%)")
    save_outputs(fig, SLUG)


if __name__ == "__main__":
    main()
