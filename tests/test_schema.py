from src.data_collection.schema import (
    EXPECTED_COLUMNS,
    MONTHLY_TRAFFIC_SCHEMA,
    WEEKLY_TRAFFIC_SCHEMA,
    ROBOTS_SCRAPE_SCHEMA,
    LANGUAGE_DETECTION_SCHEMA,
    AI_MODE_RELEASE_SCHEMA,
    AI_OVERVIEWS_RELEASE_SCHEMA,
)

def test_expected_columns_non_empty():
    assert len(EXPECTED_COLUMNS) >= 5

def test_all_schemas_non_empty():
    for schema in [
        MONTHLY_TRAFFIC_SCHEMA,
        WEEKLY_TRAFFIC_SCHEMA,
        ROBOTS_SCRAPE_SCHEMA,
        LANGUAGE_DETECTION_SCHEMA,
        AI_MODE_RELEASE_SCHEMA,
        AI_OVERVIEWS_RELEASE_SCHEMA,
    ]:
        assert isinstance(schema, dict)
        assert len(schema) > 0
