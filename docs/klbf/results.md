# Test log

One machine: **AMD Radeon RX 9070 XT 16 GB** (RDNA4, Adrenalin 32.0.32029.2010) · Ryzen 7 9800X3D · 32 GB DDR5 · Windows 11 (26200).
Text only, no screenshots. Times are seconds from launch; the world starts at about 60 s.

| Date (UTC) | Project | Build | Result |
|---|---|---|---|
| 2026-11-24 13:30 | **KLBF Lab 03** | same, no scripted keys, XInput pad | **1,006 s, stopped by us, no device removal**; pad input and rumble work, mission objectives advance; world still black at ~1 fps (6,500 draws/frame), menus 10–93 fps; 16.5 GB working set, GPU ~10 % busy |
| 2026-11-24 13:14 | **KLBF Lab 03** | **+ #584 + #493** | **483 s, stopped by us, no device removal; gameplay reached (control prompts)** |
| 2026-11-24 13:11 | KLBF Lab 02 | + #584 | 160 s, device removed: page fault at a low address (`0x29f4000`) in a compute dispatch |
| 2026-11-24 12:54 | KLBF Lab | + #493 (bounded root SRVs) | 147 s, device removed: read far past the end of the view heap (`0x1f00f0000`) |
| 2026-11-24 12:43 | Palmwave | `5a54236` | stops at 6 s, `0x887a0020` (×2, also with `XCL_PSO_DISK_CACHE=0`) |
| 2026-11-24 12:38 | KLBF Lab | + #688 (dynamic slots on a capped heap) | 144 s, device removed, page fault |
| 2026-11-24 11:19 | **KLBF Lab** | **`klbf-lab` branch, `VICTORY_D3D12_DRED=1`** | **221 s: ~160 s in the world, audio and subtitles, ~1 fps; then device removed + page fault** |
| 2026-11-24 11:16 | KLBF Lab | same, without DRED | 87 s, device hung |
| 2026-11-24 11:12 | Palmwave | `b739d34` | stops at 6 s, `0x887a0020` (×2) |
| 2026-11-24 10:30 | KLBF Lab | `klbf-lab` branch | 160 s, ~100 s in the world |
| 2026-11-24 09:16 | Palmwave | `ecb988c` | ~105 s, then `0x887a0020` |
| 2026-11-24 | VIctory | `main` | world at ~60 s, device removed 3–4 s later (clean DRED breadcrumbs: a timeout) |
| 2026-11-24 | XCL | `main` | stops ~100 s on the hang detector (`+0x23cf683`), 30–38 GB committed |

Notes:
- `VICTORY_KEYS` makes the keyboard stand-in pad the signed-in user's pad: a real pad then only reaches the pause button. Leave it unset to play with a pad.
- Alt+Enter (fullscreen) freezes the picture in the world: stay windowed.
- `VICTORY_D3D12_DRED=1` made runs clearly more stable on this card.
