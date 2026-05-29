from __future__ import annotations

import pandas as pd
import plotly.express as px

from _common import DATA_RAW, require_nonempty, save_outputs, save_processed

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


def _load_real() -> pd.DataFrame:
    """Real Eurostat nama_10r_2gdp: regional GDP (MIO_EUR), % change 2020 vs 2019."""
    df = pd.read_csv(DATA_RAW / "eurostat_regional_gdp.csv")
    df["year"] = pd.to_numeric(df["TIME_PERIOD"].astype(str).str[:4], errors="coerce")
    df = df[
        (df["geo"].isin(_NUTS2_NAMES))
        & (df["unit"] == "MIO_EUR")   # absolute GDP in million euro (the file mixes several units)
    ].dropna(subset=["year", "OBS_VALUE"])
    pivot = df.pivot_table(index="geo", columns="year", values="OBS_VALUE", aggfunc="sum")
    result = pd.DataFrame({
        "geo": pivot.index,
        "gdp_change_2020_pct": (pivot[2020] / pivot[2019] - 1) * 100,
    }).reset_index(drop=True)
    result["comunidad_autonoma"] = result["geo"].map(_NUTS2_NAMES)
    return result[["comunidad_autonoma", "gdp_change_2020_pct"]].dropna().sort_values("gdp_change_2020_pct")


def main() -> None:
    out = require_nonempty(_load_real(), "Eurostat regional GDP").copy()
    title = "Regional GDP Change 2020 vs 2019 (NUTS-2, Eurostat)"
    source = "Eurostat nama_10r_2gdp"

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
