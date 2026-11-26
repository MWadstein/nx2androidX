<!-- game facts: made by docs/gen_tables.py from android.tsv; edit android.tsv, not this block -->
# 13 Sentinels: Aegis Rim (Asia)

![13 Sentinels: Aegis Rim (Asia)](../../../../docs/images/13-sentinels-asia.jpg)

| | |
|---|---|
| Status | **playable** |
| Title ID | `01008D7016438000` |
| Tested with nx2android | `v0.4.0` |
| Tested build and device | v0 Xiaomi 23117RK66C (Snapdragon 8 Gen 3, Adreno 750, Android 16) |
| App package | `org.nx2a.thirteensentinelsasia` |
| Needs | a GPU that reads BC-compressed textures (Adreno, Xclipse; not Mali or PowerVR) |

Read the profile's porting log in the comment header of [`android.tsv`](android.tsv). Back to the [games list](../../../../README.md#games).
<!-- end of the game facts -->

## Game version

- Base game 1.00.
- The Asian release (Japanese, Korean, Chinese).
- The profile was checked with `v0` (the `tested` row of android.tsv).

## Frame rate

- 60 fps.

## Tested devices

| Device | GPU | Vulkan driver | Game version | nx2android | Result |
|---|---|---|---|---|---|
| Xiaomi 23117RK66C (Snapdragon 8 Gen 3, Adreno 750, Android 16) | Adreno 750 | not recorded | 1.00 (v0) | `v0.4.0` | playable |

Tested on the Xiaomi 23117RK66C (Android 16).

## Options

- Not recorded.

## Quirks and known issues

- Not recorded.

## Porting notes

Status: **playable** — ported and played on an Android device.

The Asian release (Japanese, Korean, Chinese) of the game the western profile `01003FC01670C000` covers: its own title ID and its own `main` build, the same `subsdk0` / `sdk` builds and the same shader keys at other offsets in `main`. It covers **1.00 (`v0`)**, title ID `01008D7016438000`. Other game versions are outside this assessment.

### Compatibility evidence

NVN GLSLC shaders are embedded in main; shaders/pairs match the supported western game (the offsets differ in `shader_map`). The existing `alloc_big_align`, movie path, pool chunking, BC textures and renderer support apply; no code is keyed to this Asian main.

The game and build are supported by nxnative; see its [game notes](https://github.com/seedds/nxnative/blob/3084f7a205bcb3a9cb74cf26180dabcc01c7abca/dm/games/01008D7016438000/README.md) and [profile](https://github.com/seedds/nxnative/blob/3084f7a205bcb3a9cb74cf26180dabcc01c7abca/dm/games/01008D7016438000/game.tsv). The local profile is authored from that build metadata, with the shader input tables consumed by this fork.

Relevant existing paths:

- `nxnative/dm/gfx/tools/shader_split.py`

### Build and defaults

| Module | Build ID |
|---|---|
| `main` | `311947020f64f5742ce3c16162c4d87f` |
| `subsdk0` | `507f19d1240d09d00992248e8a0fd77e` |
| `sdk` | `2d369d9999e3e10e665106f840ffff9b` |

Android starts docked, with the gamepad visible. The gamepad's theme pack is the western release's (`13sentinels`), and the gamepad's layout, the pause menu's settings and the operation mode are the western profile's, so the two releases play the same way.

### Device testing

Tested on the **Xiaomi 23117RK66C** (Snapdragon 8 Gen 3, Adreno 750, Android 16), the player's own dump and keys:

1. The port of the version above finishes without missing inputs: the extraction, the rewriting and the shader translation all complete (the profile's 751 shader keys all resolve).
2. A fresh save goes through the menus into gameplay: the game's Chinese text, its cutscenes and its save menu work, the sound plays, and the on-screen gamepad draws the theme.
3. 58-59 fps at 1440p (the game's own frame rate), 1.4 GB resident, no red log line.

The frame rate is the game's own: the western release asks for 60 fps (present interval 1) and so does this one, the same engine and the same display.


<!-- upstream-nxnative README: upstream-nxnative/main -->

## Upstream bring-up history (seedds/nxnative)

# 13 Sentinels: Aegis Rim, Asian release (`01008D7016438000`)

Base game 1.00 (v0), SDK 11.4.3: the Japanese / Korean / Chinese cartridge and eShop release, under its own title ID. Vanillaware's own engine on NVN, as in the western release ([01003FC01670C000](../01003FC01670C000/README.md)), whose note covers the engine. Modules `main`, `subsdk0` (NintendoSDK_movie 11.4.3) and `sdk`. `subsdk0` and `sdk` are the western builds; `main` (`31194702…`) is not the western 1.10's (`4b632573…`), so the NSP script's lookup by main build ([`same_build`](../../../scripts/build_ipa_from_nsp.py)) does not find the western profile for it. Plays on the Mac from the base NSP alone (packed with `--platform mac`): 60 fps with sound, saving and loading (PR #161). Not tested on the iPhone.

## What it needs

| Setting | Where | Why |
|---|---|---|
| `alloc_big_align on` | [`game.tsv`](game.tsv) | the engine's ring heaps are cut from a memory pool at 64 KB alignment; without it they do not fit the pool ([the western note, Memory](../01003FC01670C000/README.md#memory)) |
| 4 GB layout: `mem_reserve 0x100000000`, `mem_alias 0x10000000`, `mem_stack 0x10000000`, `app_pool 0xCD500000` | `game.tsv` | as the western profile: no system resource in the NPDM, the game sets a heap |
| `sys_resource 0x0` | `game.tsv` | the NPDM declares no system resource (the NSP script writes it from the NPDM) |
| `depth_mode zero` | `game.tsv` | the game sets the near = 0 depth mode, so the pipeline bases made before it runs (the NSP script's Mac prebuild, and a [pipeline archive made offline](../../../docs/development.md#the-pipeline-archive-made-offline) for the iPhone when one is built with `DM_PSO_GPUS`) take its vertex shaders' `main0_z` entries (the host itself follows the mode the game sets) |

No `patches.py`, no `sdk_patches.py` cut for its `sdk` build (`2d369d99…`), no `pad_layout` (the iPhone pad starts in the 2D layout). The rest of the profile is the NSP script's provisional one.

## Files and shaders

- The data is in CRI CPK archives as in the western release; `ROBO_CN.CPK` is the `romfs_marker`.
- Shaders: GLSLC outputs in `main`, with the same keys as the western release's (all 751 `shader_map.tsv` rows; `shader_pairs.tsv`, `shader_facts.tsv` and `bf_want.tsv` are identical), at other offsets in `main`.

## Found on this game

- **Guest clock frozen and clock reads parked during NVN `mtl_prepare()` and `pso4_init()`** (`hle_os.c`, `nvn_mtl.m`): [Guest threads running ahead during the prepare step or archive open](../../../docs/reference/nvn-objects.md#guest-threads-running-ahead-during-the-prepare-step-or-archive-open) (reported on this release from a USB 2.0 disk in PR #2936).

## Open

- Not tested on the iPhone.
- `pso_manifest.tsv` is not recorded yet (no prewarm).
- Only the base game was packed; no update is known.
- Whether the western base game's own `main` (v0) is this build was not checked; the western profile registers only its 1.10.
