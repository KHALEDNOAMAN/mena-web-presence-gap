"""Interactive version of the MENA Web Presence Gap analysis.

    pip install -r requirements.txt
    streamlit run app.py

Reads the same aggregated CSVs as the notebook, so the two always agree.
"""
from pathlib import Path

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

DATA = Path(__file__).parent / "data"
ACCENT, MUTED, C2, C3 = "#D97757", "#C9C5BC", "#6A9BCC", "#B8A26A"
STATUS = [
    ("no_website", "No website", ACCENT),
    ("social_only", "Social only", C2),
    ("broken", "Broken", C3),
    ("live", "Live site", MUTED),
]

st.set_page_config(page_title="MENA Web Presence Gap", layout="wide")


@st.cache_data
def load():
    return (
        pd.read_csv(DATA / "summary.csv"),
        pd.read_csv(DATA / "cities.csv"),
        pd.read_csv(DATA / "categories.csv"),
        pd.read_csv(DATA / "quality.csv"),
        pd.read_csv(DATA / "hot.csv"),
    )


summary, cities, categories, quality, hot = load()

st.title("MENA Web Presence Gap")
st.caption(
    "10,802 Google Maps business listings across seven MENA cities, each website checked and "
    "labelled live, broken, social only or none (October 2026). Aggregated counts only, "
    "no business names or contacts."
)

# ---------------------------------------------------------------- headline
total = int(summary["count"].sum())
live = int(summary.loc[summary.status == "Live website", "count"].iloc[0])
none_ = int(summary.loc[summary.status == "No website", "count"].iloc[0])
without = total - live
k1, k2, k3, k4 = st.columns(4)
k1.metric("Businesses analysed", f"{total:,}")
k1.caption("Seven cities, October 2026")
k2.metric("Without a working website", f"{without:,}")
k2.caption(f"{without / total:.0%} of all: none, social only or broken")
k3.metric("No website at all", f"{none_:,}")
k3.caption(f"{none_ / total:.0%} of all")
k4.metric("Priority prospects", f"{int(hot['count'].iloc[0]):,}")
k4.caption("No site, 4.5+ stars, 100+ reviews, WhatsApp")

tab_city, tab_sector, tab_quality, tab_method = st.tabs(
    ["By city", "By sector", "Are offline businesses weaker?", "Method"]
)

# ---------------------------------------------------------------- cities
with tab_city:
    show_istanbul = st.toggle(
        "Include Istanbul",
        value=False,
        help="Istanbul's 157 listings came from a search for businesses without a website, "
             "so its 100% is how they were collected, not a finding about the city.",
    )
    c = cities if show_istanbul else cities[cities.city != "Istanbul"]
    c = c.assign(without_share=(c.no_website + c.social_only + c.broken) / c.total)
    order = c.sort_values("without_share", ascending=False).city.tolist()

    long = c.melt(id_vars=["city", "total"], value_vars=[s[0] for s in STATUS],
                  var_name="status", value_name="count")
    long["share"] = long["count"] / long["total"]
    long["status"] = long["status"].map({k: label for k, label, _ in STATUS})
    long["order"] = long["status"].map({label: i for i, (_, label, _) in enumerate(STATUS)})

    chart = (
        alt.Chart(long)
        .mark_bar()
        .encode(
            y=alt.Y("city:N", sort=order, title=None),
            x=alt.X("share:Q", stack="normalize", axis=alt.Axis(format="%"), title=None),
            color=alt.Color("status:N",
                            scale=alt.Scale(domain=[s[1] for s in STATUS], range=[s[2] for s in STATUS]),
                            legend=alt.Legend(orient="bottom", title=None)),
            order="order:Q",
            tooltip=["city", "status", alt.Tooltip("count:Q", format=","),
                     alt.Tooltip("share:Q", format=".0%")],
        )
        .properties(height=48 * len(c))
    )
    st.altair_chart(chart, width="stretch")
    st.caption("Cities are compared by share, not count: Riyadh is 57% of all rows.")
    st.dataframe(
        c[["city", "total", "without_share"]].sort_values("without_share", ascending=False)
        .rename(columns={"city": "City", "total": "Listings", "without_share": "Without a working site"})
        .style.format({"Listings": "{:,}", "Without a working site": "{:.0%}"}),
        hide_index=True, width="stretch",
    )

# ---------------------------------------------------------------- sectors
with tab_sector:
    min_n = st.slider("Only sectors with at least this many listings", 100, 600, 100, step=50)
    k = categories[categories.total >= min_n].assign(
        share=lambda d: d.no_working_site / d.total)
    med = k.share.median()
    k["group"] = np.where(k.share >= med, "At or above median", "Below median")
    chart = (
        alt.Chart(k)
        .mark_bar()
        .encode(
            y=alt.Y("category:N", sort="-x", title=None,
                    axis=alt.Axis(labelOverlap=False, labelLimit=220)),
            x=alt.X("share:Q", axis=alt.Axis(format="%"), scale=alt.Scale(domain=[0, 1]),
                    title="Share without a working website"),
            color=alt.Color("group:N", scale=alt.Scale(
                domain=["At or above median", "Below median"], range=[ACCENT, MUTED]),
                legend=alt.Legend(orient="bottom", title=None)),
            tooltip=["category", alt.Tooltip("total:Q", title="listings", format=","),
                     alt.Tooltip("no_working_site:Q", title="without a site", format=","),
                     alt.Tooltip("share:Q", format=".0%")],
        )
        .properties(height=26 * len(k))
    )
    st.altair_chart(chart, width="stretch")
    st.caption(f"{len(k)} sectors, {int(k.total.sum()):,} listings. The 22 largest sectors cover "
               f"{categories.total.sum():,} of {total:,} listings ({categories.total.sum() / total:.0%}).")

# ---------------------------------------------------------------- quality
with tab_quality:
    q = quality.copy()
    q["with"] = q.with_site / q.with_site_n
    q["without"] = q.without_site / q.without_site_n
    se = np.sqrt(q["with"] * (1 - q["with"]) / q.with_site_n
                 + q["without"] * (1 - q["without"]) / q.without_site_n)
    q["gap"] = (q["with"] - q["without"]) * 100
    q["lo"] = q["gap"] - 196 * se
    q["hi"] = q["gap"] + 196 * se

    st.markdown(
        "Similar ratings, less visibility. Offline businesses are rated close to the rest, "
        "have fewer reviews, and run on WhatsApp instead of Instagram."
    )
    pair = q.melt(id_vars="metric", value_vars=["with", "without"], var_name="group", value_name="share")
    pair["group"] = pair["group"].map({"with": "Live site", "without": "No working site"})
    bars = (
        alt.Chart(pair)
        .mark_bar()
        .encode(
            y=alt.Y("metric:N", title=None, sort=q.metric.tolist(),
                    axis=alt.Axis(labelLimit=260)),
            yOffset="group:N",
            x=alt.X("share:Q", axis=alt.Axis(format="%"), scale=alt.Scale(domain=[0, 1]), title=None),
            color=alt.Color("group:N", scale=alt.Scale(domain=["No working site", "Live site"],
                                                        range=[ACCENT, MUTED]),
                            legend=alt.Legend(orient="bottom", title=None)),
            tooltip=["metric", "group", alt.Tooltip("share:Q", format=".1%")],
        )
        .properties(height=300)
    )
    st.altair_chart(bars, width="stretch")

    st.subheader("Is each gap real?")
    st.caption("Difference in percentage points (live site minus no working site), with a 95% confidence "
               "interval. An interval that does not cross zero is a real difference.")
    base = alt.Chart(q).encode(y=alt.Y("metric:N", title=None, sort=q.metric.tolist(),
                                       axis=alt.Axis(labelLimit=260)))
    ci = base.mark_rule(strokeWidth=2).encode(
        x=alt.X("lo:Q", title="Gap, percentage points"), x2="hi:Q")
    pts = base.mark_point(filled=True, size=80, color=ACCENT).encode(
        x="gap:Q",
        tooltip=["metric", alt.Tooltip("gap:Q", format=".1f"), alt.Tooltip("lo:Q", format=".1f"),
                 alt.Tooltip("hi:Q", format=".1f")])
    zero = alt.Chart(pd.DataFrame({"x": [0]})).mark_rule(strokeDash=[4, 4], color="gray").encode(x="x:Q")
    st.altair_chart((zero + ci + pts).properties(height=220), width="stretch")

# ---------------------------------------------------------------- method
with tab_method:
    st.markdown(
        """
- **Without a working website** = no website + social media only + broken site.
- Listings come from targeted Google Maps searches, not a random sample of every business in each city.
- **Istanbul's 157 listings** came from a lead search for businesses without a website. They count in the
  totals but are hidden from the city comparison by default.
- Cities may differ in sector mix, which can drive part of the city gap.
- Sector results cover the 22 largest sectors.
- Confidence intervals use the two-proportion normal approximation.
- Website status reflects the time of collection (October 2026).

Source and notebook: [github.com/KHALEDNOAMAN/mena-web-presence-gap](https://github.com/KHALEDNOAMAN/mena-web-presence-gap)
        """
    )
