# simple-time-zone-database

Provides offline access to IANA time zone identifiers and standard-time metadata, with no network access and no third-party dependencies.

## Usage

```python
from simple_time_zone_database import TimeZoneDatabase, TimezoneInfo

db = TimeZoneDatabase()

info: TimezoneInfo = db.get("America/New_York")
print(info.utc_offset_str)      # -05:00
print(info.utc_offset_seconds)  # -18000
print(info.countries)           # ['CA', 'US']

print(db.zones_for_country("US"))
print(db.zones_at_offset(0))
```

## Why

The `zoneinfo` module ships OS tzdata and can resolve identifiers, but it does not give you a browsable list of zones, their standard offsets, or country associations without parsing the raw tzdata files. This library provides that curated index as a static Python dict, offline.

The trade-off: the data is a fixed snapshot. It is correct as written but will go out of date as IANA publishes updates. For zones that have changed their standard offset historically, only the current standard-time offset is stored.

## The awkward edge

DST transition dates are not modeled. Each `TimezoneInfo` carries a `dst_offset_seconds` (typically 3600 or 0) but not when DST starts or ends. If you need to know whether a zone is in DST at a given instant, this library is insufficient — use `zoneinfo` or `datetime.tzinfo` for that. The `dst_offset_seconds` is the magnitude of the shift, not a flag that DST is active.
