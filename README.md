# MENA Web Presence Gap

Data analysis of **10,802 local businesses** across seven MENA cities, answering three questions:

1. How many businesses have no working website?
2. Where (city, sector) is the gap largest?
3. Are offline businesses weaker businesses, or good businesses that are simply offline?

The data comes from Google Maps listings I collected for a website-building outreach project. Each listing's website was checked and labelled `live`, `broken`, `social_only` or `none`. Only aggregated counts are published, with no business names or contact details.

## Key findings

| | |
|---|---|
| Businesses analysed | **10,802** |
| Without a working website | **5,524 (51%)** |
| No website at all | **3,851 (36%)** |
| Priority prospects (no site, 4.5+ stars, 100+ reviews, WhatsApp) | **304** |

**1. The gap varies a lot by city.** Nearly every listed business in Istanbul and Amman is offline, while Dubai and Doha are around one third.

![By city](images/by_city.png)

**2. Printing presses, wedding halls and nurseries need websites most.** Medical labs and accounting offices are the most online.

![By sector](images/by_sector.png)

**3. Offline does not mean low quality.** Businesses without a site are rated almost the same as those with one (56% vs 60% at 4.5+ stars). They rely on WhatsApp instead (76% vs 56%) and rarely have Instagram (7% vs 43%).

![Quality](images/quality.png)

## What's in the repo

```
analysis.ipynb      # full analysis with code, charts and findings
build_notebook.py   # regenerates the notebook from source
data/               # aggregated CSVs (by city, sector, quality signal)
images/             # charts exported from the notebook
```

## Run it

```bash
pip install -r requirements.txt
jupyter notebook analysis.ipynb
```

## Method and limitations

- "Without a working website" = no website + social-media only + broken site.
- Listings come from targeted Google Maps searches, not a random sample of every business in each city.
- Riyadh is 57% of rows, so cities are compared by share, not count. Istanbul has the smallest sample (n=157).
- Sector results cover the 22 largest sectors (about 83% of listings).
- Website status reflects the time of collection (October 2026).

**Tools:** Python, pandas, matplotlib, Jupyter.

## Author

Khaled Noaman · [LinkedIn](https://linkedin.com/in/khalednoaman1) · [GitHub](https://github.com/KHALEDNOAMAN)
