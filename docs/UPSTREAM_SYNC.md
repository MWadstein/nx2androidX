# Upstream sync inventory

This fork keeps its own Android app and porter, but it should not fall behind the two
repositories it grew from. Both are now read-only remotes:

- `upstream-nxnative` — [seedds/nxnative](https://github.com/seedds/nxnative), whose `dm/`
  tree was copied into `nxnative/dm/` as a squashed subtree at `6034fca` (2026-10-24).
- `upstream-nx2android` — [shirai91/nx2android](https://github.com/shirai91/nx2android),
  the product line this fork was forked from.

[peanuts-native](https://github.com/igawa6/peanuts-native) is a third source of
generic fixes. It is a sibling Android fork on Banana Native, not a descendant of
ours. [LNPANDY/NX2Apple](https://github.com/LNPANDY/NX2Apple) is a fourth research
source: an MIT-licensed Swift launcher/community fork of `seedds/nxnative` for
iPhone/iPad/Mac. It has the same engine core but its own front end, build seeds
and game-profile observations. It is not an ancestor of this fork; its Swift and
Metal launcher code does not transfer to Android, so use only portable nxnative
patches, issues and profile findings from it, with the attribution rule below.

[v0lumehi/nxkit](https://github.com/v0lumehi/nxkit) is a fifth research source:
an MIT-licensed Rust build tool and runtime for Apple silicon that runs both
Switch and Switch 2 games. It is an independent reimplementation, not a fork of
ours or of nxnative; its Metal 4 backend and title modules are Apple-only, so it
is useful for Switch 2 design/progress observations and general engine ideas,
not for direct code reuse. Switch 2 support here is a low-priority, bottom-of-list
item while upstream implementations are still Apple-only. For context,
`upstream-nxnative/main` is further along than that wording suggests: its README
lists 21 Switch 2 titles with Mac gameplay testing (including both Xenoblade 2
and Xenoblade X Switch 2 Editions), NUP/folder build instructions, and 88 commit
subjects mentioning Switch 2. It has NVN2/Ampere shaders, Switch 2 pad, Mii,
audio, codec and display work. Those builds are validated on Mac, not iOS, and
this Android tree has no NUP packing or Switch 2 service layer, so Switch 2
support here stays a research item rather than an imminent port.

See [TECH_LINEAGE.md](TECH_LINEAGE.md) for the full stack and for the exact
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
validated on the device before they land. We compare the files on every sweep and pull
only what our Android build actually consumes; copying a whole folder would overwrite
`android.tsv` (our app metadata and porting log) and can change shader inputs for a
build we have not validated. The upstream `README.md` files are the exception: they
are history, not inputs, so we keep them where the profile exists as provenance for
brings-up, allocator evidence and stability fixes. They are never authoritative for
Android behavior. See [TECH_LINEAGE.md](TECH_LINEAGE.md) for attribution.

### What the profile files do here

| File | Used on Android? | Notes |
|---|---|---|
| `game.tsv` | Yes | Title/build IDs, module list, memory layout and profile keys; read by the porter and rewriter. |
| `android.tsv` | Yes | Our layer: status, package, orientation, graphics, env rows and the porting log; drives the app library and generated docs. |
| `shader_map.tsv` (+ `.conflicts.tsv`) | Yes | Shader keys and stages used by the device split and translator. |
| `shader_facts.tsv` | Yes | Reflection answers not derivable from code; `shader_vk.py` loads it via `dmsh_facts`, and the host reads `shader_facts_manual.tsv` when a texture answer is wrong. |
| `shader_pairs.tsv` | Shared format, not an Android runtime input | Pipeline pairs for the Apple chain's build-time pairing; Android records `vk_pipelines.bin` at runtime instead. Kept for profile parity and chain inputs. |
| `pso_manifest.tsv` | No (legacy here) | Apple's prewarm seed list. Android prewarms from the per-pack pipeline records, so this is not read by our host. |
| `bf_want.tsv` | No direct Android use | Apple chain's rewritable-sample variant list; declared as a chain input but not used by `shader_vk.py`. |
| `README.md` | No (provenance) | Local game page plus appended `seedds/nxnative` bring-up history where it exists: tested builds, allocator/memory evidence, issues and stability findings. `devtools/append_upstream_readmes.py` appends it under a marker and is idempotent; it never overwrites the local page. Our gallery/checklist are generated from `android.tsv` by `docs/gen_tables.py`. |

Example checked on `010074F013262000` (Xenoblade Chronicles 3): `game.tsv`, all
shader tables, `.conflicts`, `shader_pairs`, `pso_manifest`, `bf_want` and
`shader_facts` are byte-identical to `upstream-nx2android/main`. Our `android.tsv`
adds `graphics nvn` and a `readme_note` row; those are our Android metadata and
should be kept. Upstream's `README.md` is now kept here too: it records the compact
4 GB / 512 MB arena trade-off, issue #3149 and the open Zstd worker crash — history
worth preserving as research, but not a substitute for our own validation.
The fuller `seedds/nxnative` README is appended below the local page; it records
issue #3149's 4 GB / 512 MB compact-layout exhaustion, the 60 GB restoration on
large alias regions, and the still-open Zstd worker crash.

On each sweep, check which upstream READMEs are missing or stale before deciding
what to pull:

```bash
git ls-tree -r --name-only upstream-nx2android/main -- nxnative/dm/games |
  grep '/README.md$'
git ls-tree -r --name-only HEAD -- nxnative/dm/games | grep '/README.md$'
```

Copy only the ones whose profile folder exists here, and keep Android-written
READMEs as-is.

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
   into `integration/main` so the next build starts from everything that works.
5. Record what was considered and why it was skipped. A mechanical diff is not a to-do
   list: many upstream-only files are platform front ends or profiles that do not apply.

## Cadence

Do not auto-merge or copy whole trees. Sync at these points instead:

- **Before a new game bring-up**: a light sweep of commit subjects in the shared area
  that game will use (HLE, NVN/gfx, shader tools, save/audio) to catch fixes already
  waiting. Pull only what applies to our build.
- **When a bug appears**: search upstream for that subsystem first. The Xeno X 60 GB,
  movie-EOS and NVN host-segment fixes were all found this way.
- **When changing shared core code**: compare the same upstream files before and after
  the change so we do not drift further from a fix we could have reused.
- **Every ~25 local commits or monthly, whichever comes first**: refresh the inventory
  counts and shortlist in this document; re-rank the top few portable fixes.
- **On a new upstream release or a large upstream merge**: an immediate targeted review
  of changed shared files, not a tree-wide replacement.
- **After a device validation pass**: record which fixes are proven here and promote
  repeated external fixes into our own profile/tooling data with attribution.

Profile folders are compared on each sweep but only pulled selectively, per the table
above. No PRs or pushes to upstream unless explicitly asked.

## Local workflow

`integration/main` is the working base for this single-person fork. The old
`integration/all-fixes` branch remains on `myfork` as a historical alias. Keep
the base clean and pushed before starting new work. Do the work in a separate
worktree so the base checkout stays untouched:

```
git fetch myfork upstream-nxnative upstream-nx2android
git worktree add ../nx2androidx-worktrees/fix/<name> -b fix/<name> integration/main
# edit, add tests, run the Python/arch/Kotlin checks, validate on the device
git -C ../nx2androidx-worktrees/fix/<name> commit -m "fix(<area>): ..."
git merge --no-ff fix/<name> -m "chore: fold <name>"
git push myfork integration/main
git worktree remove ../nx2androidx-worktrees/fix/<name>
```

Before merging, confirm the branch contains exactly the intended commits and
that the base has no uncommitted changes. After merging, run the checks again
on the base. If shared runtime C changed, bump `PLAYER_API_REVISION`, rebuild
the APK from `integration/main`, install it, and let the device rebuild
game runtimes. Build from the base branch, never from a feature worktree, so a
fix cannot exist only in a branch.

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
