from __future__ import annotations

import plotly.express as px

from _common import apply_layout, load_mobility, save_outputs, save_processed

SLUG = "11_mobility_lockdown"


def main() -> None:
    df = load_mobility()
    sp = df[(df["country_region"] == "Spain") & (df["sub_region_1"].isna())].copy()
    sp = sp.rename(
        columns={
            "retail_and_recreation_percent_change_from_baseline": "retail",
            "transit_stations_percent_change_from_baseline": "transit",
            "workplaces_percent_change_from_baseline": "workplaces",
        }
    )
    out = sp[["date", "retail", "transit", "workplaces"]]
    save_processed(out, SLUG)
    long_df = out.melt(id_vars="date", var_name="metric", value_name="pct_change")
    fig = px.line(long_df, x="date", y="pct_change", color="metric")
    fig = apply_layout(fig, "Spain Mobility During and After Lockdown", "% change from baseline")
    save_outputs(fig, SLUG)


if __name__ == "__main__":
    main()
