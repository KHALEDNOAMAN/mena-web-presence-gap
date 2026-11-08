"""Builds analysis.ipynb from code cells, so the notebook stays reproducible."""
import nbformat as nbf

nb = nbf.v4.new_notebook()
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell

nb.cells = [
    md("# MENA Web Presence Gap\n\n"
       "**Question:** how many local businesses in seven MENA cities have no working website, "
       "where is the gap largest, and are these weaker businesses or good businesses that are simply offline?\n\n"
       "**Data:** 10,802 Google Maps business listings collected for a website-building outreach project "
       "(Riyadh, Doha, Kuwait City, Cairo, Dubai, Amman, Istanbul). Each listing's website was checked and labelled "
       "`live`, `broken`, `social_only` or `none`. Only aggregated counts are published here, no names or contacts."),
    code("import pandas as pd\nimport matplotlib.pyplot as plt\n\n"
         "plt.rcParams.update({'figure.dpi': 120, 'axes.spines.top': False, 'axes.spines.right': False, 'font.size': 10})\n"
         "ACCENT, MUTED, C2, C3 = '#D97757', '#C9C5BC', '#6A9BCC', '#B8A26A'\n\n"
         "summary = pd.read_csv('data/summary.csv')\ncities = pd.read_csv('data/cities.csv')\n"
         "categories = pd.read_csv('data/categories.csv')\nquality = pd.read_csv('data/quality.csv')\nhot = pd.read_csv('data/hot.csv')\n"
         "summary"),
    md("## 1. How big is the gap?\n\"Without a working website\" = no website + social-media only + broken site."),
    code("total = summary['count'].sum()\n"
         "without = summary.loc[summary.status != 'Live website', 'count'].sum()\n"
         "print(f'Listings analysed: {total:,}')\n"
         "print(f'Without a working website: {without:,} ({without/total:.1%})')\n"
         "print(f'No website at all: {summary.set_index(\"status\").loc[\"No website\",\"count\"]:,}')\n"
         "print(f'Priority prospects (no site, 4.5+ stars, 100+ reviews, WhatsApp): {hot[\"count\"].iloc[0]:,}')"),
    md("## 2. The gap by city\nCollection was heavier in Riyadh (57% of rows), so cities are compared by **share**, not count.\n\n"
       "**Istanbul is left out of this comparison.** Its 157 listings came from a lead search for businesses *without* a website, "
       "so 0 of 157 having a live site is how they were collected, not a finding about the city. They still count in the totals."),
    code("cities['without_share'] = (cities.no_website + cities.social_only + cities.broken) / cities.total\n"
         "# Istanbul was collected from a no-website lead search, so its share is 100% by construction\n"
         "comparable = cities[cities.city != 'Istanbul']\n"
         "c = comparable.sort_values('without_share')\n"
         "parts = [('no_website','No website',ACCENT),('social_only','Social only',C2),('broken','Broken',C3),('live','Live site',MUTED)]\n"
         "fig, ax = plt.subplots(figsize=(8, 4))\nleft = pd.Series(0.0, index=c.index)\n"
         "for col, label, color in parts:\n    v = c[col] / c.total\n    ax.barh(c.city, v, left=left, color=color, label=label, height=0.6)\n    left += v\n"
         "for i, (s, n) in enumerate(zip(c.without_share, c.total)):\n    ax.text(1.01, i, f'{s:.0%}  (n={n:,})', va='center', fontsize=9)\n"
         "ax.set_xlim(0, 1); ax.xaxis.set_major_formatter(lambda x, _: f'{x:.0%}')\n"
         "ax.set_title('Share of businesses by website status', loc='left')\n"
         "ax.legend(ncol=4, loc='upper center', bbox_to_anchor=(0.45, -0.1), frameon=False)\n"
         "plt.tight_layout(); plt.savefig('images/by_city.png', bbox_inches='tight'); plt.show()\n"
         "comparable[['city','total','without_share']].sort_values('without_share', ascending=False)"),
    md("## 3. Which sectors need websites most?\n22 largest sectors (7,886 listings, 73% of the total)."),
    code("categories['share'] = categories.no_working_site / categories.total\n"
         "s = categories.sort_values('share')\nmed = s.share.median()\n"
         "fig, ax = plt.subplots(figsize=(8, 7))\n"
         "ax.barh(s.category, s.share, color=[ACCENT if v >= med else MUTED for v in s.share], height=0.65)\n"
         "for i, (v, n) in enumerate(zip(s.share, s.no_working_site)):\n    ax.text(v + 0.01, i, f'{v:.0%} ({n:,})', va='center', fontsize=8)\n"
         "ax.set_xlim(0, 1); ax.xaxis.set_major_formatter(lambda x, _: f'{x:.0%}')\n"
         "ax.set_title('Share of businesses without a working website, by sector', loc='left')\n"
         "plt.tight_layout(); plt.savefig('images/by_sector.png', bbox_inches='tight'); plt.show()\n"
         "categories.sort_values('share', ascending=False).head(8)"),
    md("## 4. Are offline businesses weaker businesses?\nCompare businesses **with** a live site against those **without** one on four signals."),
    code("quality['with_site_%'] = quality.with_site / quality.with_site_n\n"
         "quality['without_site_%'] = quality.without_site / quality.without_site_n\n"
         "q = quality.iloc[::-1].reset_index(drop=True)\n"
         "fig, ax = plt.subplots(figsize=(8, 3.8)); y = range(len(q)); h = 0.38\n"
         "ax.barh([i + h/2 for i in y], q['without_site_%'], height=h, color=ACCENT, label='No working site')\n"
         "ax.barh([i - h/2 for i in y], q['with_site_%'], height=h, color=MUTED, label='Live site')\n"
         "for i in y:\n    ax.text(q['without_site_%'][i] + 0.01, i + h/2, f\"{q['without_site_%'][i]:.0%}\", va='center', fontsize=8)\n"
         "    ax.text(q['with_site_%'][i] + 0.01, i - h/2, f\"{q['with_site_%'][i]:.0%}\", va='center', fontsize=8)\n"
         "ax.set_yticks(list(y)); ax.set_yticklabels(q.metric); ax.set_xlim(0, 1)\n"
         "ax.xaxis.set_major_formatter(lambda x, _: f'{x:.0%}')\n"
         "ax.set_title('Share of each group meeting the condition', loc='left'); ax.legend(frameon=False, loc='lower right')\n"
         "plt.tight_layout(); plt.savefig('images/quality.png', bbox_inches='tight'); plt.show()\n"
         "quality[['metric','with_site_%','without_site_%']].round(3)"),
    md("### Is each gap real, or noise?\nWith about 5,000 businesses in each group, even small gaps can be real. "
       "A 95% confidence interval on each difference (two-proportion, normal approximation) shows which ones are, and how big."),
    code("import numpy as np\n"
         "p1, p2 = quality['with_site_%'], quality['without_site_%']\n"
         "se = np.sqrt(p1*(1-p1)/quality.with_site_n + p2*(1-p2)/quality.without_site_n)\n"
         "quality['gap_pts'] = (p1 - p2) * 100\n"
         "quality['ci_low'] = (p1 - p2 - 1.96*se) * 100\n"
         "quality['ci_high'] = (p1 - p2 + 1.96*se) * 100\n"
         "quality[['metric','gap_pts','ci_low','ci_high']].round(1)"),
    md("## Findings\n"
       "1. **About half (51%) of listed businesses have no working website**, and 36% have no website at all.\n"
       "2. **The gap is widest in Amman (92%)** and narrowest in Dubai (32%) and Doha (36%). Istanbul is excluded because its listings were collected from a no-website lead search.\n"
       "3. **Offline does not mean low quality, but it does mean less visible.** Ratings are close: 56% vs 60% at 4.5+ stars, "
       "a real but small gap of 3.3 points (95% CI 1.4 to 5.1). Reviews differ more: 28% vs 38% have 100+ reviews. "
       "They lean on WhatsApp instead (76% vs 56%) and rarely have Instagram (7% vs 43%).\n"
       "4. **Wedding halls, printing presses and nurseries** have the largest gap; medical labs and accounting offices the smallest.\n"
       "5. **304 priority prospects** combine no website, strong ratings, 100+ reviews and a WhatsApp number to contact.\n\n"
       "**Limitations:** listings come from targeted Google Maps searches, not a random sample of all businesses; "
       "website status was checked at collection time; city sample sizes differ a lot; Istanbul's listings came from a no-website lead search, "
       "so it is excluded from the city comparison; cities may differ in sector mix, which can drive part of the city gap."),
]
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
nbf.write(nb, "analysis.ipynb")
