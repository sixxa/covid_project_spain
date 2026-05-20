from __future__ import annotations

import plotly.express as px

from _common import PALETTE, load_owid, save_outputs, save_processed

SLUG = "02_cumulative_cases_per_100k"


def main() -> None:
    df = load_owid()
    view = df[df["location"].isin(["Spain", "Poland", "European Union"])][["date", "location", "total_cases_per_million"]].dropna()
    view["cases_per_100k"] = view["total_cases_per_million"] / 10
    out = view[["date", "location", "cases_per_100k"]]
    save_processed(out, SLUG)
    fig = px.line(
        out,
        x="date",
        y="cases_per_100k",
        color="location",
        color_discrete_map={
            "Spain": PALETTE["spain"],
            "Poland": PALETTE["poland"],
            "European Union": PALETTE["neutral"],
        },
    )
    fig.update_layout(template="plotly_white", title="Cumulative Cases per 100k: Spain vs Poland vs EU", font={"size": 18})
    fig.update_yaxes(title="Cases per 100k")
    save_outputs(fig, SLUG)


if __name__ == "__main__":
    main()
