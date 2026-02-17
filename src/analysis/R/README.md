# R Analysis Scripts

## Overview

This folder contains staggered difference-in-differences estimation code using the `did` package (Callaway & Sant'Anna, 2021) and the related checks for heterogeneity-robust DiD analysis.

---

## Scripts

### `01_staggered_did_weekly.R`

**Main analysis:** Weekly traffic impact by platform

- Loads weekly traffic data for US, GB, IE
- Implements Callaway-Sant'Anna group-time ATT estimation
- Runs both levels and log specifications
- Generates event-study plots with 95% CIs
- Outputs summary plots and tables

**Usage:**
```r
source("src/analysis/R/01_staggered_did_weekly.R")
```

**Outputs:** `output/did_weekly/`

---

### `02_channel_heterogeneity.R`

**Heterogeneity analysis:** Channel composition effects

- Uses monthly data with marketing-channel breakdowns
- Estimates ATT on channel shares
- Identifies which traffic sources (search, direct, referral) are affected

**Usage:**
```r
source("src/analysis/R/02_channel_heterogeneity.R")
```

**Outputs:** `output/did_channels/`

---

## Quick Start

### 1. Install Dependencies

```r
install.packages(c(
  "dplyr", "tidyr", "did", "ggplot2", "ggdid", "xtable"
))
```

### 2. Prepare Data

Place data files in `data/raw/`:
- Weekly: `w_2000_{US,GB,IE}.csv`
- Monthly: `m_2000_{US,GB,IE}.csv`

See `data/README.md` for data requirements and access.

### 3. Run Analysis

```r
# Weekly DiD
source("src/analysis/R/01_staggered_did_weekly.R")

# Channel heterogeneity
source("src/analysis/R/02_channel_heterogeneity.R")
```

---

## Requirements

- **R version:** ≥ 4.2.0
- **Key packages:** `did` (Callaway-Sant'Anna estimator), `ggplot2`, `dplyr`
- **Data:** See `data/README.md` for file specifications

---

## Outputs

**Event-study plots:**
- `output/did_weekly/*.png` (platform-specific)
- `output/did_channels/eventstudy_*.png` (channel-specific)

**Summary tables:**
- `output/did_weekly/summary_results.csv`
- `output/did_channels/channel_results.csv`
- `output/did_weekly/did_results_tables.tex` (LaTeX)

---

## Methodological Details

For identification strategy, treatment timing, and assumptions, see:
- **`docs/identification_strategy.md`** — Research design and causal inference approach

---

## Reference

Callaway, B., & Sant'Anna, P. H. (2021). Difference-in-differences with multiple time periods. *Journal of Econometrics*, 225(2), 200–230. [https://doi.org/10.1016/j.jeconom.2020.12.001](https://doi.org/10.1016/j.jeconom.2020.12.001)
