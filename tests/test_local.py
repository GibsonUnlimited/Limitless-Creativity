import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from publishing_crew.calendar import upcoming
from publishing_crew.storage import import_catalog, search_catalog, save_idea, list_ideas, save_report, database, originality_check

class LocalToolsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env = patch.dict(os.environ, {"PUBLISHING_DATA_DIR": self.tmp.name})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def test_calendar_rollover_and_moveable_dates(self):
        dates = {e["event"]: e["date"] for e in upcoming("2026-12-20", 150)["events"]}
        self.assertEqual(dates["New Year's Day"], "2027-01-01")
        self.assertEqual(dates["Easter"], "2027-03-28")
        self.assertEqual(dates["Mother's Day"], "2027-05-09")
        self.assertTrue(upcoming("2026-12-20", 6)["events"][0]["publish_window_missed"])

    def test_empty_catalog_does_not_invent_history(self):
        self.assertEqual(search_catalog(), [])
        self.assertEqual(originality_check("A dragon learns patience")["records_checked"], 0)

    def test_idea_persistence_and_deduplication(self):
        a = save_idea("Dragon", "Learns patience", "4-6", "picture book", 8)
        b = save_idea("Dragon", "Learns patience", "4-6", "picture book", 8)
        self.assertEqual(a["id"], b["id"])
        self.assertEqual(len(list_ideas()), 1)
        self.assertEqual(originality_check("Dragon Learns patience")["matches"][0]["similarity"], 1.0)

    def test_report_and_parameterized_search(self):
        report = save_report("A report", "Evidence unknown")
        with database() as conn:
            self.assertEqual(conn.execute("SELECT content FROM research_reports WHERE id=?", (report["report_id"],)).fetchone()[0], "Evidence unknown")
        self.assertEqual(search_catalog("' OR 1=1 --"), [])

    def test_import_atomic_and_upsert(self):
        path = Path(self.tmp.name) / "catalog.json"
        row = {"id":"1", "kind":"book", "title":"Dragon", "summary":"Waits for a turn"}
        path.write_text(json.dumps([row]), encoding="utf-8")
        self.assertEqual(import_catalog(path), 1)
        row["summary"] = "Learns to wait"
        path.write_text(json.dumps([row]), encoding="utf-8")
        import_catalog(path)
        self.assertEqual(search_catalog("wait")[0]["summary"], "Learns to wait")
        row["id"] = "2"
        path.write_text(json.dumps([row, {"kind":"bad"}]), encoding="utf-8")
        with self.assertRaises(ValueError):
            import_catalog(path)
        self.assertEqual(len(search_catalog()), 1)

    def test_validation(self):
        with self.assertRaises(ValueError):
            save_idea("Title", "Concept", "4-6", "book", 11)
        with self.assertRaises(ValueError):
            upcoming("2026-01-01", 731)
        with self.assertRaises(ValueError):
            save_report("", "body")

if __name__ == "__main__":
    unittest.main()
