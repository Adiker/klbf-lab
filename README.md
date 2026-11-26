<p align="center"><img src="docs/klbf/logo.svg" width="120" alt="KLBF Lab"></p>
<h1 align="center">KLBF Lab — test build (26 Nov 2026)</h1>
<p align="center">
  <img src="https://img.shields.io/badge/tested%20on-RX%209070%20XT-555" alt="tested on RX 9070 XT">
  <img src="https://img.shields.io/badge/stage-experimental-ffb000" alt="experimental">
</p>

KLBF Lab is a test build of a compatibility layer that runs an Xbox Series title natively on Windows from files you supply. It gathers the best fixes we could measure, aimed at **AMD Radeon (RDNA, 64-lane) cards**. This build is based on Neptune (Traffic & zm0kiemedia) plus contributors' fixes credited below, and our pipeline pre-build that survives AMD driver crashes.

**No game files are included.** You need your own legally obtained copy. New to this? Follow the [beginner's guide](docs/GUIDE.md).

## Speed

Measured during a real play session (controller), RX 9070 XT 16 GB, Ryzen 7 9800X3D, 32 GB RAM, Series S profile + FSR 4, the settings of [`play.ps1`](play.ps1):

| Situation | fps |
|---|---|
| Standing still, looking at the sky | 20–23 |
| Standing still in traffic | 15–17 |
| On foot in the open world | up to 14 (varies with the area) |
| Driving fast (the world streams in) | 9–12, short dips while new areas load |

Occasional short freezes in any situation (on foot or driving); they do not crash the game and it stays playable.

Route: start at the male lead's house right after first arriving there (~3% progress), then a lap of his neighbourhood. One machine only: other cards and drivers may behave differently. Full log: [docs/klbf/results.md](docs/klbf/results.md).

Known issues:
- Occasional freezes when the card or PC memory fills (try `-LowMemory`).
- Some shadows flicker near trees.
- Mirrors stay black (they need ray tracing).
- Car windows (glass) are not drawn: you can break into a car but the glass is invisible.
- Resolution is Series S, upscaled.

## Build and run

Needs Git, [rustup](https://rustup.rs), Visual Studio Build Tools (C++ workload) and AMD's [FidelityFX SDK](https://github.com/GPUOpen-LibrariesAndSDKs/FidelityFX-SDK) 2.4 unzipped to `C:\FidelityFX-SDK`.

```powershell
git clone -b beta-2 https://github.com/PastiiJay/klbf-lab
cd klbf-lab
cargo build --release
powershell -ExecutionPolicy Bypass -File .\play.ps1 -GameDir C:\Games\Title -Prebuild   # once per build, about 10-20 min; resumes by itself after a driver crash
powershell -ExecutionPolicy Bypass -File .\play.ps1 -GameDir C:\Games\Title   # play
```

`-SeriesX` plays in Series X mode (no FSR needed, slower). `-LowMemory` caps textures at 512 px: fewer freezes when memory is full, softer textures. `-FfxDir` points at another FSR folder. Plug the controller in before starting.

## Settings

`play.ps1` sets these (the pre-build and the game must use the same ones: the shader cache depends on them):

- Our pre-build and skip list: `VICTORY_SKIP_PIPELINES` = [docs/klbf/skip-amd.txt](docs/klbf/skip-amd.txt); pipelines the driver crashed on are skipped from `prebuild-crashed.txt`.
- New in this build: `VICTORY_CLAMP_AFTER_WRITER=1` (zm0kiemedia), `VICTORY_PORT_CONSTANTS=1` and `VICTORY_PORT_DESCRIPTORS=1` (avatarmanz's renderer port), `VICTORY_DYNAMIC_SLOTS=786432` (more descriptor slots: no more draws dropped, fixes flicker), `VICTORY_INDIRECT_RAW=0` and `VICTORY_STAGE_POOL_MB=2048` (WillyboPeep).
- `-LowMemory`: `VICTORY_TEXTURE_MAX_DIM=512` (Evan-Lowry), off by default.
- Series S: `--console series-s` and `VICTORY_FSR_DLL=<FidelityFX SDK>\Kits\FidelityFX\signedbin\amd_fidelityfx_upscaler_dx12.dll`.
- Neptune's set: `VICTORY_CARD_WINDOWS_MB=4096`, `BAKE_TEXTURES_MS=10000`, `EARLY_TEXTURES_MS=40`, `WAVE_OWN_LDS_GROUPS=64,128`, `WIDE_MERGE=1`, `RELAY_OWN_QUEUE=1`, `UNDER_WRITES_WORDS=1`, `UNDER_WRITES_RUNS=100000`, `UNDER_WRITES_MASKS=1`, `UNDER_WRITES_MASKS_LEAST=1`, `RELAY=2`, `WIDE_REFRESH=1`, `ASK_ONCE=1`, `TEXTURE_NO_WAIT=1`, `CARD_REHASH_RUNS=1`, `JOIN_COPIES=1`, `D3D12_BACKGROUND=0`, `LATE_WAIT_LISTS=1024`, `WINDOW_TAILS=1`, `TEXTURE_STAGE_MB=512`, `CARD_BUFFERS_MIN_KB=64`, `ASK_QUIET=8`, `COPY_CHANGED=1`, `QUIET_BACK=1`, `LIST_POOL_MOST=2048`, `LIST_POOL_MB=2048`, `WIDE_THREADS=12`, `TEXTURE_HASH_EVERY=32`, `LEVELS_ON_DEMAND=1`, `WINDOW_KB=1024`, `CARD_BUFFERS_MB=1536`, `CARD_WINDOW_UPLOAD=1`, `DROP_DXIL=1`, `DESC_DATA=1`, `VRAM_IDLE_MS=15000,2500,1000`, `PIPELINE_WAIT_MS=2500`, `OCEAN_READBACK=1`, `WATCH_4K=1`, `THIN=1`, `OVERLAY=0` (all with the `VICTORY_` prefix).

Please report results in an [issue](https://github.com/PastiiJay/klbf-lab/issues): GPU, driver, how long it ran, fps, what looks wrong. Text only, no game screenshots. Patch notes: [CHANGELOG.md](CHANGELOG.md).

Product names are only used to say what this works with; they belong to their owners. KLBF Lab is not affiliated with them. License: GPL-3.0 ([LICENSE](LICENSE)).

## Credits

Every commit keeps its author. Thank you:

- [@Marvisak](https://github.com/Marvisak) for [VIctory](https://github.com/Marvisak/VIctory), the base of everything here, and [@fxceless](https://github.com/fxceless) for [victory-fork](https://github.com/fxceless/victory-fork).
- Traffic and [@zm0kiemedia](https://github.com/zm0kiemedia) for Neptune, the base of this build, and the indirect-argument clamps.
- [@avatarmanz](https://github.com/avatarmanz) ([VIctory-7900XTX](https://github.com/avatarmanz/VIctory-7900XTX)): renderer port 1 and 2.
- [@Evan-Lowry](https://github.com/Evan-Lowry): the texture size cap (`-LowMemory`).
- [@WillyboPeep](https://github.com/WillyboPeep) ([neptune-ve](https://github.com/WillyboPeep/neptune-ve)): loading-screen pipelines, section views, profiler and settings.
- [@proneonn](https://github.com/proneonn) (Neon, [Vertex](https://github.com/proneonn/Vertex)) and [@tippythetaidum](https://github.com/tippythetaidum): face fixes.
- [@GamingRipperDoc](https://github.com/GamingRipperDoc) (fxceless/victory-fork#1216, analysis by [@IxMxAMAR](https://github.com/IxMxAMAR)): device-loss fix.
- [@IxMxAMAR](https://github.com/IxMxAMAR) and [@MalfoyDraco99](https://github.com/MalfoyDraco99) (fxceless/victory-fork#1213): AMD compiler crash fix.
- Carried in Neptune's base: [@myokex](https://github.com/myokex) ([victory-amd](https://github.com/myokex/victory-amd)), JoshuaO22, Spexivus, joroyt and tightfall.
- KLBF Lab ([@PastiiJay](https://github.com/PastiiJay)): the crash-surviving pipeline pre-build, the skip list, KLBF Lab names, tests and docs.
