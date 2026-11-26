# KLBF Lab: beginner's guide (Windows)

Every step below is a command to copy and paste, in order. You only need your own copy of the title's Xbox Series files in a folder. KLBF Lab includes no game files.

In this guide the game files are in **`C:\Games\Title`** (the folder that holds the title's `.exe` and `shaders.rpf`). If yours are elsewhere, replace that path everywhere.

Open **PowerShell** (Start menu → type `PowerShell` → Enter) and paste each block. Wait for one block to finish before the next.

**First run in 3 steps** (once the tools are built, steps 1–5):
1. Tell `play.ps1` where the game is: `-GameDir <folder>` (see [Common questions](#common-questions)).
2. Run `.\play.ps1 -GameDir <folder> -Prebuild` once. Wait for `Pre-build done`.
3. Run `.\play.ps1 -GameDir <folder>` to play.

---

## 1. Check your PC (1 minute)

- A recent graphics card with DirectX 12 (tested on AMD Radeon RX 9070 XT only).
- **More than 8 GB of video memory** recommended.
- **32 GB of RAM**, or 16 GB plus a large page file (step 2).
- About 15 GB of free disk space for the tools and the shader cache.

## 2. Page file (only if you have 16 GB of RAM)

```powershell
SystemPropertiesPerformance.exe
```

Then: **Advanced** tab → **Virtual memory: Change…** → tick **Automatically manage paging file size for all drives** (or untick it, pick your fastest drive, **Custom size**, Initial `32768`, Maximum `49152`) → **Set** → **OK** → restart the PC.

## 3. Install the tools (10–20 minutes, once)

```powershell
winget install --id Git.Git -e --source winget
winget install --id Rustlang.Rustup -e --source winget
winget install --id Microsoft.VisualStudio.2022.BuildTools -e --source winget --override "--quiet --wait --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"
```

**Close PowerShell and open a new one** so the new tools are found.

## 4. Download and build KLBF Lab (5–15 minutes)

```powershell
cd $HOME
git clone -b beta-2 https://github.com/PastiiJay/klbf-lab
cd klbf-lab
cargo build --release
```

## 5. Get AMD's FidelityFX SDK (for Series S mode)

Download **FidelityFX SDK v2.4.0** from AMD's official page: https://github.com/GPUOpen-LibrariesAndSDKs/FidelityFX-SDK/releases. Unzip it to **`C:\FidelityFX-SDK`**. Check that this file exists: `C:\FidelityFX-SDK\Kits\FidelityFX\signedbin\amd_fidelityfx_upscaler_dx12.dll`.

## 6. Pre-build the shaders (10–20 minutes, once per build)

```powershell
cd $HOME\klbf-lab
powershell -ExecutionPolicy Bypass -File .\play.ps1 -GameDir C:\Games\Title -Prebuild
```

If the graphics driver crashes, the script starts again by itself where it stopped and remembers what crashed. It's done when it prints `Pre-build done`.

## 7. Play

```powershell
cd $HOME\klbf-lab
powershell -ExecutionPolicy Bypass -File .\play.ps1 -GameDir C:\Games\Title
```

- **Plug in the controller before starting.** The account picker only answers the controller, not the keyboard ([#69](https://github.com/PastiiJay/klbf-lab/issues/69)).
- No FSR? Add `-SeriesX` (slower). Run step 6 again with `-SeriesX` too.
- The first minutes in a new area are slow while shaders finish loading.

## Updating later

```powershell
cd $HOME\klbf-lab
git pull
cargo build --release
```

Then step 6 again, and step 7.

## Something went wrong?

| What you see | What to do |
|---|---|
| `AMD FSR not found` | Step 5, or `-FfxDir <your signedbin folder>` |
| `Build first` | Step 4 |
| Crash about 3 seconds after start, black window | Not enough memory: step 2 (page file), close other programs |
| `X3506` or `vs_5_1` in the log, black window | Old Windows shader compiler: copy the x64 `d3dcompiler_47.dll` from a recent Windows SDK (`Redist\D3D\x64`) next to `target\release\victory.exe` |
| Crash while loading after `dstorage: request failed: zlib … hr=0x8007000d` | Some game files are incomplete or damaged: copy the game folder again from your source (thanks @Emaxoso) |

Still stuck? Open an [issue](https://github.com/PastiiJay/klbf-lab/issues) with your graphics card, driver version, Windows version and the last lines PowerShell printed. Text only, no game screenshots.

## Common questions

**Which folder is the game folder? Is my `victory.toml` okay?**
The game folder is the one that holds the game's main `.exe` and `shaders.rpf`. `play.ps1` takes the largest `.exe` in it (or the one you give with `-Exe`).
With `play.ps1`, pass it with `-GameDir <folder>`. Without `-GameDir`, `play.ps1` uses `C:\Games\Title`. It sets that folder itself, so `game_dir` in `victory.toml` is not used by `play.ps1`. `victory.toml` only matters when you run `victory.exe` yourself.
In `victory.toml`, `cache_dir` and `data_dir` can stay commented: the defaults (`%LOCALAPPDATA%\victory\cache` and `%LOCALAPPDATA%\victory\data`) are fine. Every path must be outside the `klbf-lab` folder: the tools refuse paths inside it.

**`--jobs 12` or `--jobs 8`? Do I need `SHADER_OPT=0` or `skip-amd.txt`?**
No manual commands are needed. Just run `.\play.ps1 -Prebuild` once per new version. It sets the jobs, the skip list and every setting itself.

**Do I need `-Prebuild` before every launch?**
No. Once per new version (after `git pull` and `cargo build --release`). Use the same options for `-Prebuild` and for play (for example `-SeriesX` or `-LowMemory` in both): the shader cache depends on them.

**`-Prebuild` keeps printing `Pass N ended with code -1073741819 (driver crash?): resuming...`**
That is normal. The graphics driver crashed on one shader. The next pass makes the suspects alone, finds the one that crashed and skips it from then on (listed in `prebuild-crashed.txt`). It resumes by itself, up to 120 passes. Let it finish.

**Every pass ends with code 3 (Linux / Proton).**
We don't know the cause yet. Open an [issue](https://github.com/PastiiJay/klbf-lab/issues) with the full console of one pass (see below).

**Does it run on an integrated GPU (Radeon 780M and similar)?**
Untested. It needs a lot of dedicated video memory (more than 8 GB recommended), so expect problems.

**I have an 8 GB card or 16 GB of RAM.**
Add `-LowMemory` (textures capped at 512 px instead of 1024) to both `-Prebuild` and play. With 16 GB of RAM, also set a page file of 32 GB or more (step 2).

**Where is the crash log? Where are the bench results?**
- Crash log: `%LOCALAPPDATA%\victory\data\<title ID>\crashes.log` (the 8-character folder in `%LOCALAPPDATA%\victory\data`). If you set `data_dir`, it is there instead.
- Bench results: the `bench-results` folder next to `victory.exe`, so `target\release\bench-results` (or the folder in `KLBF_BENCH_DIR`).

**How do I share the console?**
Add `*>&1 | Tee-Object run.log` at the end of the command:

```powershell
powershell -ExecutionPolicy Bypass -File .\play.ps1 -GameDir C:\Games\Title *>&1 | Tee-Object run.log
```

Then attach `run.log` to a GitHub [issue](https://github.com/PastiiJay/klbf-lab/issues).

---

Thanks to [@HishamMuhammed](https://github.com/HishamMuhammed), whose questions shaped this guide.
