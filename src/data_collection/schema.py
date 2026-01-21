"""
Data schema definitions for the AI Overviews staggered DiD project.

These helpers document expected columns and types for the main datasets.
"""

# Main panel schema (you can keep or adapt this if you already had EXPECTED_COLUMNS)
EXPECTED_COLUMNS = {
    "site_id": "str",
    "date": "datetime",
    "traffic": "float",
    "treated": "int",            # 0/1 indicator
    "treatment_start_date": "datetime",
    "group": "int",              # treatment cohort
    "time": "int"                # period index
}

# Monthly traffic dataset ("monthly" type)
MONTHLY_TRAFFIC_SCHEMA = {
    "domain": "str",
    "country": "str",
    "channel": "str",                    # e.g. direct / referral / search
    "yearmonth": "period",               # year-month, e.g. 2024-01
    "desktop_marketing_channels_visits": "float",
    "mobile_marketing_channels_visits": "float",
}

# Weekly traffic dataset ("weekly" type)
WEEKLY_TRAFFIC_SCHEMA = {
    "domain": "str",
    "country": "str",
    "date": "date",                      # e.g. 2023-12-25
    "all_traffic_visits": "float",
    "all_traffic_pages_per_visit": "float",
    "all_traffic_average_visit_duration": "float",
    "all_traffic_bounce_rate": "float",
    "desktop_visits": "float",
    "desktop_pages_per_visit": "float",
    "desktop_average_visit_duration": "float",
    "desktop_bounce_rate": "float",
}

# Wayback Machine / robots.txt scraping dataset
ROBOTS_SCRAPE_SCHEMA = {
    "domain": "str",
    "timestamp": "str",                   # Wayback timestamp string
    "scraped_url": "str",
    "robots_txt": "str",                  # cleaned robots.txt content
    "raw_robots_response_text": "str",    # raw HTTP response body
    "robots_content_type": "str",
    "robots_rules": "dict_or_str",        # parsed rules, e.g. JSON-like
    "meta_robots": "str",
    "x_robots_tag": "str",
    "status_robots": "int",
    "status_home": "int",
    "error_details": "str",
    "datetime": "datetime",               # human-readable timestamp
}

# Language detection dataset
LANGUAGE_DETECTION_SCHEMA = {
    "domain": "str",
    "category": "str",                    # e.g. AI_Chatbots_and_Tools
    "country": "str",
    "rank": "int",
    "detected_language": "str",           # e.g. 'en', 'fr', 'zh', 'connection_error'
}

# AI Mode release dates
AI_MODE_RELEASE_SCHEMA = {
    "country": "str",
    "release_date": "date",
    "language_0": "str",
    "language_1": "str",
    "language_2": "str",
    "language_3": "str",
}

# AI Overviews release / wave info
AI_OVERVIEWS_RELEASE_SCHEMA = {
    "country": "str",
    "wave": "str",                        # e.g. 'Wave 1', 'Wave 2'
    "language_0": "str",
    "language_1": "str",
    "language_2": "str",
    "language_3": "str",
}
