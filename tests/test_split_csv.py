"""Check CSV fidelity and upload size limits, including quoted multiline records."""
import csv
import importlib.util
from pathlib import Path
import tempfile
import unittest

MODULE = Path(__file__).resolve().parents[1] / "skills/geopf-geocoding/scripts/split_csv.py"
spec = importlib.util.spec_from_file_location("split_csv", MODULE)
splitter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(splitter)


class SplitCSVTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "input.csv"
        self.output = self.root / "chunks"
        self.rows = [["id", "address", "postcode"], ["1", "Saint-Mandé, centre\nsecond line", "01000"],
                     ["2", 'Street "with quotes"', "00100"], ["3", "é" * 20, ""], ["4", "", ""]]

    def write(self, delimiter=","):
        with self.source.open("w", encoding="utf-8-sig", newline="") as handle:
            csv.writer(handle, delimiter=delimiter).writerows(self.rows)

    def test_record_and_byte_boundaries(self):
        self.write()
        original = self.source.read_bytes()
        paths = splitter.split_csv(self.source, self.output, max_rows=2, max_bytes=100)
        recovered = []
        for path in paths:
            self.assertLessEqual(path.stat().st_size, 100)
            self.assertTrue(path.read_bytes().startswith(splitter.BOM))
            with path.open(encoding="utf-8-sig", newline="") as handle:
                records = list(csv.reader(handle))
            self.assertEqual(records[0], self.rows[0])
            self.assertLessEqual(len(records) - 1, 2)
            recovered.extend(records[1:])
        self.assertEqual(recovered, self.rows[1:])
        self.assertEqual(self.source.read_bytes(), original)

    def test_semicolon_input(self):
        self.write(";")
        paths = splitter.split_csv(self.source, self.output, delimiter=";")
        with paths[0].open(encoding="utf-8-sig", newline="") as handle:
            self.assertEqual(list(csv.reader(handle)), self.rows)

    def test_existing_output_is_preserved(self):
        self.write()
        self.output.mkdir()
        sentinel = self.output / "keep.txt"
        sentinel.write_text("keep")
        with self.assertRaises(FileExistsError):
            splitter.split_csv(self.source, self.output)
        self.assertEqual(sentinel.read_text(), "keep")

    def test_oversized_record_is_rejected(self):
        self.write()
        with self.assertRaisesRegex(ValueError, "exceeds the byte limit"):
            splitter.split_csv(self.source, self.output, max_bytes=30)

    def test_bad_csv_is_rejected(self):
        self.source.write_text('id,address\n1,"unterminated\n')
        with self.assertRaises(csv.Error):
            splitter.split_csv(self.source, self.output)

    def test_header_only(self):
        self.source.write_text("id,address\n")
        self.assertEqual(splitter.split_csv(self.source, self.output), [])

    def test_wrong_column_count(self):
        self.source.write_text("id,address\n1,street,unexpected\n")
        with self.assertRaisesRegex(ValueError, "wrong number of columns"):
            splitter.split_csv(self.source, self.output)


if __name__ == "__main__":
    unittest.main()
