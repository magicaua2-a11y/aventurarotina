import tempfile
import unittest
from pathlib import Path
from rotina import add_task, complete_task, connect, csv_safe, list_tasks, main


class RotinaTests(unittest.TestCase):
    def setUp(self):
        self.db = connect(":memory:")

    def tearDown(self):
        self.db.close()

    def test_task_lifecycle_and_filters(self):
        task_id = add_task(self.db, "Estudar SQL", "2026-12-01", 1)
        self.assertEqual(list_tasks(self.db)[0]["title"], "Estudar SQL")
        complete_task(self.db, task_id)
        complete_task(self.db, task_id)
        self.assertEqual(len(list_tasks(self.db)), 0)
        self.assertEqual(len(list_tasks(self.db, "done")), 1)

    def test_validation(self):
        for title, due, priority in [(" ", "2026-01-01", 1), ("a", "2026-02-30", 1), ("a", "2026-01-01", 4)]:
            with self.assertRaises(ValueError):
                add_task(self.db, title, due, priority)
        with self.assertRaises(ValueError):
            complete_task(self.db, 99)
        self.assertEqual(len(list_tasks(self.db, "all")), 0)

    def test_order_and_sql_parameterization(self):
        add_task(self.db, "depois", "2026-12-02", 1)
        add_task(self.db, "'); DROP TABLE tasks; --", "2026-12-01", 2)
        add_task(self.db, "urgente", "2026-12-01", 1)
        self.assertEqual(list_tasks(self.db)[0]["title"], "urgente")
        self.assertEqual(len(list_tasks(self.db)), 3)

    def test_persistence_and_csv_export(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tasks.db"
            db = connect(path)
            add_task(db, "=1+1", "2026-12-01")
            db.close()
            target = Path(directory) / "tasks.csv"
            main(["--db", str(path), "exportar", str(target)])
            self.assertIn("'=1+1", target.read_text(encoding="utf-8-sig"))
            self.assertEqual(csv_safe("normal"), "normal")


if __name__ == "__main__":
    unittest.main()
