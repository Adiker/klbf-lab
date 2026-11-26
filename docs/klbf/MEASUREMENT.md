# A shared way to measure frame rate

Every project reports frame rates from different places and in different ways: an empty sea, a menu, a loading screen, one lucky second. Those numbers cannot be compared. This page proposes one method, open to any project, so that we can all compare on equal footing.

## Where to start

- Play from a new game until you first arrive at the male lead's house (about 3 % progress), at the point where you can make your first save in his bed. Save there. Every run starts from this save.

## What to play

1. Walk out of the house to his car.
2. Drive laps of his neighbourhood: streets, a junction, a bridge if there is one nearby.
3. Also stop for a while: standing still in traffic, standing still looking at the sky, on foot in a quiet spot.
4. Play at least 15 minutes, as you would normally. No pausing in an empty scene to raise the average.

## What to report

1. **Frame rate seen in the world**: the peak in each situation (sky, quiet area on foot, traffic, busy street on foot, driving fast...).
2. **Stability index**: the share of the session spent in each band (18 and more, 15–18, 12–15, 9–12, 5–9, under 5).
3. **Average performance index**: average, median, 5 % low and 1 % low over the whole session.
4. The machine: GPU and its memory, CPU, RAM, driver version, Windows version, console profile (Series S or X), upscaler, and the exact settings or launcher used.
5. Known issues seen during the run (freezes, flicker, missing objects).

Samples are one-second averages taken while the world is on screen (loading screens and menus excluded). With this project, [`tools/fps-session.py`](../../tools/fps-session.py) computes the three tables from the run's log and prints one line to share. The session length comes from the log's own timestamps, and the line ends with the log's fingerprint: anyone you give the log to can rerun the tool and check that the line matches it.

## Rules

- No cherry-picked scenes. If a number comes from a quiet scene, say so.
- Report the bad numbers too. Freezes count.
- One machine is one machine: say that other cards may behave differently.
