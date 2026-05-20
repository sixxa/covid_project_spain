from __future__ import annotations

import plotly.express as px

from _common import PALETTE, load_owid, save_outputs, save_processed

SLUG = "04_cumulative_deaths_per_100k"


def main() -> None:
    df = load_owid()
    view = df[df["location"].isin(["Spain", "Poland", "World"])][["date", "location", "total_deaths_per_million"]].dropna()
    view["deaths_per_100k"] = view["total_deaths_per_million"] / 10
    out = view[["date", "location", "deaths_per_100k"]]
    save_processed(out, SLUG)
    fig = px.line(
        out,
        x="date",
        y="deaths_per_100k",
        color="location",
        color_discrete_map={
            "Spain": PALETTE["spain"],
            "Poland": PALETTE["poland"],
            "World": PALETTE["global"],
        },
    )
    fig.update_layout(template="plotly_white", title="Cumulative Deaths per 100k: Spain vs Poland vs World", font={"size": 18})
    fig.update_yaxes(title="Deaths per 100k")
    save_outputs(fig, SLUG)


if __name__ == "__main__":
    main()
