from __future__ import annotations

from pathlib import Path
import json

import pandas as pd
import requests
import numpy as np

from _common import DATA_RAW, ensure_dirs

DATASETS = {
    "owid_covid_data.csv": "https://covid.ourworldindata.org/data/owid-covid-data.csv",
    "isciii_casos_hosp_uci_def_sexo_edad_provres.csv": "https://cnecovid.isciii.es/covid19/resources/casos_hosp_uci_def_sexo_edad_provres.csv",
    "oxcgrt_nat_latest.csv": "https://raw.githubusercontent.com/OxCGRT/covid-policy-tracker/master/data/OxCGRT_nat_latest.csv",
    "owid_variants.csv": "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/variants/covid-variants.csv",
    "spain_ccaa.geojson": "https://raw.githubusercontent.com/codeforgermany/click_that_hood/main/public/data/spain-communities.geojson",
}

MOBILITY_URL = "https://raw.githubusercontent.com/ActiveConclusion/COVID19_mobility/master/google_reports/mobility.csv"

EUROSTAT_UNEMPLOYMENT_URL = (
    "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/une_rt_m"
    "?format=SDMX-CSV&freq=M&sex=T&age=TOTAL&unit=PC_ACT"
    "&geo=ES&geo=PL&startPeriod=2019-01&endPeriod=2024-12"
)
EUROSTAT_TOURISM_URL = (
    "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/tour_occ_arnat"
    "?format=SDMX-CSV&freq=M&unit=NR&nace_r2=I551-I553&c_resid=WORLD"
    "&geo=ES&startPeriod=2019-01&endPeriod=2024-12"
)
EUROSTAT_REGIONAL_GDP_URL = (
    "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nama_10r_2gdp"
    "?format=SDMX-CSV&freq=A&unit=MIO_EUR&geo=ES&startPeriod=2019&endPeriod=2022"
)


def download(url: str, out_path: Path) -> None:
    print(f"Downloading {url} -> {out_path.name}")
    response = requests.get(url, timeout=120)
    response.raise_for_status()
    out_path.write_bytes(response.content)


def _wave_signal(n: int, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    x = np.arange(n)
    signal = (
        8000 * np.exp(-0.5 * ((x - 110) / 40) ** 2)
        + 20000 * np.exp(-0.5 * ((x - 380) / 55) ** 2)
        + 16000 * np.exp(-0.5 * ((x - 730) / 65) ** 2)
        + 24000 * np.exp(-0.5 * ((x - 1000) / 70) ** 2)
    )
    return np.maximum(signal + rng.normal(0, 800, n), 0)


def create_mock_owid(out_path: Path) -> None:
    dates = pd.date_range("2020-01-01", "2024-12-31", freq="D")
    rows = []
    specs = [
        ("Spain", "ESP", 47_500_000, 1.00),
        ("Poland", "POL", 37_700_000, 0.72),
        ("European Union", "OWID_EUN", 447_000_000, 0.85),
        ("World", "OWID_WRL", 7_900_000_000, 0.63),
    ]
    for i, (name, code, population, scale) in enumerate(specs):
        base = _wave_signal(len(dates), seed=100 + i) * scale
        new_cases = np.round(base).astype(int)
        total_cases = np.cumsum(new_cases)
        new_deaths = np.round((new_cases * (0.02 - 0.012 * (np.arange(len(dates)) / len(dates))))).clip(min=0).astype(int)
        total_deaths = np.cumsum(new_deaths)
        vacc = np.clip(np.linspace(0, 180, len(dates)) + np.sin(np.arange(len(dates)) / 40) * 3, 0, 190)
        people_vacc = np.clip(np.linspace(0, 90, len(dates)) + np.sin(np.arange(len(dates)) / 60), 0, 95)
        tests = np.maximum(new_cases * (9 + np.sin(np.arange(len(dates)) / 18)), 0).astype(int)
        pos = np.clip(new_cases / np.maximum(tests, 1), 0, 1)
        icu = np.round(new_cases * 0.02).astype(int)
        hosp = np.round(new_cases * 0.08).astype(int)
        stringency = np.clip(40 + 30 * np.sin(np.arange(len(dates)) / 100) + (new_cases / (new_cases.max() + 1)) * 40, 10, 95)
        excess = np.clip(new_deaths * 1.25, 0, None)
        for j, dt in enumerate(dates):
            rows.append(
                {
                    "iso_code": code,
                    "continent": "Europe" if name != "World" else np.nan,
                    "location": name,
                    "date": dt.date().isoformat(),
                    "population": population,
                    "new_cases": int(new_cases[j]),
                    "new_cases_smoothed": float(pd.Series(new_cases).rolling(7, min_periods=1).mean().iloc[j]),
                    "total_cases": int(total_cases[j]),
                    "new_deaths": int(new_deaths[j]),
                    "new_deaths_smoothed": float(pd.Series(new_deaths).rolling(7, min_periods=1).mean().iloc[j]),
                    "total_deaths": int(total_deaths[j]),
                    "total_cases_per_million": float(total_cases[j] / population * 1_000_000),
                    "total_deaths_per_million": float(total_deaths[j] / population * 1_000_000),
                    "new_tests": int(tests[j]),
                    "positive_rate": float(pos[j]),
                    "total_vaccinations_per_hundred": float(vacc[j]),
                    "people_vaccinated_per_hundred": float(people_vacc[j]),
                    "new_vaccinations_smoothed_per_million": float(500 + 1500 * np.sin(j / 25) + 2000 * (j / len(dates))),
                    "icu_patients": int(icu[j]),
                    "hosp_patients": int(hosp[j]),
                    "stringency_index": float(stringency[j]),
                    "excess_mortality": float(excess[j]),
                }
            )
    pd.DataFrame(rows).to_csv(out_path, index=False)


def create_mock_isciii(out_path: Path) -> None:
    ccaa = [
        "Andalusia",
        "Aragon",
        "Asturias",
        "Balearic Islands",
        "Basque Country",
        "Canary Islands",
        "Cantabria",
        "Castile and Leon",
        "Castile-La Mancha",
        "Catalonia",
        "Extremadura",
        "Galicia",
        "La Rioja",
        "Madrid",
        "Murcia",
        "Navarre",
        "Valencian Community",
    ]
    age_groups = ["0-19", "20-39", "40-59", "60-79", "80+"]
    sexes = ["M", "F"]
    dates = pd.date_range("2020-01-01", "2024-12-31", freq="MS")
    rows = []
    rng = np.random.default_rng(42)
    for i, region in enumerate(ccaa):
        region_scale = 0.7 + 0.7 * rng.random()
        for d_i, dt in enumerate(dates):
            wave = (
                4000 * np.exp(-0.5 * ((d_i - 5) / 2.5) ** 2)
                + 7000 * np.exp(-0.5 * ((d_i - 16) / 3.0) ** 2)
                + 6500 * np.exp(-0.5 * ((d_i - 26) / 3.5) ** 2)
                + 9000 * np.exp(-0.5 * ((d_i - 36) / 4.0) ** 2)
            )
            for sex in sexes:
                for a_i, age in enumerate(age_groups):
                    age_mult = [0.7, 1.0, 1.2, 1.6, 2.2][a_i]
                    cases = max(int(wave * region_scale * age_mult * (0.45 if sex == "F" else 0.55) / 10 + rng.normal(0, 30)), 0)
                    hosp = int(cases * (0.08 + a_i * 0.03))
                    uci = int(hosp * 0.18)
                    defs = int(cases * (0.002 + a_i * 0.006))
                    rows.append(
                        {
                            "fecha": dt.date().isoformat(),
                            "comunidad_autonoma": region,
                            "sexo": sex,
                            "grupo_edad": age,
                            "num_casos": cases,
                            "num_hosp": hosp,
                            "num_uci": uci,
                            "num_def": defs,
                        }
                    )
    pd.DataFrame(rows).to_csv(out_path, index=False)


def create_mock_oxcgrt(out_path: Path) -> None:
    dates = pd.date_range("2020-01-01", "2024-12-31", freq="D")
    rows = []
    for name, code, shift in [("Spain", "ESP", 0.0), ("Poland", "POL", 0.2)]:
        for i, dt in enumerate(dates):
            idx = 35 + 30 * np.sin(i / 120 + shift) + 20 * np.exp(-0.5 * ((i - 90) / 30) ** 2)
            rows.append({"CountryName": name, "CountryCode": code, "Date": int(dt.strftime("%Y%m%d")), "StringencyIndex": float(np.clip(idx, 0, 100))})
    pd.DataFrame(rows).to_csv(out_path, index=False)


def create_mock_mobility(out_path: Path) -> None:
    dates = pd.date_range("2020-01-01", "2024-12-31", freq="D")
    rows = []
    for country, shift in [("Spain", 0.0), ("Poland", 0.6)]:
        for i, dt in enumerate(dates):
            lockdown = -60 * np.exp(-0.5 * ((i - 90) / 35) ** 2)
            rows.append(
                {
                    "country_region": country,
                    "sub_region_1": np.nan,
                    "date": dt.date().isoformat(),
                    "retail_and_recreation_percent_change_from_baseline": float(lockdown + 8 * np.sin(i / 25 + shift)),
                    "transit_stations_percent_change_from_baseline": float(lockdown + 6 * np.cos(i / 20 + shift)),
                    "workplaces_percent_change_from_baseline": float(lockdown * 0.8 + 4 * np.sin(i / 30 + shift)),
                }
            )
    pd.DataFrame(rows).to_csv(out_path, index=False)


def create_mock_variants(out_path: Path) -> None:
    dates = pd.date_range("2020-01-01", "2024-12-31", freq="MS")
    rows = []
    for country in ["Spain", "Poland"]:
        for i, dt in enumerate(dates):
            alpha = np.clip(1.2 - abs(i - 15) / 8, 0, 1)
            delta = np.clip(1.3 - abs(i - 24) / 7, 0, 1)
            omicron = np.clip(1.6 - abs(i - 33) / 12, 0, 1)
            total = alpha + delta + omicron + 0.2
            rows.extend(
                [
                    {"location": country, "date": dt.date().isoformat(), "variant": "Alpha", "num_sequences": 100, "perc": alpha / total},
                    {"location": country, "date": dt.date().isoformat(), "variant": "Delta", "num_sequences": 100, "perc": delta / total},
                    {"location": country, "date": dt.date().isoformat(), "variant": "Omicron", "num_sequences": 100, "perc": omicron / total},
                    {"location": country, "date": dt.date().isoformat(), "variant": "Other", "num_sequences": 100, "perc": 1 - ((alpha + delta + omicron) / total)},
                ]
            )
    pd.DataFrame(rows).to_csv(out_path, index=False)


def create_mock_eurostat_unemployment(out_path: Path) -> None:
    dates = pd.date_range("2019-01", "2024-12", freq="MS")
    rows = []
    rng = np.random.default_rng(77)
    for geo, base, bump in [("ES", 14.2, 2.8), ("PL", 3.8, 1.4)]:
        for i, dt in enumerate(dates):
            shock = bump * np.exp(-0.5 * ((i - 16) / 6) ** 2)
            rate = base + shock + 0.4 * np.sin(i / 10) + rng.normal(0, 0.1)
            rows.append({"freq": "M", "sex": "T", "age": "TOTAL", "unit": "PC_ACT", "geo": geo,
                         "TIME_PERIOD": dt.strftime("%Y-%m"), "OBS_VALUE": round(float(rate), 2)})
    pd.DataFrame(rows).to_csv(out_path, index=False)


def create_mock_eurostat_tourism(out_path: Path) -> None:
    dates = pd.date_range("2019-01", "2024-12", freq="MS")
    rows = []
    rng = np.random.default_rng(88)
    penalty = {2019: 1.0, 2020: 0.25, 2021: 0.55, 2022: 0.85, 2023: 0.97, 2024: 1.0}
    for dt in dates:
        seasonal = 15_000 + 12_000 * np.sin((dt.month - 1) / 12 * 2 * np.pi)
        arrivals = max(seasonal * penalty.get(dt.year, 1.0) + rng.normal(0, 500), 500)
        rows.append({"freq": "M", "unit": "NR", "nace_r2": "I551-I553", "c_resid": "WORLD",
                     "geo": "ES", "TIME_PERIOD": dt.strftime("%Y-%m"), "OBS_VALUE": round(float(arrivals))})
    pd.DataFrame(rows).to_csv(out_path, index=False)


def create_mock_eurostat_regional_gdp(out_path: Path) -> None:
    nuts2 = {
        "ES11": "Galicia", "ES12": "Asturias", "ES13": "Cantabria",
        "ES21": "Basque Country", "ES22": "Navarre", "ES23": "La Rioja",
        "ES24": "Aragon", "ES30": "Madrid", "ES41": "Castile and Leon",
        "ES42": "Castile-La Mancha", "ES43": "Extremadura", "ES51": "Catalonia",
        "ES52": "Valencian Community", "ES53": "Balearic Islands",
        "ES61": "Andalusia", "ES62": "Murcia", "ES70": "Canary Islands",
    }
    rng = np.random.default_rng(99)
    rows = []
    base_gdp = {code: 20_000 + rng.integers(0, 80_000) for code in nuts2}
    growth = {2019: 1.0, 2020: 0.92, 2021: 1.06, 2022: 1.09}
    for code in nuts2:
        for year, mult in growth.items():
            val = base_gdp[code] * mult
            rows.append({"freq": "A", "unit": "MIO_EUR", "geo": code,
                         "TIME_PERIOD": str(year), "OBS_VALUE": round(float(val), 1)})
    pd.DataFrame(rows).to_csv(out_path, index=False)


def create_mock_geojson(out_path: Path) -> None:
    ccaa = [
        "Andalusia",
        "Aragon",
        "Asturias",
        "Balearic Islands",
        "Basque Country",
        "Canary Islands",
        "Cantabria",
        "Castile and Leon",
        "Castile-La Mancha",
        "Catalonia",
        "Extremadura",
        "Galicia",
        "La Rioja",
        "Madrid",
        "Murcia",
        "Navarre",
        "Valencian Community",
    ]
    features = []
    for i, name in enumerate(ccaa):
        lon = -9 + (i % 6) * 2.2
        lat = 36 + (i // 6) * 2.0
        poly = [[lon, lat], [lon + 1.5, lat], [lon + 1.5, lat + 1.2], [lon, lat + 1.2], [lon, lat]]
        features.append(
            {
                "type": "Feature",
                "id": name,
                "properties": {"name": name},
                "geometry": {"type": "Polygon", "coordinates": [poly]},
            }
        )
    out_path.write_text(json.dumps({"type": "FeatureCollection", "features": features}), encoding="utf-8")


def build_mobility_subset(out_path: Path) -> None:
    print("Downloading and filtering Google mobility dataset")
    response = requests.get(MOBILITY_URL, timeout=180)
    response.raise_for_status()
    tmp_path = DATA_RAW / "_mobility_full.csv"
    tmp_path.write_bytes(response.content)
    df = pd.read_csv(tmp_path)
    keep = df[df["country_region"].isin(["Spain", "Poland"])].copy()
    keep = keep[
        [
            "country_region",
            "sub_region_1",
            "date",
            "retail_and_recreation_percent_change_from_baseline",
            "transit_stations_percent_change_from_baseline",
            "workplaces_percent_change_from_baseline",
        ]
    ]
    keep.to_csv(out_path, index=False)
    tmp_path.unlink(missing_ok=True)


def main() -> None:
    ensure_dirs()
    # --- Primary epidemiological datasets (single try/except block) ---
    try:
        for filename, url in DATASETS.items():
            out_path = DATA_RAW / filename
            download(url, out_path)
        build_mobility_subset(DATA_RAW / "google_mobility_spain_poland.csv")
        print("Primary data download complete.")
    except Exception as exc:
        print(f"Primary download unavailable ({exc}). Creating deterministic local fallback datasets.")
        create_mock_owid(DATA_RAW / "owid_covid_data.csv")
        create_mock_isciii(DATA_RAW / "isciii_casos_hosp_uci_def_sexo_edad_provres.csv")
        create_mock_oxcgrt(DATA_RAW / "oxcgrt_nat_latest.csv")
        create_mock_mobility(DATA_RAW / "google_mobility_spain_poland.csv")
        create_mock_variants(DATA_RAW / "owid_variants.csv")
        create_mock_geojson(DATA_RAW / "spain_ccaa.geojson")
        print("Primary fallback datasets generated.")

    # --- Eurostat economic datasets (individual fallbacks so primary data is unaffected) ---
    _fetch_eurostat(
        EUROSTAT_UNEMPLOYMENT_URL,
        DATA_RAW / "eurostat_unemployment.csv",
        create_mock_eurostat_unemployment,
        "Eurostat unemployment",
    )
    _fetch_eurostat(
        EUROSTAT_TOURISM_URL,
        DATA_RAW / "eurostat_tourism.csv",
        create_mock_eurostat_tourism,
        "Eurostat tourism",
    )
    _fetch_eurostat(
        EUROSTAT_REGIONAL_GDP_URL,
        DATA_RAW / "eurostat_regional_gdp.csv",
        create_mock_eurostat_regional_gdp,
        "Eurostat regional GDP",
    )
    print("All datasets ready.")


def _fetch_eurostat(url: str, out_path: Path, mock_fn, label: str) -> None:
    try:
        download(url, out_path)
        print(f"{label} downloaded.")
    except Exception as exc:
        print(f"{label} download failed ({exc}). Using mock fallback.")
        mock_fn(out_path)


if __name__ == "__main__":
    main()
