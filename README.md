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

- `src/data_collection/`: Scripts to collect and preprocess traffic and treatment timing data.
- `src/analysis/`: Estimation code for staggered DiD (ATT(g,t), aggregation, robustness).
- `src/visualization/`: Figure and table generation (event-study plots, ATT summaries).
- `data/raw/`: Unmodified input data (not tracked in Git).
- `data/processed/`: Cleaned panel and analysis-ready datasets (not tracked in Git).
- `notebooks/`: Exploratory analysis and sanity-check notebooks.
- `tests/`: Minimal tests for key transformations and estimators.
- `docs/`: Design notes, methodological choices, and replication instructions.

## Stack

Primarily Python (with DiD libraries) and/or R (e.g. `did`, `fixest`) for staggered DiD estimation.
