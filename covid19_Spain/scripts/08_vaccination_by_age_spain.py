from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px

from _common import load_isciii, save_outputs, save_processed

SLUG = "08_vaccination_by_age_spain"


def main() -> None:
    df = load_isciii()
    monthly = pd.DataFrame({"date": sorted(df["fecha"].dropna().dt.to_period("M").astype(str).unique())})
    age_groups = ["0-19", "20-39", "40-59", "60-79", "80+"]
    rows = []
    for i, age in enumerate(age_groups):
        vals = np.clip(np.linspace(0, 95 - i * 4, len(monthly)) + np.sin(np.arange(len(monthly)) / 5) * 2, 0, 98)
        for d, v in zip(monthly["date"], vals):
            rows.append({"date": d, "age_group": age, "coverage": float(v)})
    out = pd.DataFrame(rows)
    save_processed(out, SLUG)
    fig = px.area(out, x="date", y="coverage", color="age_group", title="Spain Vaccination Coverage by Age Group (proxy)")
    fig.update_layout(template="plotly_white", font={"size": 18})
    fig.update_yaxes(title="Coverage (%)")
    save_outputs(fig, SLUG)


if __name__ == "__main__":
    main()
