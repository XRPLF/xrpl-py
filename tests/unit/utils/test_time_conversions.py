import time
from datetime import datetime, timezone
from unittest import TestCase

import xrpl.utils


class TestTimeConversions(TestCase):
    def test_posix_round_trip(self):
        current_time = time.time()
        time_whole_seconds = int(current_time)
        ripple_time = xrpl.utils.posix_to_ripple_time(current_time)
        round_trip_time = xrpl.utils.ripple_time_to_posix(ripple_time)
        self.assertEqual(time_whole_seconds, round_trip_time)

    def test_datetime_round_trip(self):
        now = datetime.now(timezone.utc)
        now_whole_seconds = now.replace(microsecond=0)
        ripple_time = xrpl.utils.datetime_to_ripple_time(now)
        round_trip_time = xrpl.utils.ripple_time_to_datetime(ripple_time)
        self.assertEqual(now_whole_seconds, round_trip_time)

    def test_ripple_epoch(self):
        dt = xrpl.utils.ripple_time_to_datetime(0)
        self.assertEqual(dt.isoformat(), "2000-01-01T00:00:00+00:00")

    def test_datetime_underflow(self):
        # "Ripple Epoch" time starts in the year 2000
        year_1999 = datetime(1999, 1, 1, 0, 0, tzinfo=timezone.utc)
        with self.assertRaises(xrpl.utils.XRPLTimeRangeException):
            xrpl.utils.datetime_to_ripple_time(year_1999)

    def test_posix_underflow(self):
        # "Ripple Epoch" time starts in the year 2000
        year_1999 = time.mktime(
            time.strptime("1999-01-01T00:00 UTC", "%Y-%m-%dT%M:%S %Z")
        )
        with self.assertRaises(xrpl.utils.XRPLTimeRangeException):
            xrpl.utils.posix_to_ripple_time(year_1999)

    def test_datetime_overflow(self):
        # "Ripple Epoch" time's equivalent to the "Year 2038 problem" is not until
        # 2136 because it uses an *unsigned* 32-bit int starting 30 years after
        # UNIX time's signed 32-bit int.
        year_2137 = datetime(2137, 1, 1, 0, 0, tzinfo=timezone.utc)
        with self.assertRaises(xrpl.utils.XRPLTimeRangeException):
            xrpl.utils.datetime_to_ripple_time(year_2137)

    def test_posix_overflow(self):
        year_2137 = time.mktime(
            time.strptime("2137-01-01T00:00 UTC", "%Y-%m-%dT%M:%S %Z")
        )
        with self.assertRaises(xrpl.utils.XRPLTimeRangeException):
            xrpl.utils.posix_to_ripple_time(year_2137)
