# Upstream sync inventory

This fork keeps its own Android app and porter, but it should not fall behind the two
repositories it grew from. Both are now read-only remotes:

- `upstream-nxnative` — [seedds/nxnative](https://github.com/seedds/nxnative), whose `dm/`
  tree was copied into `nxnative/dm/` as a squashed subtree at `6034fca` (2026-10-24).
- `upstream-nx2android` — [shirai91/nx2android](https://github.com/shirai91/nx2android),
  the product line this fork was forked from.

[peanuts-native](https://github.com/igawa6/peanuts-native) is a third source of
generic fixes. It is a sibling Android fork on Banana Native, not a descendant of
ours. See [TECH_LINEAGE.md](TECH_LINEAGE.md) for the full stack and for the exact
source of every borrowed fix.

Neither remote is ever pushed to. Work is committed to organized local branches; there
are no pull requests while this fork is used by one person. Commit bodies name the
source with `Upstream: owner/repo@sha`, `Follows: owner/repo#n` or `Co-authored-by:`
as described in [TECH_LINEAGE.md](TECH_LINEAGE.md).

## What is shared and what is not

The engine core is shared: `nxnative/dm/host/`, `nxnative/dm/gfx/`, `nxnative/dm/tools/`,
`nxnative/dm/games/`, `nxnative/dm/third_party/` and `nxnative/dm/android/`, plus the
engine's `tests/`. The app (`android/`), the on-device porter (`porter/`), APK packaging
(`packaging/`), this fork's `devtools/` and docs are ours alone. `devtools/upstream_conflict_surface.py`
classifies the paths and prints the files a merge would need a human to look at.

Game profiles are reference material, not automatic updates. A profile from upstream is
read to understand a game; fixes for our build stay in our own profile branch and are
validated on the device before they land.

## Where we stand

The counts below are mechanical path/status counts from `git diff --no-renames`; they are
an inventory of work, not a claim that every file should be copied.

Comparison of `HEAD:nxnative/dm` to `upstream-nxnative/main:dm` (`A` = present upstream,
not here; `M` = present on both sides but different; `D` = present here, not upstream):

| Area | Upstream-only (A) | Modified (M) | Local-only (D) |
| --- | ---: | ---: | ---: |
| `games/` | 1,125 | — | — |
| `gfx/` | 531 | — | — |
| `tools/` | 282 | — | — |
| `third_party/` | 254 | — | — |
| `host/` | 213 | — | — |
| `ios/` | 49 | — | — |
| **all `dm/`** | **1,884** | **578** | **793** |

Since the subtree base `6034fca`, upstream has 1,996 commits. Keyword counts over their
subjects: shader 335, `host/` 177, fps 141, fix 135, `gfx/` 111, memory 87, save 81,
cache 65, audio 46, `tools/` 40, crash 33, Vulkan 30. This is a large surface: port
correctness fixes one branch at a time, with tests, rather than taking a whole tree.

Against `upstream-nx2android/main`, the merge base is `7cd66c36`; upstream has 54 commits
we do not have and this line has 504 commits it does not have. The 156 upstream files
changed since the base are concentrated in `nxnative/` (105), `tests/` (30), `docs/` (11)
and `porter/` (5). The porter and app differences are expected — they are separate worlds.

A repeatable inventory can be produced with:

```
git log --oneline 6034fca..upstream-nxnative/main
git diff --no-renames HEAD:nxnative/dm upstream-nxnative/main:dm
python devtools/upstream_conflict_surface.py --upstream upstream-nx2android/main --ours HEAD
```

## Working method

1. Keep a dedicated branch per port (for example `fix/shader-vk-bindless-reflection`),
   cut from the current integration base. No PR and no push to an upstream.
2. Prefer a generic fix with a test over a profile-only workaround. Port only the shared
   core; skip Apple front ends and game-specific data unless they are the actual subject.
3. Check what this fork already has: several fixes arrived here independently (for
   example the Vulkan cache identity, queue raster origin, audio renderer offset and
   ARH2/NVN2 shader reader work).
4. Validate on the device when the fix touches runtime behavior, then merge the branch
   into `integration/all-fixes` so the next build starts from everything that works.
5. Record what was considered and why it was skipped. A mechanical diff is not a to-do
   list: many upstream-only files are platform front ends or profiles that do not apply.

## Considered and skipped

- `9a4a3c5f8` (stale save handles after rollback): needs upstream's canonical transaction
  root and per-generation fd table. This fork's `hle_fs.c` has neither, so it would be a
  full save-core port, not a small fix. Revisit when porting the transaction layer.
- `a3d58526b` (PG_NONE fault): local `nvn_dirty.c` already has a different span cache and
  Android-specific protection path; the upstream unit test cannot be transferred as-is.
- `e4e5ff64e` (`-fwrapv`): the changed compilers are Apple's `xcrun metal` front ends.
  Android compiles SPIR-V; it does not use those commands.
- `1e9e3df40`, `1e69c180c`, `0fd9b1c88`: already present or superseded here.
- Vulkan/Metal front-end commits (`392f98a1`, `d65c0af0`) and all `save_sync.c` / JIT
  plugin commits: those files are absent or replaced on Android.
