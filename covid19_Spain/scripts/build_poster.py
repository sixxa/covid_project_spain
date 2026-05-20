"""Build the A0 portrait poster for the Spain COVID-19 project.

Curated to 7 main plots + heavy explanatory text, sized so that when printed
on A4 the figures and captions remain readable.

Run:
    python scripts/build_poster.py
Writes:
    covid19_Spain_poster.pdf  (A0, vector text + raster figures)
"""
from __future__ import annotations

import textwrap
from pathlib import Path

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Rectangle


def wrap(text: str, width: int) -> str:
    """Wrap paragraphs to a fixed character width, preserving blank lines."""
    out = []
    for para in text.split("\n\n"):
        para = " ".join(para.split())
        out.append(textwrap.fill(para, width=width))
    return "\n\n".join(out)

ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / "figures" / "static"
OUT_PDF = ROOT / "covid19_Spain_poster.pdf"

# A0 portrait in inches (33.1 x 46.8)
A0_W, A0_H = 33.1, 46.8

SPAIN_RED = "#C41E3A"
INK = "#1A1A1A"
PAPER = "#FFFFFF"


def add_image(ax, path: Path) -> None:
    ax.set_axis_off()
    if path.exists():
        img = mpimg.imread(path)
        ax.imshow(img)
    else:
        ax.text(0.5, 0.5, f"missing: {path.name}", ha="center", va="center",
                fontsize=14, color="red", transform=ax.transAxes)


def block_title(ax, text: str) -> None:
    ax.set_axis_off()
    ax.add_patch(Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                           facecolor=SPAIN_RED, edgecolor="none"))
    ax.text(0.02, 0.5, text, transform=ax.transAxes,
            ha="left", va="center", color="white",
            fontsize=26, fontweight="bold")


def caption(ax, text: str, width: int = 46) -> None:
    ax.set_axis_off()
    ax.text(0.0, 1.0, wrap(text, width), transform=ax.transAxes,
            ha="left", va="top", color=INK,
            fontsize=19, linespacing=1.35)


def body_text(ax, text: str, width: int = 60, size: int = 20, bold: bool = False) -> None:
    ax.set_axis_off()
    ax.text(0.0, 1.0, wrap(text, width), transform=ax.transAxes,
            ha="left", va="top", color=INK,
            fontsize=size, linespacing=1.4,
            fontweight=("bold" if bold else "normal"))


def main() -> None:
    fig = plt.figure(figsize=(A0_W, A0_H), facecolor=PAPER)

    # 26 rows x 12 cols master grid
    gs = GridSpec(
        nrows=26, ncols=12, figure=fig,
        left=0.025, right=0.975, top=0.985, bottom=0.015,
        hspace=0.9, wspace=0.30,
    )

    # ── Title banner ────────────────────────────────────────────────────────
    ax_title = fig.add_subplot(gs[0:2, :])
    ax_title.set_axis_off()
    ax_title.add_patch(Rectangle((0, 0), 1, 1, transform=ax_title.transAxes,
                                 facecolor=SPAIN_RED, edgecolor="none"))
    ax_title.text(0.02, 0.65, "COVID-19 in Spain",
                  transform=ax_title.transAxes, ha="left", va="center",
                  color="white", fontsize=68, fontweight="bold")
    ax_title.text(0.02, 0.22,
                  "A data story, with Poland as benchmark   "
                  "•   DAV Project 2026   •   University of Warsaw",
                  transform=ax_title.transAxes, ha="left", va="center",
                  color="white", fontsize=22)
    ax_title.text(0.98, 0.22,
                  "Sources: OWID  •  ISCIII  •  OxCGRT  "
                  "•  Google Mobility  •  Eurostat  •  INE",
                  transform=ax_title.transAxes, ha="right", va="center",
                  color="white", fontsize=16)

    # ── Key numbers banner ──────────────────────────────────────────────────
    ax_kn_title = fig.add_subplot(gs[2, :])
    block_title(ax_kn_title, "Spain in five numbers")

    numbers = [
        (">120,000", "confirmed COVID-19 deaths (2020–2024)"),
        ("342",      "deaths per 100,000 population"),
        ("66%",      "fewer international tourist arrivals in 2020"),
        ("16.5%",    "peak unemployment rate (Q3 2020)"),
        ("12.5%",    "peak test positivity, far above the WHO 5% threshold"),
    ]
    for i, (big, small) in enumerate(numbers):
        c0 = round(i * 12 / 5)
        c1 = round((i + 1) * 12 / 5)
        ax = fig.add_subplot(gs[3:5, c0:c1])
        ax.set_axis_off()
        ax.text(0.5, 0.78, big, ha="center", va="center",
                fontsize=46, fontweight="bold", color=SPAIN_RED,
                transform=ax.transAxes)
        ax.text(0.5, 0.22, small, ha="center", va="center",
                fontsize=14, color=INK, transform=ax.transAxes, wrap=True)

    # ── Context + definitions block ─────────────────────────────────────────
    ax_ctx_title = fig.add_subplot(gs[5, :])
    block_title(ax_ctx_title, "What this poster shows — and why Spain?")

    ax_ctx = fig.add_subplot(gs[6:8, :])
    body_text(
        ax_ctx,
        "Spain was one of the European countries hit earliest and hardest by SARS-CoV-2. "
        "Madrid recorded community transmission already in late February 2020, and the "
        "national State of Alarm (14 March 2020) imposed one of the strictest lockdowns on "
        "the continent. With a tourism-dependent economy (~12% of GDP) and an ageing "
        "population (median age 44), Spain combines an unusually severe epidemiological "
        "shock with an unusually severe economic shock — which is why we chose it. "
        "Throughout the poster we benchmark Spain against Poland, a country with a similar "
        "population size but a very different pandemic timeline, demographic profile and "
        "policy response.\n\n"
        "Definitions used in this poster.  "
        "Cases = laboratory-confirmed SARS-CoV-2 infections reported by ISCIII / OWID.  "
        "Excess mortality = observed deaths minus the 2015–2019 baseline for the same "
        "calendar week (Eurostat).  Stringency index = 0–100 score of containment "
        "policies (Oxford OxCGRT).  CFR = case-fatality rate = deaths / confirmed cases "
        "(a biased estimator when testing capacity changes — see Wave Analysis).  "
        "All population-adjusted figures use 2020 INE / Eurostat populations.",
        width=145, size=20,
    )

    # ── 3-column body layout ────────────────────────────────────────────────
    # Column ranges: left 0-3, middle 4-7, right 8-11
    LEFT = slice(0, 4)
    MID  = slice(4, 8)
    RIGHT = slice(8, 12)

    # ── LEFT COLUMN ─────────────────────────────────────────────────────────
    # The epidemic curve
    ax = fig.add_subplot(gs[8, LEFT]);  block_title(ax, "The epidemic curve")
    ax = fig.add_subplot(gs[9:12, LEFT]); add_image(ax, FIG_DIR / "01_cases_timeline.png")
    ax = fig.add_subplot(gs[12:14, LEFT])
    caption(ax,
        "Daily new cases per 100k inhabitants, Spain vs Poland. Five clear waves: "
        "the catastrophic first wave (Mar–May 2020, mostly invisible in "
        "confirmed cases because testing was unavailable), the summer 2020 "
        "resurgence, alpha (winter 20/21), delta (summer 21) and omicron "
        "(winter 21/22). After 2022, reporting changes flatten the curve.\n\n"
        "The first wave dwarfs everything else in mortality but is barely visible "
        "in confirmed cases — a measurement artefact, not a real low. "
        "Excess mortality (below) corrects for this.")

    ax = fig.add_subplot(gs[14, LEFT]); block_title(ax, "The true toll: excess mortality")
    ax = fig.add_subplot(gs[15:18, LEFT]); add_image(ax, FIG_DIR / "05_excess_mortality.png")
    ax = fig.add_subplot(gs[18:20, LEFT])
    caption(ax,
        "Weekly excess deaths over the 2015–2019 baseline (Eurostat). "
        "The spring-2020 peak in Spain is one of the largest ever recorded in a "
        "European country in peacetime. Subsequent waves are visible but "
        "progressively smaller — vaccination and acquired immunity blunted "
        "later peaks.\n\n"
        "Why this matters: confirmed-death counts depend on testing capacity "
        "and definitions. Excess mortality does not — making it the most "
        "reliable single indicator of pandemic severity.")

    # ── MIDDLE COLUMN ───────────────────────────────────────────────────────
    ax = fig.add_subplot(gs[8, MID]); block_title(ax, "Where and who")
    ax = fig.add_subplot(gs[9:12, MID]); add_image(ax, FIG_DIR / "12_choropleth_waves.png")
    ax = fig.add_subplot(gs[12:13, MID])
    caption(ax,
        "Cumulative cases per 100k by wave across Spain's 17 autonomous "
        "communities. Madrid leads the first wave; later waves spread more "
        "uniformly, with inland communities bearing higher per-capita burden.")

    ax = fig.add_subplot(gs[13:16, MID]); add_image(ax, FIG_DIR / "15_age_sex_pyramid.png")
    ax = fig.add_subplot(gs[16:18, MID])
    caption(ax,
        "Age-sex mortality pyramid. COVID-19 deaths are overwhelmingly "
        "concentrated in the 70+ age band, with male excess at every age above "
        "50 — a pattern repeated across Europe but especially pronounced in "
        "Spain due to a high share of nursing-home residents in early 2020.\n\n"
        "Spain's burden was not evenly distributed: by region, by age, or by "
        "sex. Public-health planning that treats the country as a single unit "
        "misses where the mortality actually fell.")

    ax = fig.add_subplot(gs[18, MID]); block_title(ax, "Economy: a tourism shock")
    ax = fig.add_subplot(gs[19:22, MID]); add_image(ax, FIG_DIR / "18_tourism_collapse.png")
    ax = fig.add_subplot(gs[22:24, MID])
    caption(ax,
        "International tourist arrivals collapsed by 66% in 2020 — the "
        "steepest drop on record. Recovery to pre-pandemic levels took until "
        "2023.\n\n"
        "Tourism is ~12% of Spanish GDP. The Balearic and Canary Islands saw "
        "regional GDP contractions above 20% in 2020 — the largest of any "
        "EU NUTS-2 region. This is the channel through which an "
        "epidemiological shock became a historic economic shock.")

    # ── RIGHT COLUMN ────────────────────────────────────────────────────────
    ax = fig.add_subplot(gs[8, RIGHT]); block_title(ax, "Forecasts: training window matters")
    ax = fig.add_subplot(gs[9:14, RIGHT]); add_image(ax, FIG_DIR / "22_sarima_2020_2024.png")
    ax = fig.add_subplot(gs[14:17, RIGHT])
    caption(ax,
        "SARIMA forecast of weekly cases. Top panel: model trained on "
        "2020–2022 only — it cannot 'see' the post-Omicron endemic "
        "decline and overshoots dramatically. Bottom panel: the same "
        "specification trained on 2020–2024 produces a plausible flat "
        "endemic baseline. Same model, very different conclusions.\n\n"
        "Take-away: for a disease in transition from epidemic to endemic, "
        "training-window choice dominates model choice. We report both "
        "windows deliberately rather than picking the one that 'looks right'.")

    ax = fig.add_subplot(gs[17, RIGHT]); block_title(ax, "Conclusions")
    ax = fig.add_subplot(gs[18:24, RIGHT])
    body_text(ax,
        "•  Spain's first wave was among the deadliest in Europe; excess "
        "mortality shows that confirmed counts understate it sharply.\n\n"
        "•  Mortality is concentrated in the elderly and in inland "
        "regions — a national average hides what matters.\n\n"
        "•  The tourism-dependent economy turned an epidemiological shock "
        "into a record economic contraction (-11% GDP in 2020).\n\n"
        "•  Vaccination cut the case-fatality rate by more than an order "
        "of magnitude between waves 3 and 5.\n\n"
        "•  SARIMA forecasts are highly sensitive to training-window "
        "choice — a methodological caution, not a model failure.",
        width=46, size=21,
    )

    # ── Footer ──────────────────────────────────────────────────────────────
    ax_foot = fig.add_subplot(gs[25, :])
    ax_foot.set_axis_off()
    ax_foot.text(0.5, 0.5,
                 "All scripts and processed data: scripts/  •  data/  "
                 "•  Interactive HTML version: covid19_Spain.html",
                 transform=ax_foot.transAxes, ha="center", va="center",
                 fontsize=14, color=INK, style="italic")

    fig.savefig(OUT_PDF, format="pdf", bbox_inches=None, facecolor=PAPER)
    plt.close(fig)
    print(f"Wrote {OUT_PDF}")


if __name__ == "__main__":
    main()
