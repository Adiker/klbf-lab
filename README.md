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

**Not playable.** The progress below comes from the VIctory community's open pull requests: they are not merged
yet, and once they are, official VIctory will do the same. We build them together, test them on an AMD card and
report the numbers back.

What VIctory `main` does on our card, and what it does with the open pull requests listed under
[What's inside](#whats-inside):

| Stage | VIctory `main` | `main` + the open pull requests below |
|---|---|---|
| Boot, first-boot screens, intro video, start screen | 30 fps | 30 fps |
| Loading into the world (~50 s) | works | works |
| The world (opening scene) | reached; GPU timeout after 3–4 s | plays through with audio and subtitles, ~1 fps |
| Gameplay | not reached | reached and controllable with a pad (input, rumble, pause menu); 1,006 s with no device removal, stopped by us |
| A picture of the world | dark | still dark or blank |
| Speed in the world | – | ~1 fps; GPU ~10 % busy, host-side copies are the bottleneck |

Tested on one machine: Windows 11, AMD Radeon RX 9070 XT (RDNA4), Ryzen 7 9800X3D, 32 GB.

## What's inside

KLBF Lab is a fork of [VIctory](https://github.com/Marvisak/VIctory). The `klbf-lab` branch is VIctory `main`
plus the following.

### From the VIctory community (open pull requests, merged as they stood when we tested them)

| Pull request | Author | What it does | What we measured on AMD |
|---|---|---|---|
| [#452](https://github.com/Marvisak/VIctory/pull/452) | AntoninMichelq | shader spin-wait / loop limits in release builds | ends the 2 s GPU timeout when entering the world |
| [#431](https://github.com/Marvisak/VIctory/pull/431) | AntoninMichelq | frees host textures only after running submissions | removes the "inside freed" page faults |
| [#67](https://github.com/Marvisak/VIctory/pull/67) | alessiodeia | CopyTextureRegion texture-to-buffer readbacks | part of the same stack |
| [#584](https://github.com/Marvisak/VIctory/pull/584) | FibbS6 | clamps descriptor heap indices | removes the read far past the end of the view heap |
| [#493](https://github.com/Marvisak/VIctory/pull/493) | hophaver | binds root SRVs as bounded one-view tables | with #584, removes the next page fault (1,006 s, no removal) |

Tested and not kept on our card: [#688](https://github.com/Marvisak/VIctory/pull/688), [#641](https://github.com/Marvisak/VIctory/pull/641) (brings the #493 fault back), [#955](https://github.com/Marvisak/VIctory/pull/955) (same result as #584 here). XCL and Palmwave are tested too, see [docs/klbf/xcl-palmwave.md](docs/klbf/xcl-palmwave.md).

### Our own small changes

| Change | Why |
|---|---|
| #584's index limit raised to 1,507,328 | the view heap on our AMD card is 1,245,184 + 2^18 dynamic slots, above #584's 1,000,000 |
| `VICTORY_KEYS` also works with a pad connected (same idea as [#197](https://github.com/Marvisak/VIctory/pull/197)) | scripted test runs |
| Window caption reads "KLBF Lab (VIctory)" | no confusion with official builds |

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
