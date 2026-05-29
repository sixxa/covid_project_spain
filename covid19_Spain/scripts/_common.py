from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
FIG_HTML = ROOT / "figures" / "html"
FIG_STATIC = ROOT / "figures" / "static"

PALETTE = {
    "spain": "#AA151B",
    "poland": "#0057B8",
    "neutral": "#4D4D4D",
    "global": "#6C757D",
    "accent": "#F1BF00",
}

# ISCIII province (provincia_iso) -> autonomous community, using the exact Spanish
# names found in data/raw/spain_ccaa.geojson (properties.name) so regional plots can
# join straight onto the choropleth geometry. "NC" (no consta / unknown) is dropped.
PROVINCIA_TO_CCAA = {
    "A": "Valencia", "AB": "Castilla-La Mancha", "AL": "Andalucia", "AV": "Castilla-Leon",
    "B": "Cataluña", "BA": "Extremadura", "BI": "Pais Vasco", "BU": "Castilla-Leon",
    "C": "Galicia", "CA": "Andalucia", "CC": "Extremadura", "CE": "Ceuta",
    "CO": "Andalucia", "CR": "Castilla-La Mancha", "CS": "Valencia", "CU": "Castilla-La Mancha",
    "GC": "Canarias", "GI": "Cataluña", "GR": "Andalucia", "GU": "Castilla-La Mancha",
    "H": "Andalucia", "HU": "Aragon", "J": "Andalucia", "L": "Cataluña",
    "LE": "Castilla-Leon", "LO": "La Rioja", "LU": "Galicia", "M": "Madrid",
    "MA": "Andalucia", "ML": "Melilla", "MU": "Murcia", "NA": "Navarra",
    "O": "Asturias", "OR": "Galicia", "P": "Castilla-Leon", "PM": "Baleares",
    "PO": "Galicia", "S": "Cantabria", "SA": "Castilla-Leon", "SE": "Andalucia",
    "SG": "Castilla-Leon", "SO": "Castilla-Leon", "SS": "Pais Vasco", "T": "Cataluña",
    "TE": "Aragon", "TF": "Canarias", "TO": "Castilla-La Mancha", "V": "Valencia",
    "VA": "Castilla-Leon", "VI": "Pais Vasco", "Z": "Aragon", "ZA": "Castilla-Leon",
}

# ISCIII sex codes (Spanish) -> English labels used by the plots.
SEXO_TO_LABEL = {"H": "Male", "M": "Female"}

# Map CoVariants Nextstrain clades to broad variant families for a readable share plot.
VARIANT_FAMILY_ORDER = ["Alpha", "Delta", "Omicron", "Other"]


def variant_family(clade: str) -> str:
    for family in ("Alpha", "Delta", "Omicron"):
        if family in clade:
            return family
    return "Other"


def require_nonempty(df: pd.DataFrame, source: str) -> pd.DataFrame:
    """Fail loud if a load/filter produced no rows, so charts never render on emptiness."""
    if df is None or len(df) == 0:
        raise ValueError(
            f"No data after loading/filtering '{source}'. Re-run scripts/00_fetch_data.py "
            f"and check the upstream schema; this project uses NO synthetic fallback."
        )
    return df


def ensure_dirs() -> None:
    for path in (DATA_RAW, DATA_PROCESSED, FIG_HTML, FIG_STATIC):
        path.mkdir(parents=True, exist_ok=True)


def apply_layout(fig: go.Figure, title: str, y_title: str = "") -> go.Figure:
    fig.update_layout(
        template="plotly_white",
        title=title,
        font={"size": 18},
        legend={
            "orientation": "h",
            "yanchor": "top",
            "y": -0.22,
            "xanchor": "left",
            "x": 0,
            "title": {"text": ""},
            "font": {"size": 14},
            "bgcolor": "rgba(255,255,255,0.85)",
        },
        hoverlabel={
            "bgcolor": "#FFFFFF",
            "bordercolor": "#1F2937",
            "font": {"color": "#111111", "size": 14},
        },
        margin={"l": 60, "r": 30, "t": 80, "b": 130},
    )
    if y_title:
        fig.update_yaxes(title=y_title)
    fig.update_xaxes(title="")
    return fig


def save_outputs(fig: go.Figure, slug: str) -> None:
    ensure_dirs()
    # Keep hover labels readable in embedded iframes across all slides.
    fig.update_layout(
        hoverlabel={
            "bgcolor": "#FFFFFF",
            "bordercolor": "#1F2937",
            "font": {"color": "#111111", "size": 14},
        }
    )
    html_path = FIG_HTML / f"{slug}.html"
    pdf_path = FIG_STATIC / f"{slug}.pdf"
    png_path = FIG_STATIC / f"{slug}.png"
    fig.write_html(html_path, include_plotlyjs="directory", full_html=True,
                   config={"responsive": True})
    try:
        fig.write_image(pdf_path, format="pdf", scale=2)
        fig.write_image(png_path, format="png", scale=2, width=1600, height=900)
    except Exception:
        # Fallback when kaleido/Chrome export is unavailable in runtime.
        plt.figure(figsize=(10, 2))
        plt.axis("off")
        plt.text(0.01, 0.5, f"Static export fallback for {slug}.\nOpen figures/html/{slug}.html for full chart.", fontsize=14)
        plt.savefig(pdf_path, format="pdf", bbox_inches="tight")
        plt.savefig(png_path, format="png", bbox_inches="tight", dpi=200)
        plt.close()


def save_processed(df: pd.DataFrame, slug: str) -> Path:
    ensure_dirs()
    out = DATA_PROCESSED / f"{slug}.csv"
    df.to_csv(out, index=False)
    return out


def load_owid() -> pd.DataFrame:
    path = DATA_RAW / "owid_covid_data.csv"
    df = pd.read_csv(path, parse_dates=["date"], low_memory=False)
    # Some OWID aggregates (e.g. "European Union (27)") ship duplicate rows per date.
    df = df.drop_duplicates(subset=["location", "date"], keep="last")
    return df


def load_isciii() -> pd.DataFrame:
    """Real ISCIII data: province × sex × age, daily (Jan 2020 – Mar 2022).

    Adds a `comunidad_autonoma` column (geojson Spanish names) and normalizes the
    Spanish `sexo` codes (H=Male, M=Female) to English labels. Rows with unknown
    province ("NC") or sex ("NC") are dropped.
    """
    path = DATA_RAW / "isciii_casos_hosp_uci_def_sexo_edad_provres.csv"
    df = pd.read_csv(path)
    if "fecha" in df.columns:
        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df["comunidad_autonoma"] = df["provincia_iso"].map(PROVINCIA_TO_CCAA)
    df["sexo"] = df["sexo"].map(SEXO_TO_LABEL)
    df = df.dropna(subset=["comunidad_autonoma", "sexo"])
    return df


def load_oxcgrt() -> pd.DataFrame:
    path = DATA_RAW / "oxcgrt_nat_latest.csv"
    df = pd.read_csv(path, low_memory=False)
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"].astype(str), format="%Y%m%d", errors="coerce")
    # Real OxCGRT names the headline index StringencyIndex_Average; expose it as StringencyIndex.
    if "StringencyIndex" not in df.columns and "StringencyIndex_Average" in df.columns:
        df["StringencyIndex"] = df["StringencyIndex_Average"]
    return df


def load_mobility() -> pd.DataFrame:
    """Google mobility, country level (Spain & Poland national rows).

    Returns tidy columns: country_region, date, retail, grocery, parks, transit,
    workplaces, residential.
    """
    path = DATA_RAW / "google_mobility_spain_poland.csv"
    df = pd.read_csv(path, parse_dates=["date"])
    df = df.rename(columns={
        "country": "country_region",
        "retail and recreation": "retail",
        "grocery and pharmacy": "grocery",
        "parks": "parks",
        "transit stations": "transit",
        "workplaces": "workplaces",
        "residential": "residential",
    })
    return df


def load_variants(countries: Iterable[str] = ("Spain", "Poland")) -> pd.DataFrame:
    """Parse CoVariants EUClusters data into tidy variant-family shares.

    Output columns: location, date, variant (Alpha/Delta/Omicron/Other), perc.
    """
    path = DATA_RAW / "covariants_clusters.json"
    raw = json.loads(path.read_text(encoding="utf-8"))["countries"]
    rows = []
    for country in countries:
        block = raw.get(country)
        if not block:
            continue
        weeks = block["week"]
        totals = block["total_sequences"]
        clade_cols = [k for k in block if k not in ("week", "total_sequences")]
        for i, (week, total) in enumerate(zip(weeks, totals)):
            if not total:
                continue
            family_counts: dict[str, float] = {}
            for clade in clade_cols:
                family_counts[variant_family(clade)] = (
                    family_counts.get(variant_family(clade), 0) + block[clade][i]
                )
            for family in VARIANT_FAMILY_ORDER:
                rows.append({
                    "location": country,
                    "date": pd.Timestamp(week),
                    "variant": family,
                    "perc": family_counts.get(family, 0) / total,
                })
    return pd.DataFrame(rows)


def load_ecdc_vaccine_age() -> pd.DataFrame:
    """Real ECDC vaccine-tracker data for Spain: cumulative ≥1-dose coverage by age group.

    Output columns: date (ISO week start), age_group, coverage (% of age-group population).
    """
    path = DATA_RAW / "ecdc_vaccine_spain.csv"
    df = pd.read_csv(path)
    age_order = ["Age18_24", "Age25_49", "Age50_59", "Age60_69", "Age70_79", "Age80+"]
    df = df[df["TargetGroup"].isin(age_order)].copy()
    df["date"] = pd.to_datetime(df["YearWeekISO"] + "-1", format="%G-W%V-%u", errors="coerce")
    # Sum first doses across vaccine brands within each week & age group.
    weekly = (
        df.groupby(["TargetGroup", "date"], as_index=False)
        .agg(first_dose=("FirstDose", "sum"), denom=("Denominator", "first"))
        .sort_values("date")
    )
    weekly["cum_first"] = weekly.groupby("TargetGroup")["first_dose"].cumsum()
    weekly["coverage"] = (weekly["cum_first"] / weekly["denom"] * 100).clip(upper=100)
    label = {
        "Age18_24": "18-24", "Age25_49": "25-49", "Age50_59": "50-59",
        "Age60_69": "60-69", "Age70_79": "70-79", "Age80+": "80+",
    }
    weekly["age_group"] = weekly["TargetGroup"].map(label)
    return weekly[["date", "age_group", "coverage"]]


def country_slice(df: pd.DataFrame, countries: Iterable[str]) -> pd.DataFrame:
    return df[df["location"].isin(list(countries))].copy()


def load_eurostat_unemployment() -> pd.DataFrame:
    path = DATA_RAW / "eurostat_unemployment.csv"
    df = pd.read_csv(path)
    if "TIME_PERIOD" in df.columns:
        df["TIME_PERIOD"] = pd.to_datetime(df["TIME_PERIOD"], format="%Y-%m", errors="coerce")
    return df


def load_eurostat_tourism() -> pd.DataFrame:
    path = DATA_RAW / "eurostat_tourism.csv"
    df = pd.read_csv(path)
    if "TIME_PERIOD" in df.columns:
        df["TIME_PERIOD"] = pd.to_datetime(df["TIME_PERIOD"], format="%Y-%m", errors="coerce")
    return df


def load_eurostat_regional_gdp() -> pd.DataFrame:
    path = DATA_RAW / "eurostat_regional_gdp.csv"
    df = pd.read_csv(path)
    if "TIME_PERIOD" in df.columns:
        df["TIME_PERIOD"] = pd.to_datetime(df["TIME_PERIOD"].astype(str), format="%Y", errors="coerce")
    return df
