"""Offline regression cases use captured metadata, not a running MCP server."""

from pathlib import Path
import unittest

from mcp_tooldelta.catalog import CatalogError, load_catalog
from mcp_tooldelta.diff import compare

ROOT = Path(__file__).resolve().parent.parent


class RealCatalogTests(unittest.TestCase):
    def test_official_filesystem_snapshots(self):
        old = load_catalog(ROOT / "examples/filesystem/2025.1.14.json")
        new = load_catalog(ROOT / "examples/filesystem/2026.8.31.json")
        self.assertEqual(len(old), 11)
        self.assertEqual(len(new), 14)
        self.assertIn("read_file", old)
        report = compare({"tools": list(old.values())}, {"tools": list(new.values())})
        self.assertTrue(report.changes)
        self.assertEqual(compare({"tools": list(new.values())}, {"tools": list(new.values())}).counts["breaking"], 0)
        self.assertTrue(any(c.code == "tool.added" for c in report.changes))
        breaking = [c for c in report.changes if c.severity == "breaking"]
        self.assertEqual(len(breaking), 1)
        self.assertEqual(breaking[0].tool, "read_multiple_files")
        self.assertEqual(breaking[0].path, "/inputSchema/properties/paths/minItems")
        self.assertEqual(report.counts, {"breaking": 1, "review": 45, "info": 41})

    def test_legacy_unpinned_dependency_output_is_rejected(self):
        with self.assertRaises(CatalogError):
            load_catalog(ROOT / "examples/filesystem/2025.1.14-unpinned.json")


if __name__ == "__main__":
    unittest.main()
