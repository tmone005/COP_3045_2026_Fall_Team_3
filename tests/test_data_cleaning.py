
"""Tests for cleaning and combining crash data."""

import unittest

import pandas as pd

from crash_analysis.data_cleaning import (
    clean_crashes,
    clean_vehicles,
    merge_datasets,
)


class TestDataCleaning(unittest.TestCase):

    def test_clean_crashes_removes_duplicates(self):
        crashes = pd.DataFrame({
            "CRASH_RECORD_ID": ["A", "A", "B", None],
            "INJURIES_TOTAL": [2, 2, 1, 0],
            "POSTED_SPEED_LIMIT": [30, 30, 25, 20],
            "WEATHER_CONDITION": ["CLEAR"] * 4,
            "LIGHTING_CONDITION": ["DAYLIGHT"] * 4,
            "FIRST_CRASH_TYPE": ["REAR END"] * 4,
        })

        result = clean_crashes(crashes)

        self.assertEqual(len(result), 2)
        self.assertEqual(result["CRASH_RECORD_ID"].tolist(), ["A", "B"])

    def test_clean_crashes_handles_missing_values(self):
        crashes = pd.DataFrame({
            "CRASH_RECORD_ID": ["A", "B"],
            "INJURIES_TOTAL": [-3, None],
            "POSTED_SPEED_LIMIT": ["30", "unknown"],
            "WEATHER_CONDITION": [None, "RAIN"],
            "LIGHTING_CONDITION": [None, "DARKNESS"],
            "FIRST_CRASH_TYPE": [None, "REAR END"],
        })

        result = clean_crashes(crashes)

        self.assertEqual(result["TOTAL_INJURIES"].tolist(), [0, 0])
        self.assertEqual(result.loc[0, "WEATHER_CONDITION"], "UNKNOWN")
        self.assertEqual(result.loc[0, "LIGHTING_CONDITION"], "UNKNOWN")
        self.assertEqual(result.loc[0, "FIRST_CRASH_TYPE"], "UNKNOWN")
        self.assertEqual(result.loc[0, "POSTED_SPEED_LIMIT"], 30)
        self.assertTrue(pd.isna(result.loc[1, "POSTED_SPEED_LIMIT"]))

    def test_clean_crashes_missing_column(self):
        with self.assertRaises(ValueError):
            clean_crashes(pd.DataFrame({"CRASH_RECORD_ID": ["A"]}))

    def test_clean_vehicles_counts_unique_units(self):
        vehicles = pd.DataFrame({
            "CRASH_RECORD_ID": ["A", "A", "A", "B", None],
            "CRASH_UNIT_ID": [1, 2, 2, 3, 4],
        })

        result = clean_vehicles(vehicles)

        counts = dict(zip(result["CRASH_RECORD_ID"], result["NUM_VEHICLES"]))
        self.assertEqual(counts, {"A": 2, "B": 1})

    def test_clean_vehicles_missing_column(self):
        with self.assertRaises(ValueError):
            clean_vehicles(pd.DataFrame({"CRASH_UNIT_ID": [1]}))

    def test_merge_datasets_handles_missing_vehicles(self):
        crashes = pd.DataFrame({
            "CRASH_RECORD_ID": ["A", "B", "C"],
            "TOTAL_INJURIES": [2, 0, 1],
        })

        vehicles = pd.DataFrame({
            "CRASH_RECORD_ID": ["A", "B"],
            "NUM_VEHICLES": [2, 1],
        })

        result = merge_datasets(crashes, vehicles)

        self.assertEqual(result["NUM_VEHICLES"].tolist(), [2, 1, 0])
        self.assertEqual(len(result), 3)


if __name__ == "__main__":
    unittest.main()
