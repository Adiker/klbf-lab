# Regenerates docs/klbf/BAYSIDE-MORNING-V1.md from every result in docs/klbf/bench/bm-v1/*.json.
# Usage: python -I tools/bench-board.py
# Every result must pass tools/bench-check.py; one that does not stops the run and nothing is written.
import importlib.util, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('bench_check', HERE / 'bench-check.py')
bc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bc)

DOCS = HERE.parent / 'docs' / 'klbf'
FORM = 'https://github.com/PastiiJay/klbf-lab/issues/new?template=bench-bm-v1.yml'
HEAD = f"""# Bayside Morning v1 — Results

> **Indicative only.** These are self-measured runs: we check each result file (duration, no input,
> consistency, fingerprint), but we have not seen each player's screen, so we cannot confirm every
> effect was drawn correctly. A higher fps can come from lower settings or skipped shaders.
> Thank you to everyone who contributed a run.

Each run is the same 5-minute scene, measured by the build itself from the first world frame, with
input blocked after 5 s ([procedure](BENCH-BM-V1.md)). Only CERTIFIED results are listed. Each one
is checked with `tools/bench-check.py`: test and version, the full 5:00, the verdict, the frame
figures against each other, and the serial against the file name and the share line. Submit yours
through the [result form]({FORM}). Rows are sorted by average fps. Settings shows what the result
file records about quality, when it records it.

| Player | Project | GPU | CPU | RAM | avg | median | 1 % low | ≥ 12 fps % | Settings | date | proof |
|---|---|---|---|---|---|---|---|---|---|---|---|
"""


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    rows, bad = [], []
    for path in sorted((DOCS / 'bench' / 'bm-v1').glob('*.json')):
        try:
            d = json.loads(path.read_text(encoding='utf-8-sig'))
        except ValueError as e:
            bad.append(f'{path.name}: {e}')
            continue
        problems = bc.check(d, path.name)
        bad += [f'{path.name}: {x}' for x in problems]
        if not problems:
            rows.append((-d['fps']['avg'], d['serial'], bc.row(d, f'bench/bm-v1/{path.stem}')))
    if bad:
        sys.exit('\n'.join(bad))
    body = '\n'.join(r for *_, r in sorted(rows)) or '| _no results yet_ |||||||||||\n'
    (DOCS / 'BAYSIDE-MORNING-V1.md').write_text(HEAD + body.rstrip('\n') + '\n', encoding='utf-8', newline='\n')
    print(f'{len(rows)} result(s) written to docs/klbf/BAYSIDE-MORNING-V1.md')


if __name__ == '__main__':
    main()
