from __future__ import annotations

import plotly.express as px

from _common import load_ecdc_vaccine_age, require_nonempty, save_outputs, save_processed

SLUG = "08_vaccination_by_age_spain"

_AGE_ORDER = ["18-24", "25-49", "50-59", "60-69", "70-79", "80+"]


def main() -> None:
    out = require_nonempty(load_ecdc_vaccine_age(), "ECDC vaccine by age")
    out["date"] = out["date"].astype(str)
    save_processed(out, SLUG)
    fig = px.line(
        out, x="date", y="coverage", color="age_group",
        category_orders={"age_group": _AGE_ORDER},
        title="Spain: Cumulative Vaccination Coverage (≥1 dose) by Age Group",
    )
    fig.update_layout(
        template="plotly_white", font={"size": 18},
        legend={"orientation": "h", "yanchor": "top", "y": -0.18,
                "xanchor": "left", "x": 0, "title": {"text": "Age group"}},
        margin={"l": 60, "r": 30, "t": 80, "b": 130},
        annotations=[{"text": "Source: ECDC COVID-19 Vaccine Tracker", "xref": "paper",
                       "yref": "paper", "x": 0, "y": -0.34, "showarrow": False,
                       "font": {"size": 11}, "xanchor": "left"}],
    )
    fig.update_yaxes(title="Coverage (% of age group)", range=[0, 105])
    save_outputs(fig, SLUG)


if __name__ == "__main__":
    main()
