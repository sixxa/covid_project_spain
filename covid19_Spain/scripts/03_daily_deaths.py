from __future__ import annotations

import pandas as pd
import plotly.express as px

from _common import PALETTE, load_owid, save_outputs, save_processed

SLUG = "03_daily_deaths"


def main() -> None:
    df = load_owid()
    view = df[df["location"].isin(["Spain", "Poland"])][["date", "location", "new_deaths_smoothed"]].dropna()
    save_processed(view, SLUG)
    fig = px.line(
        view,
        x="date",
        y="new_deaths_smoothed",
        color="location",
        color_discrete_map={"Spain": PALETTE["spain"], "Poland": PALETTE["poland"]},
    )
    for dt in [pd.Timestamp("2020-03-15"), pd.Timestamp("2021-01-10"), pd.Timestamp("2022-01-15")]:
        fig.add_vline(x=dt, line_dash="dash", line_color="gray")
    fig.update_layout(template="plotly_white", title="Daily COVID-19 Deaths (7-day smoothed)", font={"size": 18})
    fig.update_yaxes(title="Deaths")
    save_outputs(fig, SLUG)


if __name__ == "__main__":
    main()
