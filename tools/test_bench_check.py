"""bench-check.py accepts a consistent BM-v1 result and rejects tampered ones."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('bench_check', Path(__file__).with_name('bench-check.py'))
bc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bc)

# 18,000 frames at 60 fps = 300 s; slowest frame 33.3 ms.
VALID = {
    "bench": "KLBF Lab Bench", "test": "Bayside Morning v1", "test_id": "BM-v1",
    "stamp": "CERTIFIED", "reason": "5:00 complete · no input", "stop": "5:00 reached",
    "serial": "8e45f78d", "date": "2026-11-26T21:04:05",
    "project": "PastiiJay/klbf-lab", "project_source": "git", "sha": "abc1234", "player": "PastiiJay",
    "gpu": "AMD Radeon RX 9070 XT", "gpu_vram_gb": 15.9, "cpu": "AMD Ryzen 7 9800X3D 8-Core Processor",
    "ram_gb": 31.6, "os": "Windows 11 (26200)",
    "duration_s": 300.0, "target_s": 300, "frames": 18000,
    "fps": {"avg": 60.00, "median": 60.50, "low_1pct": 40.00, "low_5pct": 50.00, "min": 30.03, "max": 70.00},
    "pct_time_ge_12fps": 100.00, "freezes_over_200ms": 0, "longest_frame_ms": 33.3,
    "black_frames": 0, "device_removed": False, "inputs_blocked": 0,
    "shaders_translated": 0, "pipelines_compiled": 0,
    "vram_end_mb": 9000, "vram_budget_mb": 15000, "ram_end_mb": 20000,
    "share": "[KLBF Lab Bench BM-v1] PastiiJay/klbf-lab@abc1234 | RX 9070 XT | Ryzen 7 9800X3D | "
             "avg 60.0 fps, 1% low 40.0 | CERTIFIED | 8e45f78d",
}
NAME = 'KLBF-Bench-BM-v1-8e45f78d.json'


def tampered(**changes):
    d = copy.deepcopy(VALID)
    for key, value in changes.items():
        if key.startswith('fps_'):
            d['fps'][key[4:]] = value
        else:
            d[key] = value
    return d


class BenchCheckTests(unittest.TestCase):
    def test_valid_sample_passes(self):
        self.assertEqual(bc.check(VALID, NAME), [])

    def test_tampered_samples_fail(self):
        cases = {
            'avg raised': tampered(fps_avg=90.0),
            'short run': tampered(duration_s=200.0, stop='F10'),
            'partial': tampered(stamp='PARTIAL'),
            'black frames': tampered(black_frames=500),
            'min not from longest frame': tampered(fps_min=50.0),
            'other version': tampered(test_id='BM-v2'),
            'serial edited': tampered(serial='deadbeef'),
            'missing field': {k: v for k, v in VALID.items() if k != 'frames'},
        }
        for label, d in cases.items():
            with self.subTest(label):
                self.assertNotEqual(bc.check(d, NAME), [])
        self.assertNotEqual(bc.check(VALID, 'KLBF-Bench-BM-v1-00000000.json'), [])

    def test_cli_prints_one_row(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / NAME
            path.write_text(json.dumps(VALID), encoding='utf8')
            out = subprocess.run([sys.executable, '-I', str(Path(__file__).with_name('bench-check.py')), str(path)],
                                 capture_output=True, text=True, encoding='utf8')
            self.assertEqual(out.returncode, 0, out.stderr)
            self.assertEqual(len(out.stdout.strip().splitlines()), 1)
            self.assertIn('[PastiiJay](https://github.com/PastiiJay)', out.stdout)
            self.assertIn('bench/bm-v1/KLBF-Bench-BM-v1-8e45f78d.png', out.stdout)
            path.write_text(json.dumps(tampered(fps_avg=90.0)), encoding='utf8')
            bad = subprocess.run([sys.executable, '-I', str(Path(__file__).with_name('bench-check.py')), str(path)],
                                 capture_output=True, text=True, encoding='utf8')
            self.assertEqual(bad.returncode, 1)

    def test_settings_column(self):
        self.assertEqual(bc.settings(VALID), '')
        self.assertEqual(bc.settings(tampered(profile='S', upscaler='FSR', draws_per_frame=6500)),
                         'profile S · FSR · 6500 draws/frame')


if __name__ == '__main__':
    unittest.main()
