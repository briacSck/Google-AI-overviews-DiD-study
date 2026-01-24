# AI Overviews – Staggered DiD Impact Study

Staggered difference-in-differences analysis of the impact of Google's AI Overviews on website traffic. With data from the European Commission and personal data collection (scrapping).

## Status

Work in progress – this repository will host a cleaned, working paper personal code sample for the project conducted with Prof. Maximilian Schäfer at IMT Business School.

## Research Question

How does the introduction of AI Overviews affect organic web traffic for affected sites relative to comparable controls, in a staggered rollout setting?

## Design Overview

- **Data**: Panel data on website traffic before and after AI Overviews rollouts, by site and time.
- **Method**: Modern staggered DiD estimators (e.g. Callaway–Sant'Anna–type estimands and event studies) to avoid two-way FE biases.
- **Outputs**: Effect estimates by event time, aggregated ATT, and publication-quality figures/tables.

## Repository Structure

.
├── src/
│   ├── data_collection/
│   │   ├── scrape_robots_wayback.py    # Wayback Machine scraper
│   │   ├── schema.py                   # Data schemas
│   │   └── construct_panel.py          # Panel construction
│   ├── analysis/
│   │   └── R/
│   │       ├── 01_staggered_did_weekly.R
│   │       └── 02_channel_heterogeneity.R
│   └── visualization/                  # (Planned)
├── data/
│   ├── raw/                            # Not tracked (proprietary)
│   ├── processed/                      # Not tracked
│   └── README.md                       # Data documentation
├── docs/
│   ├── identification_strategy.md      # Research design
│   └── data_collection_guide.md        # Scraper documentation
├── tests/
│   ├── test_schema.py
│   └── test_construct_panel.py         # (Planned)
├── notebooks/                          # Exploratory analysis
├── output/                             # Plots and tables
└── README.md

## Stack

Primarily Python (with DiD libraries) and/or R (e.g. `did`, `fixest`) for staggered DiD estimation.
