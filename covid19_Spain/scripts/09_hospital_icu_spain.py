from __future__ import annotations

import plotly.graph_objects as go

from _common import apply_layout, load_owid, save_outputs, save_processed

SLUG = "09_hospital_icu_spain"


def main() -> None:
    df = load_owid()
    es = df[df["location"] == "Spain"][["date", "hosp_patients", "icu_patients"]].dropna()
    save_processed(es, SLUG)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=es["date"], y=es["hosp_patients"], mode="lines", name="Hospitalized", line={"color": "#AA151B"}))
    fig.add_trace(go.Scatter(x=es["date"], y=es["icu_patients"], mode="lines", name="ICU", line={"color": "#F1BF00"}))
    fig = apply_layout(fig, "Spain Hospital and ICU Occupancy", "Patients")
    save_outputs(fig, SLUG)


if __name__ == "__main__":
    main()
