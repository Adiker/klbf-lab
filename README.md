<p align="center"><img src="docs/klbf/logo.svg" width="120" alt="KLBF Lab"></p>
<h1 align="center">KLBF Lab</h1>
<p align="center">
  <img src="https://img.shields.io/badge/version-Lab%2035-1f46c8" alt="version: Lab 35">
  <img src="https://img.shields.io/badge/7.3%20fps-74%20min%20without%20a%20crash-1f46c8" alt="7.3 fps, 74 min without a crash">
  <img src="https://img.shields.io/badge/license-GPL--3.0-555" alt="GPL-3.0">
  <a href="https://github.com/PastiiJay/klbf-lab-beta"><img src="https://img.shields.io/github/stars/PastiiJay/klbf-lab-beta?label=KLBF%20Lab%20Beta%20stars&color=555" alt="KLBF Lab Beta stars"></a>
</p>

<p align="center"><b>7.3 fps on average in the world (1% low 7.0), 74 minutes in one session without a crash, on an AMD Radeon RX 9070 XT.</b></p>

An open lab that runs the Xbox Series X|S (Scarlett) build of the game natively on a Windows PC: a GDK compatibility layer (`kernelx`, `xgameruntime`, `d3d12_xs` → host D3D12, RDNA2 → DXIL shader translation) that combines the best fixes from open compatibility projects into one tested build. It builds on [VIctory](https://github.com/Marvisak/VIctory) and the [fxceless/victory-fork](https://github.com/fxceless/victory-fork) (all rendering work there is its authors', see [README.fxceless.md](README.fxceless.md)), with fixes found on our own machine and fixes from other contributors, credited below.

This is the one version we recommend. It is meant for every graphics card; so far we have tested it on an AMD Radeon RX 9070 XT, and reports from other cards (NVIDIA, Intel, other AMD) are very welcome. New builds are tried first in **[KLBF Lab Beta](https://github.com/PastiiJay/klbf-lab-beta)**, the test lab, where issues and test reports go.

## Status (2026-11-25, Lab 35)

Tested on one machine: AMD Radeon RX 9070 XT 16 GB (Adrenalin 32.0.32029.2010), AMD Ryzen 7 9800X3D, 32 GB RAM, Windows 11. Self-reported, one machine so far.

| Stage | Status | Notes |
|---|---|---|
| Boot, first-run screens, intro, menus | ✅ Works | 30 fps |
| In game (prison prologue) | ✅ Player in control | the character moves under the player's control; earlier builds reached the first mission's robbery |
| Frame rate in game, recommended settings | 🟡 ~7.3 fps average | in the world only, loading excluded (first 2 min of the run left out): average 7.34, median 7.3, 1% low 7.0, 0.1% low 6.9, peak 7.7, over 72 min; renders at 1280×720 (`--console series-s`), upscaled to 1920×1080 with AMD FSR |
| Frame rate in game, native resolution | 🟡 ~5 fps | about 200 ms per frame |
| Stability | ✅ 74 min in one session without a crash | recommended settings; 41 min at native resolution |
| Rendering | 🟡 Mostly right | cell walls, faces, hair and outfits drawn; purple tint on some papers, stretched triangles around some characters, banding in skies |
| Story progress | 🟡 Prologue | further progress to be measured |

How we measure: the frame rate the layer logs about every 5 s, in the world only (loading screens and the first 2 minutes of shader compiling left out). Lows are taken from those 5 s averages, so single-frame dips may go lower.

## Community and test reports

This repository is new (25 Nov 2026), but the project is older: it started on **[KLBF Lab Beta](https://github.com/PastiiJay/klbf-lab-beta)**, where every build is tried first: **10 stars and 2 forks** there on 25 Nov 2026, plus the test reports below. Reports from other testers there:

- [RX 6900 XT (RDNA2), Windows 10](https://github.com/PastiiJay/klbf-lab-beta/issues/2): runs our builds for 19 min without a device removal; with Lab 33 the player's face renders on that card too; it helped us test two fixes.
- [RX 6800 (RDNA2)](https://github.com/PastiiJay/klbf-lab-beta/issues/4): measured our AMD fixes on that card (same speed with them; purple sky and wet-looking skin gone).
- [DirectStorage page lists](https://github.com/PastiiJay/klbf-lab-beta/issues/3): an analysis by another tester, now part of the build.

No game files are included. You need your own legally obtained copy.

## What it fixes

| Problem | Cause we found | Fix |
|---|---|---|
| Memory grows ~240 MB/s until Windows runs out | compute shader `39f0e9aeb156a61c` never leaves the AMD driver's compiler | skipped |
| Purple/magenta blocks stuck on screen | console 32-lane pixel shaders run in 64-lane waves on AMD; NaN piled up in temporal buffers | 32-lane programs run per half wave; NaN/Inf filtered on colour outputs |
| Missing or late textures | texture upload queue fixed at 192 MB / 250 ms per frame | configurable, larger by default (`VICTORY_TEXTURE_QUEUE_MB`, `VICTORY_TEXTURE_QUEUE_MS`) |
| Characters missing or broken, faces absent | two meshlet-cull compute shaders hung on AMD and had to be skipped | upstream VIctory #334 (buffer-state tracking) ported; `fc5e66f8f873d3bb` no longer skipped: Lucia's face, hair and outfit render |
| Compute results not seen by other workgroups | `glc` loads not globally coherent on RDNA | upstream VIctory #1271 ported |
| Lost or misplaced asset loads | DirectStorage page lists read after the title changed them | read at the title's submit (analysis by JappertjeV, [#3](https://github.com/PastiiJay/klbf-lab-beta/issues/3)); `VICTORY_PAGE_LIST=enqueue|submit|late` to compare |
| Cell walls, window frame and posters missing (sky where the wall should be) | pipelines skipped while the world loads, textures streamed in part taken for others | ported from [myokex/victory-amd](https://github.com/myokex/victory-amd): pipelines kept across runs and waited for while a world loads (`VICTORY_PIPELINE_GATE_S`), textures shown from their first loaded mip, lost placed views refreshed (`VICTORY_TEXTURE_SWEEP`), dispatches over 65,535 groups split |
| Walls, window frame and outfit wrong for a whole run, at random | during loading the list of remapped texture ranges overflowed and was thrown away, so which textures got re-checked depended on timing | the list is 32× larger and an overflow triggers a full re-check instead of a drop (found by comparing logs of runs with and without walls) |
| The AMD shader compiler crashes (`amdxc64.dll`) on a few pipelines | driver bug on two pipelines | `victory translate --cache --pipelines` pre-builds every pipeline offline, saves as it goes, finds the crashing ones and skips them in game too |

## What you can expect (tested on an RX 9070 XT, Adrenalin 32.0.32029.2010)

| | Result |
|---|---|
| First cell | walls, window frame, posters and photos drawn; Lucia's face, hair and orange outfit render; inmates in the yard |
| Speed, recommended settings (720p upscaled to 1080p with AMD FSR) | **~7.3 fps (median), 74 min with no device removal**, walls drawn throughout |
| Speed, native resolution without FSR | ~4.8–5.2 fps (≈200 ms/frame); 41 min with no device removal (Lab 33) |
| Skipped shaders | only one left (`39f0e9aeb156a61c`, which never leaves the AMD compiler); the other 47 we used to skip now run on this card |
| Cell walls | drawn in 5 of 6 runs (about half before Lab 35). When they are missing, the window frame turns purple and the outfit dark for the whole run; still under investigation |
| Still wrong | a purple tint on some papers and photos, stretched "web" triangles around some characters that change every frame, some textiles look wet, colour banding in skies |

These are a few runs on one machine: other cards and drivers may behave differently.

## Run

Build like VIctory (`cargo build --release`), then pre-build the pipelines once (about 10 minutes, rerun it until it ends without a crash):

```powershell
$env:VICTORY_SHADER_OPT = '0'
$env:VICTORY_SKIP_PIPELINES = (Get-Content docs\klbf\skip-amd.txt -Raw).Trim()
target\release\victory.exe translate --cache --pipelines --jobs 8 <game dir>\shaders.rpf
```

Then play with:

```powershell
$env:VICTORY_SHADER_OPT = '0'
$env:VICTORY_SKIP_PIPELINES = (Get-Content docs\klbf\skip-amd.txt -Raw).Trim()
$env:VICTORY_LATE_WAIT = '1'
$env:VICTORY_WIDE_BACK = '1'
$env:VICTORY_PIPELINE_WAIT_MS = '24'
$env:VICTORY_RELAY_COPY_QUEUE = '0'
$env:VICTORY_FFX_DIR = '<FidelityFX SDK>\Kits\FidelityFX\signedbin'
target\release\victory.exe run --console series-s <game dir>\<the title's exe> --execute
```

`--console series-s` makes the title render at 1280×720, and AMD FSR (from the official [FidelityFX SDK](https://github.com/GPUOpen-LibrariesAndSDKs/FidelityFX-SDK)) upscales it to 1920×1080: that is the ~7 fps setting. Without `--console series-s` the title renders at its native resolution (~5 fps here).

> [!TIP]
> With the recommended settings the start screen and the main menu stay **black**: the title is running behind it. Press **A** on the controller (or **Enter** on the keyboard, with the game window focused) to get past them; the picture appears once the world loads. Plug the controller in **before** starting: plugging it in during play pauses the title.

`VICTORY_SHADER_OPT=0` turns off the fork's shader clean-up passes, which crashed the AMD compiler for us. `VICTORY_TEXTURE_BUDGET_MB=6144` fixed some dark textiles for another tester but hid the cell walls in both our runs with it, so we leave it off for now. 

Please report results in an [issue](https://github.com/PastiiJay/klbf-lab-beta/issues): GPU, driver, how long it ran, fps in the window title, and what looks wrong. Patch notes: [CHANGELOG.md](CHANGELOG.md). Full run log: [docs/klbf/results.md](docs/klbf/results.md).

Product names are only used to say what this works with; they belong to their owners. KLBF Lab is not affiliated with them. License: GPL-3.0.
