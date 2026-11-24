<h1 align="center">
  <img src="docs/klbf/logo.svg" alt="KLBF Lab" width="160">
  <br>
  KLBF Lab
</h1>

<h4 align="center">An open lab that combines the best fixes from every Xbox-to-PC compatibility project into one tested build.</h4>

<p align="center">
  <a href="https://github.com/Marvisak/VIctory"><img src="https://img.shields.io/badge/based%20on-VIctory-1f46c8" alt="based on VIctory"></a>
  <img src="https://img.shields.io/badge/tested%20on-AMD%20RX%209070%20XT-c04fb0" alt="tested on RX 9070 XT">
  <img src="https://img.shields.io/badge/record-17%20min%20without%20a%20crash-ffb000" alt="record">
  <img src="https://img.shields.io/badge/license-GPL--3.0-2ea44f" alt="GPL-3.0">
</p>

<p align="center">
  <a href="#why">Why</a> •
  <a href="#status">Status</a> •
  <a href="#whats-inside">What's inside</a> •
  <a href="#build-and-run">Build and run</a> •
  <a href="#results">Results</a> •
  <a href="#testers-wanted">Testers wanted</a> •
  <a href="#rules">Rules</a> •
  <a href="#credits">Credits</a>
</p>

> [!IMPORTANT]
> This repository contains **no game files, keys, shaders or executables from the game**, and does not explain how to
> get them. You need your own legally obtained copy, already readable on disk. Nothing here decrypts or works around
> any protection. Everything a run creates stays on your PC: never share it.

## Why

Several open-source teams are working out, in public, how a modern console game can run natively on a PC: how its
graphics commands, shaders, memory and input get translated from one platform to another. It's fascinating to
watch, and with this many people following it, now is the time to learn how these systems really work.

**KLBF Lab is an educational project.** We read the code, build it, test it on real hardware and write down what we
learn. Every project solves different problems. So we **pick the fixes that really move things forward, wherever
they come from**, combine them in one build, measure it and credit the people who wrote them. We don't take sides:
our test numbers go back to every project.

## Status

**Not playable.** On our AMD card, KLBF Lab goes the furthest of every build we have tested so far.

| Stage | Official VIctory `main` | **KLBF Lab** |
|---|---|---|
| Boot, first-boot screens, intro video, start screen | ✅ 30 fps | ✅ 30 fps |
| Loading into the world (~50 s) | ✅ | ✅ |
| The world (opening scene) | ⚠️ reached, removed after 3–4 s (GPU timeout) | ✅ plays through with audio and subtitles, ~1 fps |
| Gameplay | ❌ | ✅ **reached and controllable with a pad** (input, rumble, pause menu); run stopped by us after **1,006 s with no device removal** |
| A picture of the world | ❌ dark | ❌ still dark or blank |
| Where it stops | GPU timeout (TDR) | not seen yet in 1,006 s |
| Speed | – | menus 10–93 fps; the world ~1 fps (GPU ~10 % busy: the host-side copies are the bottleneck) |

Tested on one machine: Windows 11, **AMD Radeon RX 9070 XT** (RDNA4), Ryzen 7 9800X3D, 32 GB.

## What's inside

KLBF Lab is a fork of [VIctory](https://github.com/Marvisak/VIctory). The `klbf-lab` branch is official VIctory
plus these open pull requests, merged as they stood when we tested them:

| From | Fix | Author's PR | Effect on our card |
|---|---|---|---|
| VIctory | Shader spin-wait / loop limits in release builds | [#452](https://github.com/Marvisak/VIctory/pull/452) | ends the 2 s GPU timeout when entering the world |
| VIctory | Free host textures only after running submissions | [#431](https://github.com/Marvisak/VIctory/pull/431) | removes the "inside freed" page faults |
| VIctory | CopyTextureRegion texture-to-buffer readbacks | [#67](https://github.com/Marvisak/VIctory/pull/67) | part of the stack above |
| VIctory | Clamp `ResourceDescriptorHeap` / `SamplerDescriptorHeap` indices | [#584](https://github.com/Marvisak/VIctory/pull/584) (limit raised to our 1,507,328-slot view heap) | removes the read far past the end of the view heap (`slot 125829120`) |
| VIctory | Bind root SRVs as one-view tables bounded to their host copy | [#493](https://github.com/Marvisak/VIctory/pull/493) | removes the following low-address page fault; with #584: **483 s, no crash** |
| KLBF Lab | `VICTORY_KEYS` also works with a pad connected | ours (same idea as [#197](https://github.com/Marvisak/VIctory/pull/197)) | scripted test runs |
| KLBF Lab | Window caption reads "KLBF Lab (VIctory)" | ours | no confusion with official builds |

Tested and **not** kept (no gain on our card): [#688](https://github.com/Marvisak/VIctory/pull/688). [#493](https://github.com/Marvisak/VIctory/pull/493) alone did nothing; it only helps together with #584. XCL and Palmwave are tested too, see
[docs/klbf/xcl-palmwave.md](docs/klbf/xcl-palmwave.md).

## Build and run

Same requirements as VIctory: Windows 10/11 x64, an AVX2 CPU, a Direct3D 12 GPU with shader model 6.6 and mesh
shaders, Rust. See [README.victory.md](README.victory.md) for the full setup (`victory.toml`, paths, controls).

```powershell
git clone -b klbf-lab https://github.com/PastiiJay/klbf-lab
cd klbf-lab
copy victory.example.toml victory.toml        # then set your paths (outside the repo)
cargo build --release -p victory --features diagnostics
$env:VICTORY_D3D12_DRED = '1'                 # clearly more stable on our card
target\release\victory.exe run <game dir>\<the title's exe> --execute
```

Tips from our runs:
- **Stay windowed.** Alt+Enter (fullscreen) freezes the picture in the world.
- `docs/klbf/run-test.ps1` runs a timed test and logs the caption (fps, draws per frame) every 15 s.
- When the GPU is removed, Windows resets the display driver: the screen and mouse freeze for a moment. That's expected.

## Results

Every run we made, with build and result: **[docs/klbf/results.md](docs/klbf/results.md)**.
The same numbers are posted to the projects' own threads ([VIctory #59](https://github.com/Marvisak/VIctory/issues/59),
[XCL #560](https://github.com/ivall/xcl/issues/560), [Palmwave #2](https://github.com/fablinoo/palmwave/issues/2)).

## Testers wanted

We're looking for **testers**, not chatters. Any GPU: AMD, NVIDIA or Intel.

1. Build the `klbf-lab` branch from source, with your own copy of the game.
2. Run it with `docs/klbf/run-test.ps1`.
3. [Open an issue](https://github.com/PastiiJay/klbf-lab/issues/new) with your GPU, driver, build commit, how many seconds it ran and the last error lines of the log. Text only.

> [!NOTE]
> **We have no game files and will never share any. Please don't ask.**
> **There is no Discord.** Everything happens here on GitHub, in issues and pull requests. Any server claiming to be KLBF Lab is not us.

## Rules

- **No game content.** No game files, extracted shaders, saves, keys, screenshots or videos in this repository, in issues or in pull requests.
- **No ready-made binaries.** Build it yourself from source.
- **Credit first.** Every fix keeps its author and links the original pull request.
- **Facts, not hype.** A claim comes with a build, a GPU and a log line.

## Credits

All the real work belongs to the authors of [VIctory](https://github.com/Marvisak/VIctory) and of the pull requests
listed above, and to the [XCL](https://github.com/ivall/xcl) and [Palmwave](https://github.com/fablinoo/palmwave)
teams. KLBF Lab only selects, combines and measures.

## License

[GPL-3.0](LICENSE), the license of VIctory. Original VIctory README: [README.victory.md](README.victory.md).
