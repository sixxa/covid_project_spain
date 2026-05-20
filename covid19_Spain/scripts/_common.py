from __future__ import annotations

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


def ensure_dirs() -> None:
    for path in (DATA_RAW, DATA_PROCESSED, FIG_HTML, FIG_STATIC):
        path.mkdir(parents=True, exist_ok=True)


def apply_layout(fig: go.Figure, title: str, y_title: str = "") -> go.Figure:
    fig.update_layout(
        template="plotly_white",
        title=title,
        font={"size": 18},
        legend={"orientation": "h", "y": -0.2},
        hoverlabel={
            "bgcolor": "#FFFFFF",
            "bordercolor": "#1F2937",
            "font": {"color": "#111111", "size": 14},
        },
        margin={"l": 60, "r": 30, "t": 80, "b": 80},
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
    fig.write_html(html_path, include_plotlyjs="directory", full_html=True)
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
    df = pd.read_csv(path, parse_dates=["date"])
    return df


def load_isciii() -> pd.DataFrame:
    path = DATA_RAW / "isciii_casos_hosp_uci_def_sexo_edad_provres.csv"
    df = pd.read_csv(path)
    if "fecha" in df.columns:
        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    return df


def load_oxcgrt() -> pd.DataFrame:
    path = DATA_RAW / "oxcgrt_nat_latest.csv"
    df = pd.read_csv(path)
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"].astype(str), format="%Y%m%d", errors="coerce")
    return df


def load_mobility() -> pd.DataFrame:
    path = DATA_RAW / "google_mobility_spain_poland.csv"
    df = pd.read_csv(path, parse_dates=["date"])
    return df


def load_variants() -> pd.DataFrame:
    path = DATA_RAW / "owid_variants.csv"
    df = pd.read_csv(path, parse_dates=["date"])
    return df


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
