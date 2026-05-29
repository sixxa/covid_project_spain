from __future__ import annotations

import plotly.express as px

from _common import load_variants, save_outputs, save_processed

SLUG = "17_variant_prevalence"


_ORDER = ["Alpha", "Delta", "Omicron", "Other"]
_COLORS = {"Alpha": "#0057B8", "Delta": "#F1BF00", "Omicron": "#AA151B", "Other": "#9CA3AF"}


def main() -> None:
    df = load_variants()
    sp = df[df["location"] == "Spain"][["date", "variant", "perc"]].dropna()
    save_processed(sp, SLUG)
    fig = px.area(
        sp, x="date", y="perc", color="variant",
        category_orders={"variant": _ORDER}, color_discrete_map=_COLORS,
        title="SARS-CoV-2 Variant Prevalence in Spain (CoVariants / GISAID)",
    )
    fig.update_layout(
        template="plotly_white",
        font={"size": 18},
        legend={"orientation": "h", "yanchor": "top", "y": -0.15,
                "xanchor": "left", "x": 0, "title": {"text": ""}},
        margin={"l": 60, "r": 30, "t": 80, "b": 110},
    )
    fig.update_yaxes(title="Share", tickformat=".0%")
    save_outputs(fig, SLUG)


if __name__ == "__main__":
    main()
