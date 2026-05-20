from __future__ import annotations

import plotly.express as px

from _common import PALETTE, load_owid, save_outputs, save_processed

SLUG = "06_positivity_rate"


def main() -> None:
    df = load_owid()
    view = df[df["location"].isin(["Spain", "Poland"])][["date", "location", "positive_rate"]].dropna()
    save_processed(view, SLUG)
    fig = px.line(
        view,
        x="date",
        y="positive_rate",
        color="location",
        color_discrete_map={"Spain": PALETTE["spain"], "Poland": PALETTE["poland"]},
    )
    fig.update_layout(template="plotly_white", title="Test Positivity Rate: Spain vs Poland", font={"size": 18})
    fig.update_yaxes(title="Positivity rate", tickformat=".0%")
    save_outputs(fig, SLUG)


if __name__ == "__main__":
    main()
