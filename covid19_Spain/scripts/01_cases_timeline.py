from __future__ import annotations

import plotly.express as px

from _common import PALETTE, apply_layout, country_slice, load_owid, save_outputs, save_processed

SLUG = "01_cases_timeline"


def main() -> None:
    df = load_owid()
    view = country_slice(df, ["Spain", "Poland"])[["date", "location", "new_cases_smoothed"]].dropna()
    save_processed(view, SLUG)

    fig = px.line(
        view,
        x="date",
        y="new_cases_smoothed",
        color="location",
        color_discrete_map={"Spain": PALETTE["spain"], "Poland": PALETTE["poland"]},
    )
    fig = apply_layout(fig, "Daily COVID-19 Cases (7-day smoothed): Spain vs Poland", "New cases")
    save_outputs(fig, SLUG)


if __name__ == "__main__":
    main()
