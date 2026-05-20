from __future__ import annotations

import plotly.express as px

from _common import load_variants, save_outputs, save_processed

SLUG = "17_variant_prevalence"


def main() -> None:
    df = load_variants()
    sp = df[df["location"] == "Spain"][["date", "variant", "perc"]].dropna()
    save_processed(sp, SLUG)
    fig = px.area(sp, x="date", y="perc", color="variant", title="Variant Prevalence in Spain")
    fig.update_layout(template="plotly_white", font={"size": 18})
    fig.update_yaxes(title="Share", tickformat=".0%")
    save_outputs(fig, SLUG)


if __name__ == "__main__":
    main()
