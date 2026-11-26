# Add the KLBF Lab Bench (BM-v1) to your build

> **For projects derived from VIctory only**: the same layer family (Neptune, avatarmanz and
> cool_fox, fxceless forks, and their own forks). The module calls into that layer's own code and
> files, so other emulators or layers can't drop it in as is. They can still measure the same run
> with the uncertified fallback: `python -I tools/fps-session.py <log> --bench bm-v1` (on `main`,
> see [BENCH-BM-V1.md](https://github.com/PastiiJay/klbf-lab/blob/main/docs/klbf/BENCH-BM-V1.md)).

The bench measures 5:00 from the first world frame with the input locked, then shows a card and
saves it (PNG, JSON, text). With it in your build, your players' results can be compared with
everyone else's, and your build's name (`owner/repo @ commit`) is written on each card.

Everything stays off unless `KLBF_BENCH=bm-v1` is set: without it the hooks below return at once.

## 1. Files to copy

From this branch (`beta-2`), into `crates/victory-gpu/`:

| File | What it is |
|---|---|
| `src/klbf_bench.rs` | The whole module: timing, verdict, results, card, window, timer. |
| `src/klbf_card.png` | The card template (our own drawing, no game content). `include_bytes!` picks it up. |
| `src/pixels.rs` | Neptune's pixel helpers (bitmap, PNG filters, short GPU/CPU names). Skip if your tree has it. |
| `build.rs`, the block after `(ours) KLBF Lab Bench card` | Sets `KLBF_PROJECT`, `KLBF_PROJECT_SOURCE` and `KLBF_SHA` (the card's "from:" line) from git. It needs the `owner_repo` function above it and the `git` and `env` closures. |

Optional: `tools/klbf-card-template.py` (redraws the template).

Then in `src/lib.rs`:

```rust
#[cfg(windows)]
pub mod klbf_bench;
mod pixels; // if you copied it
```

`windows-sys` features used by the module: `Win32_Foundation`, `Win32_Graphics_Gdi`,
`Win32_System_LibraryLoader`, `Win32_System_Registry`, `Win32_System_SystemInformation`,
`Win32_System_Threading`, `Win32_UI_WindowsAndMessaging`, `Win32_UI_Input_KeyboardAndMouse`,
`Win32_UI_Input_XboxController`. From `windows`: `Win32_Graphics_Dxgi` (for `IDXGIAdapter3`).

### The one block to adapt

Everything the module reads from the rest of the layer is in one section of `klbf_bench.rs`,
**"The tree"**, right after the statics: `counters`, `profile`, `tree_settings`, `ram_bytes`,
`device_removed`, `low_pct_fps`, `outside_repo`, `encode_png`. Point each one at your tree's
function. If your tree doesn't have one of the figures, return 0 (or `false`): it only goes in
the JSON and the card's small print, not in the verdict figures.

| Function | In our tree | If your tree doesn't have it |
|---|---|---|
| `counters` | `shader_cache::counts`, `pipeline::pipeline_counts`, `draw::drawn`, `draw::attempted` | `[0; 4]` |
| `profile` | `console::current()` | same in every VIctory tree |
| `tree_settings` | `resource::texture_max_dim`, `pipeline::skipped_count`, `pipeline::denied_count` | `[0; 3]` |
| `ram_bytes` | `host::bench_process_memory` (PR #78) | `K32GetProcessMemoryInfo`, `WorkingSetSize` |
| `device_removed` | `bench::is_device_removed` (PR #78) | `descriptor::host::device_removed().is_some()` |
| `low_pct_fps` | `bench::low_pct_fps` (PR #78) | copy it from our `bench.rs` (10 lines) |
| `outside_repo` | `bench::ensure_outside_repo` (PR #78) | `Ok(())` (it only refuses a results folder inside a source checkout) |
| `encode_png` | `screenshot::encode_png` | copy it from our `screenshot.rs` (uses `pixels`) |

## 2. The hooks

Four places, plus one recommended. Names are the same in most VIctory-derived trees; where they
differ, the table says so.

| # | Call | Our tree (KLBF Lab) | Same spot in avatarmanz / cool_fox / fxceless forks |
|---|---|---|---|
| 1 | `crate::klbf_bench::start(hwnd, self.adapter.clone())` | `host.rs`, `Host::presenter`, right after `CreateSwapChainForHwnd` | Same: `Host::presenter` in `host.rs` |
| 2 | `crate::klbf_bench::on_present(black, world_frame)` | `bench.rs`, `bench::on_present` (called from `queue.rs`, `present_now`) | `queue.rs`: after `host.present(...)` in `extern "system" fn present` (avatarmanz, cool_fox) or `present_now` (fxceless) |
| 3 | `if victory_gpu::klbf_bench::input_locked() { ... }` | `victory-hle`, `modules/gameinput.rs`, `impl Source for Host`: `fn pad` (return `Some(PadState::default())` after a successful `XInputGetState`), `fn keys` (return `Vec::new()`), and `mouse()` (return `Mouse::default()`) | Same `impl Source for Host`, `fn pad` and `fn keys`; those trees have no `mouse()` |
| 4 | `victory_gpu::klbf_bench::window_closed()` and `victory_gpu::klbf_bench::on_exit(\|\| end_title("bench finished", Box::new(\|\| {})))` | `modules/lifecycle.rs`: `window_closed()` in `window_proc` on `SC_CLOSE`, before `end_title`; `on_exit(...)` at the end of `hook` | Same: `window_proc`, `hook`, `end_title` in `lifecycle.rs` |
| 5 (recommended) | `if !crate::klbf_bench::holds_title() { ... }` around the FPS caption | `host.rs`, `Meter::frame`, around the line that hands the new caption to the caption thread | Same: `Meter::frame` in `host.rs`, around its `SetWindowTextW` |

Notes:

- **Hook 2, the world frame.** `world_frame` is 0 on menus and loading screens, 1 on the first
  presented frame with 500 draws or more, then +1 on every present (PR #78 by Vladimir-Human). If
  your tree doesn't have it, this is the whole counter, once per present, with the tree's running
  draw count:

  ```rust
  static LAST_DRAWN: AtomicU64 = AtomicU64::new(0);
  static WORLD_FRAME: AtomicU64 = AtomicU64::new(0);
  let prev = LAST_DRAWN.swap(drawn, Ordering::Relaxed);
  let wf = match WORLD_FRAME.load(Ordering::Relaxed) {
      0 if drawn.saturating_sub(prev) >= 500 => { WORLD_FRAME.store(1, Ordering::Relaxed); 1 }
      0 => 0,
      _ => WORLD_FRAME.fetch_add(1, Ordering::Relaxed) + 1,
  };
  crate::klbf_bench::on_present(black, wf);
  ```

  `black` is the present's black-frame flag (`shown.unwrap_or(false)`, as `blinks` uses it in
  `queue.rs`); `false` if you don't have one. `on_present` is `pub(crate)`: call it from inside
  `victory-gpu`.
- **Hook 4** is what ends the run cleanly. Without `on_exit`, the card's close calls
  `std::process::exit(0)` (your exit path's own saving is skipped); without `window_closed`, a
  run closed early writes no PARTIAL result.
- **Hook 5** keeps your FPS caption from overwriting the bench's title ("KLBF Lab · Bench 2:13 /
  5:00") and keeps figures off the screen during the run. Without it the title flickers between
  the two.
- **An FPS overlay of your own:** don't start it when `crate::klbf_bench::active()` (ours:
  `overlay.rs`, `start`). Nothing but the frame times may cost time during the run.

During the run the module shows only the time, in the game window's title and in a small label at
the window's top-left corner (placed from the window's own rectangle, once a second).

## 3. Environment variables

At run time:

| Variable | Effect |
|---|---|
| `KLBF_BENCH=bm-v1` | Turns the bench on. Nothing changes without it. |
| `KLBF_BENCH_PLAYER=<GitHub login>` | The player name on the card (otherwise "anonymous"). |
| `KLBF_BENCH_DIR=<folder>` | Where results go (default: `bench-results` next to the exe). |
| `VICTORY_FSR_DLL` | Read only, to write "FSR" or "none" in the settings. |

At build time (`build.rs`), when the build has no git checkout:

| Variable | Effect |
|---|---|
| `KLBF_PROJECT_NAME=<owner/repo>` | The project on the card, marked "(declared)". |
| `KLBF_GIT_SHA`, `KLBF_GIT_REMOTE` | The commit and origin, for a build from `git archive`. |

Tests only: `KLBF_CARD_PREVIEW=<file.png>` with the ignored card preview test draws a sample card.

## 4. What to credit

In your README or credits, and in the commit that adds it:

- **KLBF Lab Bench BM-v1** by PastiiJay, from [PastiiJay/klbf-lab](https://github.com/PastiiJay/klbf-lab)
  (`crates/victory-gpu/src/klbf_bench.rs`, the card template), GPL-3.0-or-later like the layer.
- **World frames** (`bench::world_frame`): PR #78 by Vladimir-Human.
- **The card's window and pixel helpers** (`pixels.rs`, the layered-window way of showing it): Neptune
  by Traffic & zm0kiemedia.

Please keep the card as it is (template, layout, verdict rules): that is what makes a result from
your build comparable with everyone else's. Your project's name on the card comes from your own
git origin.

## Projects that include the bench

Credit goes both ways: a project that adds the bench is listed here, with a link. Open an issue or
a pull request on [PastiiJay/klbf-lab](https://github.com/PastiiJay/klbf-lab) with your repo and
the commit that adds it.

| Project | Since |
|---|---|
| [KLBF Lab](https://github.com/PastiiJay/klbf-lab) | Lab 63 |
