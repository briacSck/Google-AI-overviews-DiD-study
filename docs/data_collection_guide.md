# Data Collection Guide

## Wayback Machine Scraper

### Purpose

The `scrape_robots_wayback.py` script collects historical web governance signals to analyze how sites control search engine access over time. This is relevant for understanding AI Overviews' impact on web publisher's behaviors relative to potential organic traffic change.

### What it collects

For each domain:
- **robots.txt files** across multiple Wayback snapshots
- **Parsed rules** (which user-agents are allowed/disallowed)
- **Meta robots tags** from homepages
- **X-Robots-Tag headers**

### Usage

**Single domain:**

```python
from src.data_collection.scrape_robots_wayback import scrape_robots_and_signals

df = scrape_robots_and_signals(
    domain="example.com",
    max_snapshots=30,
    from_timestamp="20220101000000",
    to_timestamp="20240101000000"
)

print(df.head())