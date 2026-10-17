import unittest

from simple_time_zone_database import TimeZoneDatabase, TimezoneInfo


class TestTimeZoneDatabase(unittest.TestCase):
    def test_get_known_zone(self):
        db = TimeZoneDatabase()
        info = db.get("America/New_York")
        self.assertIsNotNone(info)
        self.assertEqual(info.name, "America/New_York")
        self.assertEqual(info.utc_offset_str, "-05:00")
        self.assertEqual(info.utc_offset_seconds, -18000)
        self.assertEqual(info.dst_offset_seconds, 3600)
        self.assertIn("US", info.countries)
        self.assertIn("CA", info.countries)

    def test_get_unknown_zone_returns_none(self):
        db = TimeZoneDatabase()
        self.assertIsNone(db.get("Nonexistent/Zone"))

    def test_case_sensitive_lookup(self):
        db = TimeZoneDatabase()
        self.assertIsNotNone(db.get("UTC"))
        self.assertIsNone(db.get("utc"))

    def test_all_zones_returns_sorted_list(self):
        db = TimeZoneDatabase()
        zones = db.all_zones()
        self.assertIsInstance(zones, list)
        self.assertEqual(zones, sorted(zones))
        self.assertIn("UTC", zones)

    def test_zones_for_country(self):
        db = TimeZoneDatabase()
        us_zones = db.zones_for_country("US")
        self.assertIn("America/New_York", us_zones)
        self.assertIn("America/Chicago", us_zones)
        self.assertIn("Pacific/Honolulu", us_zones)
        self.assertNotIn("Europe/London", us_zones)

    def test_zones_for_country_case_insensitive(self):
        db = TimeZoneDatabase()
        us_lower = db.zones_for_country("us")
        us_upper = db.zones_for_country("US")
        self.assertEqual(us_lower, us_upper)

    def test_zones_for_country_unknown(self):
        db = TimeZoneDatabase()
        self.assertEqual(db.zones_for_country("ZZ"), [])

    def test_zones_at_offset(self):
        db = TimeZoneDatabase()
        utc_zero = db.zones_at_offset(0)
        self.assertIn("UTC", utc_zero)
        self.assertIn("Europe/London", utc_zero)

    def test_zones_at_offset_positive(self):
        db = TimeZoneDatabase()
        tokyo = db.zones_at_offset(32400)
        self.assertIn("Asia/Tokyo", tokyo)

    def test_zones_at_offset_none_match(self):
        db = TimeZoneDatabase()
        self.assertEqual(db.zones_at_offset(999999), [])

    def test_offset_string_format_positive(self):
        db = TimeZoneDatabase()
        info = db.get("Asia/Tokyo")
        self.assertEqual(info.utc_offset_str, "+09:00")

    def test_offset_string_format_half_hour(self):
        db = TimeZoneDatabase()
        info = db.get("Asia/Kolkata")
        self.assertEqual(info.utc_offset_str, "+05:30")

    def test_offset_string_format_negative(self):
        db = TimeZoneDatabase()
        info = db.get("Pacific/Honolulu")
        self.assertEqual(info.utc_offset_str, "-10:00")

    def test_utc_zero_offset(self):
        db = TimeZoneDatabase()
        info = db.get("UTC")
        self.assertEqual(info.utc_offset_seconds, 0)
        self.assertEqual(info.utc_offset_str, "+00:00")
        self.assertEqual(info.dst_offset_seconds, 0)

    def test_dst_zero_for_non_dst_zone(self):
        db = TimeZoneDatabase()
        info = db.get("Asia/Tokyo")
        self.assertEqual(info.dst_offset_seconds, 0)

    def test_custom_zone_injection(self):
        zones = [{"name": "Custom/Zone", "std": -9000, "dst": 0, "countries": ["XX"]}]
        db = TimeZoneDatabase(zones=zones)
        info = db.get("Custom/Zone")
        self.assertEqual(info.utc_offset_seconds, -9000)
        self.assertEqual(info.utc_offset_str, "-02:30")
        self.assertEqual(info.countries, ["XX"])

    def test_custom_zone_default_dst(self):
        zones = [{"name": "Custom/NoDst", "std": 3600, "countries": ["YY"]}]
        db = TimeZoneDatabase(zones=zones)
        info = db.get("Custom/NoDst")
        self.assertEqual(info.dst_offset_seconds, 0)

    def test_custom_zone_deduplicates_countries(self):
        zones = [{"name": "Custom/Dup", "std": 0, "dst": 0, "countries": ["AA", "AA", "BB"]}]
        db = TimeZoneDatabase(zones=zones)
        info = db.get("Custom/Dup")
        self.assertEqual(info.countries, ["AA", "BB"])

    def test_len(self):
        zones = [
            {"name": "A/1", "std": 0, "dst": 0, "countries": []},
            {"name": "A/2", "std": 0, "dst": 0, "countries": []},
        ]
        db = TimeZoneDatabase(zones=zones)
        self.assertEqual(len(db), 2)

    def test_contains(self):
        db = TimeZoneDatabase()
        self.assertIn("UTC", db)
        self.assertNotIn("Nonexistent/Zone", db)

    def test_timezones_info_is_frozen(self):
        db = TimeZoneDatabase()
        info = db.get("UTC")
        self.assertIsInstance(info, TimezoneInfo)
        with self.assertRaises(Exception):
            info.name = "Changed"

    def test_default_database_has_expected_count(self):
        db = TimeZoneDatabase()
        self.assertEqual(len(db), 30)


if __name__ == "__main__":
    unittest.main()
