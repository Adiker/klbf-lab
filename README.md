<p align="center"><img src="docs/klbf/logo.svg" width="120" alt="KLBF Lab"></p>
<h1 align="center">KLBF Lab 26 — AMD test branch</h1>
<p align="center">
  <img src="https://img.shields.io/badge/test-Lab%2026-ff7a00" alt="test: Lab 26">
  <img src="https://img.shields.io/badge/tested%20on-RX%209070%20XT-555" alt="tested on RX 9070 XT">
  <img src="https://img.shields.io/badge/stage-experimental-ffb000" alt="experimental">
  <img src="https://img.shields.io/badge/stable-4.4%20fps-ff7a00" alt="4.4 fps stable">
</p>

This branch is for **AMD Radeon (RDNA, 64-lane) cards**. It builds on the [fxceless/victory-gta6](https://github.com/fxceless/victory-gta6) fork (`578d459`, see [README.fxceless.md](README.fxceless.md); all rendering work there is its author's) and adds fixes found on an RX 9070 XT. It is a test build: expect visual defects. The stable branch is [`klbf-lab`](https://github.com/PastiiJay/klbf-lab).

No game files are included. You need your own legally obtained copy.

## What it fixes on AMD

| Problem on AMD | Cause we found | In this branch |
|---|---|---|
| Memory grows ~240 MB/s until Windows runs out (~100 GB) | compute shader `39f0e9aeb156a61c` never leaves the AMD driver's compiler | skipped by default in release builds (`VICTORY_SKIP_PIPELINES` overrides) |
| Purple/magenta blocks spreading on surfaces, stuck on screen | console 32-lane pixel shaders run in 64-lane waves on AMD; the upper half read the lower half's lane mask, producing NaN that piled up in temporal buffers | 32-lane pixel/vertex programs run per half wave (ballots and wave reductions per half); NaN/Inf filtered on colour outputs |
| White/pale hair, missing or late textures, look changing from run to run | the texture upload queue was fixed at 192 MB / 250 ms per frame; at 3–4 fps thousands of textures waited minutes | queue budget configurable, larger by default (`VICTORY_TEXTURE_QUEUE_MB`, `VICTORY_TEXTURE_QUEUE_MS`) |
| — | AMD orders some shared-dword 64-bit compares wrong | VIctory PR #1599 included |

## What you can expect (RX 9070 XT, Adrenalin 32.0.32029.2010)

| | Result |
|---|---|
| First gameplay scene | drawn, room fully lit by ambient light |
| Speed, stable settings | ~4.4 fps (≈220–230 ms/frame), no device removal in our run |
| Speed with card buffers (unstable) | ~5.4 fps (≈185 ms/frame), but the device was removed after ~11 min |
| Speed, fast settings (experimental) | 6–9 fps, but the device was removed after ~3 min |
| Longest session (earlier build of the same fixes) | ~28 min, first mission up to the robbery |
| Still wrong | ambient light comes out purple (its green channel is lost), triangle edges visible on lit surfaces, character faces too dark, white eyes, some invisible skin, some missing walls further in, very bright scenes over-exposed |

## Run

Build like VIctory (`cargo build --release`). Stable settings (remove the two `CARD_BUFFERS` lines; with them: ~5.4 fps but unstable):

```powershell
$env:VICTORY_LATE_WAIT = '1'
$env:VICTORY_WIDE_BACK = '1'
$env:VICTORY_CARD_BUFFERS_MIN_MB = '1'
$env:VICTORY_CARD_BUFFERS_MB = '1024'
target\release\victory.exe run <game dir>\<the title's exe> --execute
```

Fast settings (experimental, crashed after ~3 min here): `VICTORY_LATE_WAIT=3` instead of 1. DRED (`VICTORY_D3D12_DRED`) made no speed difference here.

If the AMD shader compiler crashes (`amdxc64.dll`), add the 41 `CS_RaytracingResolve` hashes from [fxceless #3](https://github.com/fxceless/victory-gta6/issues/3) to `VICTORY_SKIP_PIPELINES` (comma-separated, keep `39f0e9aeb156a61c`). The first launch compiles shaders for several minutes; later launches reuse them. Keep the game's high-contrast option off for real colours.

Please report results in an [issue](https://github.com/PastiiJay/klbf-lab/issues): GPU, driver, how long it ran, fps in the window title, and what looks wrong. Patch notes: [CHANGELOG.md](CHANGELOG.md). Full run log: [docs/klbf/results.md](docs/klbf/results.md).

Product names are only used to say what this works with; they belong to their owners. KLBF Lab is not affiliated with them. License: GPL-3.0.
