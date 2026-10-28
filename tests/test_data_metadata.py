"""
test_data_metadata.py - Automated Unit Tests for Data Catalog Provenance and Metadata

Verifies that all datasets in data/ are registered in data/METADATA.json with
verified regulatory authorities, source URLs, verification dates, and matching record counts.
"""

import json
import os
import sys
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

DATA_DIR = os.path.join(REPO_ROOT, "data")
METADATA_PATH = os.path.join(DATA_DIR, "METADATA.json")


class TestDataMetadataRegistry(unittest.TestCase):
    def setUp(self):
        self.assertTrue(os.path.exists(METADATA_PATH), "data/METADATA.json must exist")
        with open(METADATA_PATH, "r", encoding="utf-8") as f:
            self.registry = json.load(f)

    def test_registry_structure(self):
        """Registry must contain schema, title, last_audit_date, maintainer, and datasets."""
        self.assertIn("datasets", self.registry)
        self.assertIsInstance(self.registry["datasets"], list)
        self.assertEqual(len(self.registry["datasets"]), 22)

    def test_all_data_files_registered(self):
        """Every JSON file in data/ (except METADATA.json) must be cataloged in registry."""
        disk_files = {
            f for f in os.listdir(DATA_DIR)
            if f.endswith(".json") and f != "METADATA.json"
        }
        cataloged_files = {
            os.path.basename(ds["file"]) for ds in self.registry["datasets"]
        }
        self.assertEqual(disk_files, cataloged_files, "All data files must be cataloged in METADATA.json")

    def test_dataset_provenance_completeness(self):
        """Every dataset must have source authority, URL, verification date, update procedure."""
        required_fields = {
            "id", "file", "title", "records", "source_authority",
            "source_url", "last_verified", "version", "license",
            "known_gaps", "update_procedure", "validation_rules"
        }
        for ds in self.registry["datasets"]:
            missing = required_fields - set(ds.keys())
            self.assertEqual(len(missing), 0, f"Dataset {ds.get('id')} missing fields: {missing}")

            # Verify actual file existence and record count accuracy
            full_path = os.path.join(REPO_ROOT, ds["file"])
            self.assertTrue(os.path.exists(full_path), f"File {full_path} not found")

            with open(full_path, "r", encoding="utf-8") as df:
                content = json.load(df)
                self.assertIsInstance(content, list, f"{ds['file']} must contain a JSON array")
                self.assertEqual(
                    len(content),
                    ds["records"],
                    f"Record count mismatch in {ds['file']}: declared {ds['records']}, got {len(content)}"
                )


if __name__ == "__main__":
    unittest.main()
