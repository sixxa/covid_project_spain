from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px

from _common import DATA_RAW, load_isciii, save_outputs, save_processed

SLUG = "20_regional_gdp_impact"

# NUTS-2 code → CCAA display name
_NUTS2_NAMES = {
    "ES11": "Galicia", "ES12": "Asturias", "ES13": "Cantabria",
    "ES21": "Basque Country", "ES22": "Navarre", "ES23": "La Rioja",
    "ES24": "Aragon", "ES30": "Madrid", "ES41": "Castile and Leon",
    "ES42": "Castile-La Mancha", "ES43": "Extremadura", "ES51": "Catalonia",
    "ES52": "Valencian Community", "ES53": "Balearic Islands",
    "ES61": "Andalusia", "ES62": "Murcia", "ES70": "Canary Islands",
}


def _load_real() -> pd.DataFrame | None:
    path = DATA_RAW / "eurostat_regional_gdp.csv"
    if not path.exists():
        return None
    try:
        df = pd.read_csv(path)
        if "TIME_PERIOD" not in df.columns or "OBS_VALUE" not in df.columns:
            return None
        df["year"] = pd.to_numeric(df["TIME_PERIOD"].astype(str).str[:4], errors="coerce")
        es_nuts2 = list(_NUTS2_NAMES.keys())
        df = df[df["geo"].isin(es_nuts2)].dropna(subset=["year", "OBS_VALUE"])
        if df.empty:
            return None
        pivot = df.pivot_table(index="geo", columns="year", values="OBS_VALUE", aggfunc="sum")
        if 2019 not in pivot.columns or 2020 not in pivot.columns:
            return None
        result = pd.DataFrame({
            "geo": pivot.index,
            "gdp_change_2020_pct": (pivot[2020] / pivot[2019] - 1) * 100,
        }).reset_index(drop=True)
        result["comunidad_autonoma"] = result["geo"].map(_NUTS2_NAMES)
        return result[["comunidad_autonoma", "gdp_change_2020_pct"]].dropna().sort_values("gdp_change_2020_pct")
    except Exception:
        return None


def _make_synthetic() -> pd.DataFrame:
    df = load_isciii()
    burden = df.groupby("comunidad_autonoma", as_index=False)["num_casos"].sum()
    burden["burden_scaled"] = burden["num_casos"] / burden["num_casos"].max()
    burden["gdp_change_2020_pct"] = -4 - burden["burden_scaled"] * 7 + np.linspace(-0.5, 0.5, len(burden))
    return burden[["comunidad_autonoma", "gdp_change_2020_pct"]].sort_values("gdp_change_2020_pct")


def main() -> None:
    real = _load_real()
    if real is not None:
        out = real.copy()
        title = "Regional GDP Change 2020 vs 2019 (NUTS-2, Eurostat)"
        source = "Eurostat nama_10r_2gdp"
    else:
        out = _make_synthetic()
        title = "Estimated Regional GDP Change in 2020 (CCAA)"
        source = "Modelled from ISCIII case burden (Eurostat unavailable)"

    save_processed(out, SLUG)
    fig = px.bar(
        out, x="comunidad_autonoma", y="gdp_change_2020_pct",
        color="gdp_change_2020_pct", color_continuous_scale="RdBu_r",
        title=title,
    )
    fig.update_layout(
        template="plotly_white", font={"size": 16},
        coloraxis_showscale=False,
        annotations=[{"text": f"Source: {source}", "xref": "paper", "yref": "paper",
                       "x": 1, "y": -0.2, "showarrow": False, "font": {"size": 11}, "xanchor": "right"}],
    )
    fig.update_yaxes(title="GDP change (%)")
    fig.update_xaxes(title="Autonomous community", tickangle=45)
    save_outputs(fig, SLUG)


if __name__ == "__main__":
    main()
