from __future__ import annotations

import plotly.graph_objects as go

from _common import load_isciii, save_outputs, save_processed

SLUG = "15_age_sex_pyramid"


def main() -> None:
    df = load_isciii()
    agg = df.groupby(["grupo_edad", "sexo"], as_index=False)["num_def"].sum()
    males = agg[agg["sexo"] == "M"].copy()
    females = agg[agg["sexo"] == "F"].copy()
    males["num_def"] = -males["num_def"]
    out = agg.copy()
    save_processed(out, SLUG)

    fig = go.Figure()
    fig.add_trace(go.Bar(y=males["grupo_edad"], x=males["num_def"], name="Male", orientation="h", marker_color="#4D4D4D"))
    fig.add_trace(go.Bar(y=females["grupo_edad"], x=females["num_def"], name="Female", orientation="h", marker_color="#AA151B"))
    fig.update_layout(
        template="plotly_white",
        barmode="relative",
        title="Spain COVID-19 Deaths by Age and Sex",
        font={"size": 18},
        xaxis={"title": "Deaths (Male left / Female right)"},
        yaxis={"title": "Age group"},
    )
    save_outputs(fig, SLUG)


if __name__ == "__main__":
    main()
