import importlib.util
from pathlib import Path
import tempfile
import unittest


GENERATOR_PATH = Path(__file__).resolve().parents[1] / "scripts" / "gen_log.py"
SPEC = importlib.util.spec_from_file_location("gen_log", GENERATOR_PATH)
gen_log = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(gen_log)


class GeneratorTests(unittest.TestCase):
    def test_generates_exact_requested_size(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_path = Path(temporary_directory) / "synthetic.log"

            gen_log.generate(output_path, 1024)

            self.assertEqual(output_path.stat().st_size, 1024)
            self.assertIn("INFO Application started", output_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
