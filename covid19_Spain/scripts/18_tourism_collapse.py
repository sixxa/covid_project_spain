from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from _common import DATA_RAW, save_outputs, save_processed

SLUG = "18_tourism_collapse"


def _load_real() -> pd.DataFrame | None:
    path = DATA_RAW / "eurostat_tourism.csv"
    if not path.exists():
        return None
    try:
        df = pd.read_csv(path)
        if "TIME_PERIOD" not in df.columns or "OBS_VALUE" not in df.columns:
            return None
        # Use total arrivals (all residencies) for nace I551-I553 (all accommodation)
        mask = (df["geo"] == "ES") & (df.get("nace_r2", "I551-I553") == "I551-I553")
        if "c_resid" in df.columns:
            mask = mask & (df["c_resid"] == "TOTAL")
        df = df[mask].dropna(subset=["TIME_PERIOD", "OBS_VALUE"])
        if df.empty:
            return None
        df["year"] = pd.to_numeric(df["TIME_PERIOD"].astype(str).str[:4], errors="coerce")
        df = df.dropna(subset=["year"]).sort_values("year")
        df["arrivals_millions"] = df["OBS_VALUE"] / 1_000_000
        return df[["year", "arrivals_millions"]].drop_duplicates("year")
    except Exception:
        return None


def _make_synthetic() -> pd.DataFrame:
    dates = pd.date_range("2019-01-01", "2024-12-01", freq="MS")
    rows = []
    penalty = {2019: 1.0, 2020: 0.25, 2021: 0.55, 2022: 0.85, 2023: 0.97, 2024: 1.0}
    for dt in dates:
        seasonal = 6 + 4 * np.sin((dt.month - 1) / 12 * 2 * np.pi)
        arrivals = max(seasonal * penalty.get(dt.year, 1.0), 0.2)
        rows.append({"date": dt, "arrivals_millions": arrivals})
    return pd.DataFrame(rows)


def main() -> None:
    real = _load_real()
    if real is not None:
        out = real.rename(columns={"year": "date"}).copy()
        out["date"] = out["date"].astype(int).astype(str)
        source = "Eurostat tour_occ_arnat"
        title = "Spain: Total Tourist Nights in All Accommodation (2019–2024)"
        chart_type = "bar"
    else:
        out = _make_synthetic()
        out["date"] = out["date"].dt.year.astype(str)
        out = out.groupby("date", as_index=False)["arrivals_millions"].sum()
        source = "Modelled estimate (Eurostat unavailable)"
        title = "Spain: Estimated Tourism Arrivals (2019–2024)"
        chart_type = "bar"

    save_processed(out, SLUG)

    fig = go.Figure()
    if chart_type == "bar":
        fig.add_trace(go.Bar(
            x=out["date"], y=out["arrivals_millions"],
            marker_color="#AA151B", name="Tourist nights (millions)",
        ))
    fig.update_layout(
        template="plotly_white",
        title=title,
        font={"size": 18},
        annotations=[{"text": f"Source: {source}", "xref": "paper", "yref": "paper",
                       "x": 1, "y": -0.12, "showarrow": False, "font": {"size": 11}, "xanchor": "right"}],
    )
    fig.update_yaxes(title="Tourist nights (millions)")
    save_outputs(fig, SLUG)


if __name__ == "__main__":
    main()
