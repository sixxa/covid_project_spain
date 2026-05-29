from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from _common import load_isciii, save_outputs, save_processed

SLUG = "15_age_sex_pyramid"


AGE_ORDER = ["0-9", "10-19", "20-29", "30-39", "40-49", "50-59", "60-69", "70-79", "80+"]


def main() -> None:
    df = load_isciii()
    df = df[df["grupo_edad"].isin(AGE_ORDER)]
    agg = df.groupby(["grupo_edad", "sexo"], as_index=False)["num_def"].sum()
    agg["grupo_edad"] = pd.Categorical(agg["grupo_edad"], categories=AGE_ORDER, ordered=True)
    agg = agg.sort_values("grupo_edad")
    males = agg[agg["sexo"] == "Male"].copy()
    females = agg[agg["sexo"] == "Female"].copy()
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
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
            "font": {"size": 14},
        },
        margin={"l": 60, "r": 30, "t": 90, "b": 70},
    )
    save_outputs(fig, SLUG)


if __name__ == "__main__":
    main()
