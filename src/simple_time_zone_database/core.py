from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class TimezoneInfo:
    """Represents a single IANA time zone entry.

    Attributes:
        name: The canonical IANA time zone identifier, e.g. "America/New_York".
        utc_offset_str: The standard-time UTC offset as a string, e.g. "-05:00".
            The string is in sign + HH:MM format, always two-digit hours and minutes,
            with the sign always present (either + or -).
        utc_offset_seconds: The standard-time UTC offset in seconds, west of UTC
            being negative. This is the offset for standard time, not daylight
            time. DST transitions are intentionally not modeled; see README.
        dst_offset_seconds: The daylight saving offset in seconds relative to
            standard time. Zero when the zone does not observe DST. For zones
            that do, this is typically 3600 (one hour). Note that this value is a
            constant offset for the zone; transition dates are not modeled.
        countries: List of ISO 3166-1 alpha-2 country codes associated with this
            zone (sorted, deduplicated). May be empty; some zones are purely
            geographic and not tied to a single country.
    """
    name: str
    utc_offset_str: str
    utc_offset_seconds: int
    dst_offset_seconds: int
    countries: List[str]


class TimeZoneDatabase:
    """Offline access to IANA time zone identifiers and metadata.

    This is a static snapshot of the IANA tz database. It does not download
    updates, does not compute historical offsets, and does not model DST
    transition dates. The metadata is baked in at the time the library was
    written; see the module-level constant for what is included.

    The database is initialised from a plain dict structure so that callers
    (including tests) can inject their own subset. The default argument is a
    curated snapshot of major zones with verified standard-time offsets.
    """

    _DEFAULT_ZONES: Tuple[Dict[str, object], ...] = (
        {"name": "UTC", "std": 0, "dst": 0, "countries": []},
        {"name": "America/New_York", "std": -18000, "dst": 3600, "countries": ["US", "CA"]},
        {"name": "America/Chicago", "std": -21600, "dst": 3600, "countries": ["US"]},
        {"name": "America/Denver", "std": -25200, "dst": 3600, "countries": ["US"]},
        {"name": "America/Los_Angeles", "std": -28800, "dst": 3600, "countries": ["US"]},
        {"name": "America/Toronto", "std": -18000, "dst": 3600, "countries": ["CA"]},
        {"name": "America/Vancouver", "std": -28800, "dst": 3600, "countries": ["CA"]},
        {"name": "America/Sao_Paulo", "std": -10800, "dst": 0, "countries": ["BR"]},
        {"name": "America/Mexico_City", "std": -21600, "dst": 0, "countries": ["MX"]},
        {"name": "Europe/London", "std": 0, "dst": 3600, "countries": ["GB"]},
        {"name": "Europe/Paris", "std": 3600, "dst": 3600, "countries": ["FR"]},
        {"name": "Europe/Berlin", "std": 3600, "dst": 3600, "countries": ["DE"]},
        {"name": "Europe/Madrid", "std": 3600, "dst": 3600, "countries": ["ES"]},
        {"name": "Europe/Moscow", "std": 10800, "dst": 0, "countries": ["RU"]},
        {"name": "Africa/Cairo", "std": 7200, "dst": 0, "countries": ["EG"]},
        {"name": "Africa/Johannesburg", "std": 7200, "dst": 0, "countries": ["ZA"]},
        {"name": "Asia/Tokyo", "std": 32400, "dst": 0, "countries": ["JP"]},
        {"name": "Asia/Shanghai", "std": 28800, "dst": 0, "countries": ["CN"]},
        {"name": "Asia/Hong_Kong", "std": 28800, "dst": 0, "countries": ["HK"]},
        {"name": "Asia/Singapore", "std": 28800, "dst": 0, "countries": ["SG"]},
        {"name": "Asia/Seoul", "std": 32400, "dst": 0, "countries": ["KR"]},
        {"name": "Asia/Dubai", "std": 14400, "dst": 0, "countries": ["AE"]},
        {"name": "Asia/Kolkata", "std": 19800, "dst": 0, "countries": ["IN"]},
        {"name": "Asia/Karachi", "std": 18000, "dst": 0, "countries": ["PK"]},
        {"name": "Australia/Sydney", "std": 36000, "dst": 3600, "countries": ["AU"]},
        {"name": "Australia/Perth", "std": 28800, "dst": 0, "countries": ["AU"]},
        {"name": "Pacific/Auckland", "std": 43200, "dst": 3600, "countries": ["NZ"]},
        {"name": "Pacific/Honolulu", "std": -36000, "dst": 0, "countries": ["US"]},
        {"name": "Pacific/Guam", "std": 36000, "dst": 0, "countries": ["GU"]},
        {"name": "Antarctica/Palmer", "std": -10800, "dst": 0, "countries": ["AQ"]},
    )

    def __init__(self, zones: Optional[List[Dict[str, object]]] = None) -> None:
        if zones is None:
            zones = list(self._DEFAULT_ZONES)
        self._zones: Dict[str, TimezoneInfo] = {}
        for z in zones:
            name = str(z["name"])
            std = int(z["std"])
            dst = int(z.get("dst", 0))
            countries_raw = z.get("countries", [])
            countries = sorted(set(str(c) for c in countries_raw))
            info = TimezoneInfo(
                name=name,
                utc_offset_str=self._format_offset(std),
                utc_offset_seconds=std,
                dst_offset_seconds=dst,
                countries=countries,
            )
            self._zones[name] = info

    @staticmethod
    def _format_offset(seconds: int) -> str:
        sign = "+" if seconds >= 0 else "-"
        abs_seconds = abs(seconds)
        hours = abs_seconds // 3600
        minutes = (abs_seconds % 3600) // 60
        return f"{sign}{hours:02d}:{minutes:02d}"

    def get(self, name: str) -> Optional[TimezoneInfo]:
        """Return metadata for the given IANA identifier, or None if unknown.

        Lookup is case-sensitive, matching IANA conventions exactly. This is
        deliberate: IANA identifiers are case-sensitive, and normalising would
        hide typos from the caller.
        """
        return self._zones.get(name)

    def all_zones(self) -> List[str]:
        """Return all known IANA identifiers, sorted alphabetically."""
        return sorted(self._zones.keys())

    def zones_for_country(self, code: str) -> List[str]:
        """Return zone names for a country code, sorted alphabetically.

        The country code is matched case-insensitively and the comparison is
        normalised to uppercase, matching the convention in ISO 3166-1.
        """
        target = code.upper()
        result = []
        for name, info in self._zones.items():
            if target in [c.upper() for c in info.countries]:
                result.append(name)
        return sorted(result)

    def zones_at_offset(self, offset_seconds: int) -> List[str]:
        """Return zone names whose standard-time offset equals the given value.

        Only standard-time offsets are compared. This means, for example, that
        both Europe/London and UTC appear at offset 0, which is correct even
        though London observes BST in summer.
        """
        result = []
        for name, info in self._zones.items():
            if info.utc_offset_seconds == offset_seconds:
                result.append(name)
        return sorted(result)

    def __len__(self) -> int:
        return len(self._zones)

    def __contains__(self, name: str) -> bool:
        return name in self._zones
