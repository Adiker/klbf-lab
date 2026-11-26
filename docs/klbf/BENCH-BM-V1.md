# KLBF Lab Bench · Bayside Morning v1 (BM-v1)

One 5-minute run, always the same scene, to compare machines and versions. The build measures
itself: you load one save, press Continue and touch nothing. Results: [Bayside Morning v1 — Results](BAYSIDE-MORNING-V1.md).

## Prerequisites

- A KLBF Lab build that includes the bench, and your own legally obtained copy of the title.
- The title already reaches gameplay on your machine.
- A progress point at the male lead's house (about 3 % progress, where you can first save in his bed).
- Nothing else heavy running during the 5 minutes.

## Make the save (once)

1. At the male lead's house, sleep in his bed until the morning.
2. Get dressed.
3. Go down to the workshop and take the fishing book.
4. Save in **slot 1**, then quit.

Every run starts from this save, so the time of day, the light and the scene are the same for
everyone. Keep a copy of it as described in [MEASUREMENT.md](MEASUREMENT.md#keep-your-morning-save),
and keep your save files to yourself: they can carry your console profile's ids.

## Run

1. Set the variables (only the first is required):
   - `KLBF_BENCH=bm-v1` turns the bench on. Without it nothing changes.
   - `KLBF_BENCH_PLAYER=<nickname>` is written on the card (otherwise "anonymous"). To be linked on
     the board, use your GitHub login.
   - `VICTORY_SKIP_MOVIES=end` skips the intro movies.
2. Start the game, load the save and press **Continue**. If Continue does not bring you to the
   morning save, use **Load** and pick slot 1 (it sits one line lower, under the automatic save).
3. Touch nothing.

```powershell
$env:KLBF_BENCH = "bm-v1"; $env:KLBF_BENCH_PLAYER = "<nickname>"; $env:VICTORY_SKIP_MOVIES = "end"
```

The measurement starts at the first world frame. 5 seconds later input is blocked: the game gets an
idle controller and no keyboard; presses are only counted. Nothing is drawn over the game during the
run; only the time of each frame is recorded. At **5:00** the run stops by itself. **F10** or closing
the window stops early (PARTIAL, not comparable).

The card then covers the screen. A key or button closes it (or it closes after 60 s) and the game
exits.

## What the card means

- **Left**: the date and how the run ended ("5:00 complete · no input", or "PARTIAL m:ss / 5:00 – not comparable").
- **Round stamp**: the serial (8 characters, a fingerprint of every frame time and of the result) and
  the date. The band across it is the verdict:
  - **CERTIFIED**: the full 5:00, the graphics device kept, at most 1 % black frames, no stall of 10 s
    or more, at least 300 frames.
  - **PARTIAL**: stopped before 5:00. Not comparable.
  - **INVALID**: 5:00 done, but one of the checks failed.
- **from:** the project and version (`owner/repo @ commit`), read from git at build time; "(declared)"
  when given by `KLBF_PROJECT_NAME`, "unknown (local build)" otherwise. Below it, the nickname.
- **Big number**: average fps.
- **Four boxes**: median fps; 1 % low (average of the slowest 1 % of frames); max fps; time ≥ 12 fps
  (share of the time spent at 12 fps or more).
- **Thin line**: freezes (frames over 200 ms), measured duration, inputs blocked.
- **Bold line**: the machine (GPU and its memory, CPU, RAM, Windows).
- **Share line**: the one-line summary.

The files are in `bench-results\` next to the exe: `KLBF-Bench-BM-v1-<serial>.png` (the card),
`.json` (every figure, including 5 % low, min, black frames, shaders and pipelines compiled during
the run, memory at the end) and `.txt` (readable summary and share line).

## Share

Your results stay on your machine unless you choose to share or submit them.

- **To share**: post the card PNG with the share line from the `.txt` under it, on Fluxer or in a
  GitHub comment. For example:
  `[KLBF Lab Bench BM-v1] owner/repo@abc1234 | RX 9070 XT | Ryzen 7 9800X3D | avg 14.2 fps, 1% low 2.2 | CERTIFIED | 8e45f78d`
- **To appear on the board**: submit the JSON and the card PNG through the
  [result form](https://github.com/PastiiJay/klbf-lab/issues/new?template=bench-bm-v1.yml). Only
  CERTIFIED results are listed. Each one is checked with `python -I tools/bench-check.py <file>.json`.

Only the card, please: no screenshots of the game. When a shared result looks doubtful, we may ask
for its JSON.
