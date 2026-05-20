from __future__ import annotations

import plotly.express as px

from _common import PALETTE, load_owid, save_outputs, save_processed

SLUG = "07_vaccination_doses_animated"


def main() -> None:
    df = load_owid()
    view = df[df["location"].isin(["Spain", "Poland"])][["date", "location", "total_vaccinations_per_hundred"]].dropna()
    view["month"] = view["date"].dt.to_period("M").astype(str)
    monthly = view.groupby(["month", "location"], as_index=False)["total_vaccinations_per_hundred"].max()
    save_processed(monthly, SLUG)
    fig = px.bar(
        monthly,
        x="location",
        y="total_vaccinations_per_hundred",
        color="location",
        animation_frame="month",
        range_y=[0, max(200, monthly["total_vaccinations_per_hundred"].max() * 1.1)],
        color_discrete_map={"Spain": PALETTE["spain"], "Poland": PALETTE["poland"]},
        title="Vaccination Doses per 100 People (Animated by Month)",
    )
    fig.update_layout(
        template="plotly_white",
        font={"size": 18},
        showlegend=False,
        margin={"b": 120},
        sliders=[{
            # Tick labels would all overlap — hide them with a transparent color.
            # The currentvalue line above the slider always shows the exact month.
            "font": {"color": "rgba(0,0,0,0)", "size": 1},
            "ticklen": 4,
            "currentvalue": {
                "visible": True,
                "prefix": "Month: ",
                "xanchor": "left",
                "font": {"size": 18, "color": "#333"},
            },
        }],
    )
    fig.update_yaxes(title="Doses per 100")
    save_outputs(fig, SLUG)


if __name__ == "__main__":
    main()
