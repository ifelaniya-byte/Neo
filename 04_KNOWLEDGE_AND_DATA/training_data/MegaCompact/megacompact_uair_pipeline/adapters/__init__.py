"""Historical and read-only adapters for paper simulation assurance."""
from .historical import (
    HistoricalAdapter,
    NormalizedHistoricalEvent,
    write_sample_jsonl,
)

__all__ = [
    "HistoricalAdapter",
    "NormalizedHistoricalEvent",
    "write_sample_jsonl",
]

from .feed_format import (
    validate_feed,
    load_feed,
    ingest_feed_file,
    write_example_feed,
    feed_to_pipeline_events,
    SCHEMA_VERSION,
)
