# Data Documentation

## Overview

This directory contains raw and processed datasets for the AI Overviews impact study. Due to proprietary restrictions and file size, **data files are not tracked in Git**.

---

## Directory Structure

```
data/
├── raw/                    # Original unmodified data files
│   ├── w_2000_mediaos_US.csv
│   ├── w_2000_mediaos_GB.csv
│   ├── w_2000_mediaos_IE.csv
│   ├── m_2000_mediaos_US.csv
│   ├── m_2000_mediaos_GB.csv
│   └── m_2000_mediaos_IE.csv
├── processed/              # Cleaned analysis-ready datasets
│   ├── analysis_panel.csv
│   └── robots_wayback_analysis.csv
└── README.md              # This file
```

---

## Data Sources

### 1. Traffic Data

**Provider:** Co-Author working with/at the European Commission
**Coverage:** Top 2000 websites in US, GB, IE  
**Time period:** January 2024 – December 2024  
**Frequency:** Weekly and monthly

**Files:**
- `w_2000_mediaos_{US,GB,IE}.csv` — Weekly traffic data
- `m_2000_mediaos_{US,GB,IE}.csv` — Monthly data with channel breakdowns

**Access:** Proprietary.

### 2. AI Overviews Rollout Dates

**Source:** Google announcements
**File:** Embedded in analysis scripts (see `src/analysis/R/`)

**Treatment dates:**
- US: May 14, 2024
- GB: August 28, 2024
- IE: Never treated (control)

---

## Data Schemas

### Weekly Traffic Data

Expected columns (defined in `src/data_collection/schema.py` as `WEEKLY_TRAFFIC_SCHEMA`):

| Column | Type | Description |
|--------|------|-------------|
| `DNS` | string | Website domain (e.g., "reddit.com") |
| `country` | string | Country code (US, GB, IE) |
| `date` | date | Week start date (YYYY-MM-DD) |
| `total_visits` | float | Total weekly visits |
| `total_pages_per_visit` | float | Avg pages per session |
| `total_traffic_average_visit_duration` | float | Avg session duration (seconds) |
| `total_traffic_bounce_rate` | float | Bounce rate (0-1) |
| `PC_visits` | float | Desktop visits |
| `PC_pages_number_visit` | float | Desktop pages per session |
| `PC_average_visit_duration` | float | Desktop session duration |
| `PC_bounce_rate` | float | Desktop bounce rate |

### Monthly Traffic Data (with Channels)

Expected columns (defined as `MONTHLY_TRAFFIC_SCHEMA`):

| Column | Type | Description |
|--------|------|-------------|
| `domain` | string | Website domain |
| `country` | string | Country code |
| `channel` | string | Traffic channel (search, direct, referral, social, etc.) |
| `date_monthl_level` | string | Year-month (YYYY-MM) |
| `PC_marketing_channels_visits` | float | Desktop visits by channel |
| `phone_marketing_channels_visits` | float | Mobile visits by channel |

---

## Data Preparation

### Processing Pipeline

```r
# 1. Load and clean raw data
source("src/analysis/R/01_staggered_did_weekly.R")  # Loads w_*.csv files

# 2. Construct analysis-ready panel (if using Python pipeline)
# python src/data_collection/construct_panel.py
```

**Output:** `data/processed/analysis_panel.csv` with columns:
- `site_id`, `date`, `visits`, `treated`, `treatment_start_date`, `group`, `time`

---

## Privacy and Compliance

### Data Handling

- **Aggregated data only:** No individual-user information
- **Publicly indexed sites:** All domains are public websites

---

**Technical issues:**  
Open an issue at: [github.com/briacSck/Google-AI-overviews-DiD-study/issues](https://github.com/briacSck/Google-AI-overviews-DiD-study/issues)
