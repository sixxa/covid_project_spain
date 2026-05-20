# COVID-19 in Spain — DAV 2026 project

Analysis of the COVID-19 pandemic in Spain (2020–2024), with Poland used as a comparison throughout. The project covers epidemiology, regional breakdowns, vaccination, policy response, and economic impact.

Two versions of the presentation:
- `slides/index.html` — interactive HTML with Plotly charts (open `covid19_Spain.html` to get there)
- `covid19_Spain_poster.pdf` — A0 poster for printing

## How to run

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/00_fetch_data.py   # downloads raw data
.venv/bin/python scripts/run_all.py          # regenerates all figures
```

To rebuild the poster from LaTeX: `cd poster && make` (needs `pdflatex` + `tikzposter`).

## Data sources

| Dataset | Source |
|---|---|
| Cases, deaths, vaccinations | [Our World in Data](https://covid.ourworldindata.org/data/owid-covid-data.csv) |
| Spain regional data (CCAA, age, sex) | [ISCIII](https://cnecovid.isciii.es/covid19/resources/casos_hosp_uci_def_sexo_edad_provres.csv) |
| Government policy stringency | [OxCGRT](https://github.com/OxCGRT/covid-policy-tracker) |
| Google mobility | [ActiveConclusion mirror](https://github.com/ActiveConclusion/COVID19_mobility) |
| Variant prevalence | [OWID variants](https://github.com/owid/covid-19-data/tree/master/public/data/variants) |
| Spain regions GeoJSON | [click_that_hood](https://github.com/codeforgermany/click_that_hood) |

## Statistical models used

- **SARIMA (plots 21–22):** trained on 2020–2022, then retrained on 2020–2024 to see how the forecast changes when the epidemic decline is included. This split was suggested in the assignment brief.
- **Gompertz curve (plot 23):** fit to cumulative cases during the first wave — works well for epidemic growth that slows as the susceptible population shrinks.
- **Lagged regression (plot 24):** OxCGRT stringency index lagged by ~14 days regressed against case growth rate, to test whether stricter measures actually preceded drops.
- **Vaccine vs. CFR (plot 25):** scatter/trend of vaccination coverage against case fatality rate by period, showing the association between rollout and mortality drop.

## Plots

| # | Script | What it shows |
|---|---|---|
| 01 | `01_cases_timeline.py` | Daily cases — Spain vs Poland |
| 02 | `02_cumulative_cases_per_100k.py` | Cumulative cases per 100k |
| 03 | `03_daily_deaths.py` | Daily deaths with policy event markers |
| 04 | `04_cumulative_deaths_per_100k.py` | Cumulative deaths per 100k |
| 05 | `05_excess_mortality_vs_reported.py` | Excess mortality vs officially reported deaths |
| 06 | `06_positivity_rate.py` | Test positivity rate (WHO 5% threshold) |
| 07 | `07_vaccination_doses_animated.py` | Vaccination rollout — animated by month |
| 08 | `08_vaccination_by_age_spain.py` | Coverage by age group in Spain |
| 09 | `09_hospital_icu_spain.py` | Hospital and ICU occupancy |
| 10 | `10_stringency_vs_cases.py` | Policy stringency overlaid on case curve |
| 11 | `11_mobility_lockdown.py` | Google mobility change during lockdowns |
| 12 | `12_choropleth_waves.py` | Regional burden per wave (animated map) |
| 13 | `13_ccaa_month_heatmap.py` | Cases by region × month heatmap |
| 14 | `14_top_ccaa_deaths.py` | Death burden by autonomous community |
| 15 | `15_age_sex_pyramid.py` | Age and sex breakdown of mortality |
| 16 | `16_wave_decomposition.py` | Wave decomposition by period |
| 17 | `17_variant_prevalence.py` | Variant share over time (Alpha → Omicron) |
| 18 | `18_tourism_collapse.py` | International arrivals collapse in 2020 |
| 19 | `19_unemployment_es_pl.py` | Unemployment rate — Spain vs Poland |
| 20 | `20_regional_gdp_impact.py` | Regional GDP drop in 2020 |
| 21 | `21_sarima_2020_2022.py` | SARIMA forecast trained on 2020–2022 |
| 22 | `22_sarima_2020_2024.py` | SARIMA forecast trained on 2020–2024 |
| 23 | `23_gompertz_first_wave.py` | Gompertz fit on first-wave cumulative cases |
| 24 | `24_lag_regression_stringency.py` | Lagged regression: stringency → case growth |
| 25 | `25_vaccine_vs_cfr.py` | Vaccination coverage vs case fatality rate |
| 26 | `26_reproduction_number.py` | Effective reproduction number Rt over time |
| 27 | `27_cfr_by_wave.py` | Case fatality rate broken down by wave |

Each plot has its own script in `scripts/`, processed data in `data/processed/`, interactive HTML in `figures/html/`, and static PDF/PNG in `figures/static/`.
