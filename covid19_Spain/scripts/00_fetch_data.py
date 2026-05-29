"""Download all real source datasets used by the project.

This script ONLY fetches real, citable data from upstream sources. There is no
synthetic/mock fallback: if a source is unreachable the script prints a clear
error and exits non-zero, so the pipeline can never silently present invented
numbers as if they were real.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import requests

from _common import DATA_RAW, ensure_dirs

# --- Direct file downloads (saved verbatim to data/raw) ---------------------
DATASETS = {
    # OWID's monolithic CSV moved; the GitHub mirror carries the full real schema.
    "owid_covid_data.csv":
        "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv",
    # Spain's national epidemiology institute (ISCIII): province × sex × age, daily.
    "isciii_casos_hosp_uci_def_sexo_edad_provres.csv":
        "https://cnecovid.isciii.es/covid19/resources/casos_hosp_uci_def_sexo_edad_provres.csv",
    # OxCGRT government-response / stringency tracker (all countries).
    "oxcgrt_nat_latest.csv":
        "https://raw.githubusercontent.com/OxCGRT/covid-policy-tracker/master/data/OxCGRT_nat_latest.csv",
    # Spanish autonomous-community boundaries (real geometry).
    "spain_ccaa.geojson":
        "https://raw.githubusercontent.com/codeforgermany/click_that_hood/main/public/data/spain-communities.geojson",
    # CoVariants per-country variant/clade frequencies (replaces the removed OWID variants file).
    "covariants_clusters.json":
        "https://raw.githubusercontent.com/hodcroftlab/covariants/master/cluster_tables/EUClusters_data.json",
}

# Google mobility, country-level aggregation (national rows have region == "Total").
MOBILITY_URL = (
    "https://raw.githubusercontent.com/ActiveConclusion/COVID19_mobility/"
    "master/google_reports/mobility_report_countries.csv"
)

# ECDC COVID-19 vaccine tracker: real vaccination by age group (weekly).
ECDC_VACCINE_URL = "https://opendata.ecdc.europa.eu/covid19/vaccine_tracker/csv/data.csv"

# Eurostat SDMX-CSV endpoints (full cubes; the plot scripts filter the slice they need).
EUROSTAT_UNEMPLOYMENT_URL = (
    "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/une_rt_m"
    "?format=SDMX-CSV&startPeriod=2019-01&endPeriod=2024-12"
)
EUROSTAT_TOURISM_URL = (
    "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/tour_occ_arnat"
    "?format=SDMX-CSV&geo=ES&startPeriod=2019&endPeriod=2024"
)
EUROSTAT_REGIONAL_GDP_URL = (
    "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nama_10r_2gdp"
    "?format=SDMX-CSV&startPeriod=2019&endPeriod=2022"
)


def download(url: str, out_path: Path) -> None:
    print(f"Downloading {url}\n  -> {out_path.name}")
    response = requests.get(url, timeout=300)
    response.raise_for_status()
    if not response.content:
        raise RuntimeError(f"Empty response from {url}")
    out_path.write_bytes(response.content)


def build_mobility_subset(out_path: Path) -> None:
    """Download Google mobility (country level) and keep only Spain & Poland national rows."""
    print(f"Downloading {MOBILITY_URL}\n  -> {out_path.name} (filtered to Spain & Poland)")
    response = requests.get(MOBILITY_URL, timeout=300)
    response.raise_for_status()
    tmp_path = DATA_RAW / "_mobility_full.csv"
    tmp_path.write_bytes(response.content)
    df = pd.read_csv(tmp_path)
    keep = df[(df["country"].isin(["Spain", "Poland"])) & (df["region"] == "Total")].copy()
    if keep.empty:
        tmp_path.unlink(missing_ok=True)
        raise RuntimeError("Mobility download contained no Spain/Poland national rows")
    keep.to_csv(out_path, index=False)
    tmp_path.unlink(missing_ok=True)


def build_ecdc_vaccine_subset(out_path: Path) -> None:
    """Download ECDC vaccine tracker and keep only Spain rows (keeps the raw file small)."""
    print(f"Downloading {ECDC_VACCINE_URL}\n  -> {out_path.name} (filtered to Spain)")
    response = requests.get(ECDC_VACCINE_URL, timeout=300)
    response.raise_for_status()
    tmp_path = DATA_RAW / "_ecdc_vaccine_full.csv"
    tmp_path.write_bytes(response.content)
    df = pd.read_csv(tmp_path)
    region_col = "ReportingCountry" if "ReportingCountry" in df.columns else "Region"
    keep = df[df[region_col] == "ES"].copy()
    if keep.empty:
        tmp_path.unlink(missing_ok=True)
        raise RuntimeError("ECDC vaccine download contained no Spain (ES) rows")
    keep.to_csv(out_path, index=False)
    tmp_path.unlink(missing_ok=True)


def main() -> None:
    ensure_dirs()
    failures: list[str] = []

    for filename, url in DATASETS.items():
        try:
            download(url, DATA_RAW / filename)
        except Exception as exc:  # noqa: BLE001 - report and continue, fail loud at end
            failures.append(f"{filename}: {exc}")

    for label, builder, out_name in [
        ("Google mobility", build_mobility_subset, "google_mobility_spain_poland.csv"),
        ("ECDC vaccine by age", build_ecdc_vaccine_subset, "ecdc_vaccine_spain.csv"),
    ]:
        try:
            builder(DATA_RAW / out_name)
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{label}: {exc}")

    for label, url, out_name in [
        ("Eurostat unemployment", EUROSTAT_UNEMPLOYMENT_URL, "eurostat_unemployment.csv"),
        ("Eurostat tourism", EUROSTAT_TOURISM_URL, "eurostat_tourism.csv"),
        ("Eurostat regional GDP", EUROSTAT_REGIONAL_GDP_URL, "eurostat_regional_gdp.csv"),
    ]:
        try:
            download(url, DATA_RAW / out_name)
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{label}: {exc}")

    if failures:
        print("\nERROR: one or more real datasets could not be downloaded:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        print(
            "\nNo synthetic fallback is used. Fix the source(s) above and re-run. "
            "Do NOT build charts on partial data.",
            file=sys.stderr,
        )
        sys.exit(1)

    print("\nAll real datasets downloaded successfully.")


if __name__ == "__main__":
    main()
