<!-- game facts: made by docs/gen_tables.py from android.tsv; edit android.tsv, not this block -->
# Pokémon Violet

![Pokémon Violet](../../../../docs/images/pokemon-violet.jpg)

| | |
|---|---|
| Status | **playable** |
| Title ID | `01008F6008C5E000` |
| Tested with nx2android | `v0.4.0` |
| Tested build and device | 4.0.0 AYN Odin 2 (Adreno 740, Android 13, Turnip) |
| App package | `org.nx2a.pokemonviolet` |
| Needs | a GPU that reads BC-compressed textures (Adreno, Xclipse; not Mali or PowerVR) |

The profile sets these for you (`android.tsv`); a player changes the pause menu ones in the game, and the env rows in the data pack's `env.txt`:

| Row | What it does |
|---|---|
| `docked=0` | pause menu default on first launch: docked mode (1) or handheld mode (0) |
| `DM_DYN_SCALE=low` | the host's dynamic resolution: a level for a profile's env row, `low` (lowest scale 0.85 against 90% of the frame time), `medium` (0.70, 85%) or `high` (0.50, … |
| `DM_VK_LIN_COPY_BACK=1` | 1 = a texture copy into a LINEAR texture in CPU-visible memory also copies the region back to its storage, so the CPU reads what the GPU copied … |
| `DM_VK_UBO_COMPONENT=1` | 1 = fragment shaders' uniform buffer loads that pick a vector component at a non-constant index load the whole vector and take the component with … |
| `DM_VK_ZC_CHUNK_MB=512` | the chunk size in MB that a memory pool over it is cut into (unset: 256 MB, or the largest of 128 / 64 / 32 MB that this gralloc takes when it refuses 256 MB, … |

Read the profile's porting log in the comment header of [`android.tsv`](android.tsv). Back to the [games list](../../../../README.md#games).
<!-- end of the game facts -->

## Game version

- Update 4.0.0 (SDK 13.3.13). Other updates are not tested.

## Frame rate

- 30 fps (as on Switch). The profile's `fps_ceiling 30` holds it there.
- On the AYN Odin 2 it holds 30 in the opening, Cabo Poco, Poco Path and wild battles.
- Mezagoza plaza is the heavy case: while you turn the camera there, it drops to about 27 fps (frame time p50 about 37 ms).
- `--fps60` lifts the ceiling, but overworld frame work is 25-32 ms, so it gives about 33 fps, not 60. Game speed stays correct at 30 and at 33.
- Below 30 fps the game slows down rather than skipping ahead, as on Switch.

## Tested devices

| Device | GPU | Vulkan driver | Game version | nx2android | Result |
|---|---|---|---|---|---|
| AYN Odin 2 (Android 13) | Adreno 740 | Turnip (Mesa), packed with `--vulkan-driver` | 4.0.0 | `v0.4.0` | plays: the opening, Cabo Poco, Poco Path, Mezagoza, wild battles |
| AYN Odin 2 (Android 13) | Adreno 740 | system (Qualcomm 512.676) | 4.0.0 | `v0.4.0` | does not boot: crashes in `vkCmdDraw` on the first attachment-less pass |

## Options

- `--vulkan-driver`: pack a Turnip driver. The Odin 2's stock Qualcomm driver crashes before the game boots.
- Keep the profile's `DM_DYN_SCALE=low`. `medium` or `high` in the data pack's `env.txt` lowers resolution more in heavy scenes: `high` saves about 1 ms of GPU time but shows stair-stepped edges.
- `--fps60` is optional and gives about 33 fps (see Frame rate).

## Quirks and known issues

- Black frames in the classroom-to-crowd transition of the opening. The original game shows them too.
- The fixes in the profile's env rows are tested only on Turnip. Hair edges drew jagged white steps there without `DM_VK_UBO_COMPONENT=1`; keep that row.


<!-- upstream-nxnative README: upstream-nxnative/main -->

## Upstream bring-up history (seedds/nxnative)

# Pokémon Violet (`01008F6008C5E000`)

Base game 1.0.0 (v0), SDK 13.3.5, Game Freak's Trinity engine on NVN.
Pokémon Scarlet's twin ([0100A3D008C5C000](../0100A3D008C5C000/README.md)):
the same `sdk` (`3644a676…`) and `subsdk0` (`d0f13015…`, Nintendo's movie
module) builds, byte for byte; only `main` is a build of its own
(`959ed651…`, Scarlet's is `ca44e7dd…`). Everything in Scarlet's note about
the engine, memory, shaders, pipeline preparation and its open items holds
here; this note gives only what differs or was checked again. The profile is
Scarlet's with Violet's title, name, IPA name, build row and shader tables.
Playable on the Mac: language, look and name selection, the academy settings,
the opening, the Paldea flyover, getting up in the bedroom, walking, camera
control, the main menu and autosave, and reloading that save. iPhone testing
is pending; no IPA has been built yet.
Only 1.0.0 is registered. The NSP folder also holds update 4.0.0
(`v786432`), so build with `scripts/build_ipa_from_nsp.py <NSP folder> -k
<prod.keys> -p v0` (add `--platform mac` for a Mac build); without `-p` the
builder takes the newest version and derives a profile without these checks.

## What it needs

The same keys as Scarlet's profile, for the same reasons
([Scarlet, Memory](../0100A3D008C5C000/README.md#memory)): the alias region
for the host's StandardAllocator cap, `mem_map_limit on` for the startup
probe of all allocatable memory, `depth_mode zero` for the game's
near = 0 depth mode, and `pad_layout full`. The 62 MB node-area cut and the
alignment of large regions come with the `sdk` build (`dm/tools/sdk_patches.py`
and the SDK-wide rule). No host code is keyed to either game's `main`.

No `patches.py`.

## Files and shaders

- The base NSP extracts cleanly: 24 RomFS files, 6,369.2 MB, with the same
  layout as Scarlet's (`arc/data.trpfs` is the `romfs_marker`). The supplied
  DLC is a licence-only NSP, as for Scarlet.
- **Resolved lookup failure; base hash cause open:** [PR #2701](https://github.com/seedds/nxnative/pull/2701)
  reports a Rev 4 base whose ExeFS hash check fails when read alone, although
  its 4.0.0 update supplies readable code. The reporter verified that the
  [conditional build ID lookup](../../../docs/reference/packing.md#an-unreadable-unused-base-stops-discovery-after-a-readable-update)
  gets past the survey on a Mac15,6 (M3 Pro), macOS 26.7.3, in a fork based
  on an earlier main. The package failure was not independently reproduced;
  neither damage nor a sparse base has been established. This is survey
  validation, not gameplay validation of Rev 4 or 4.0.0.
- Shaders: 30,142 (14,999 vertex, 15,057 pixel, 86 compute; 40 in `main`),
  the same as Scarlet's. The split's tables (`shader_map.tsv`,
  `shader_facts.tsv`, `shader_pairs.tsv`, `pso_pairs.tsv`) have the same data
  rows as Scarlet's, byte for byte; only the map's header note differs. The
  prewarm list is Scarlet's (it names shaders by content key).
- Chain `b3ca4b7c621f`: all 30,142 translate and compile for the Mac, with no
  undecoded bindings. Each shader's cache key covers the profile, so Violet's
  build translates every shader again; with `DMSH_PREFILL` naming Scarlet's
  Mac library root, 19,949 Metal libraries were filled from Scarlet's build.
  The offline pipeline prebuild built 24,481 bases from 24,487 pairs
  (6 left to the draws, 0 failed) in 28 minutes.

## Performance

- On the Mac, with the build's pipeline archive: 30 fps as on the Switch
  (frame time p50 33.33 ms, p95 under 34 ms) through character selection, the
  opening and the bedroom; resident memory up to 4.7 GB, GPU allocations about
  1.6 GB. The only red line is the conservative-raster dilation diagnostic,
  as on Scarlet.
- **Open, not reproduced:** one frame of the first gameplay run took 42.5 s
  (frame 12,047, 454 s in), with 71 ms of submit and present and 11 ms of GPU
  time in it: the process waited rather than worked. It followed a covered
  window and a drawable resize to 2560x1440 in the same run, and overlapped
  another session's game host. Three later reload runs (frames 1,500 to 8,700)
  show nothing like it: worst frame 271 ms, worst p95 34.6 ms.

## Mac routes

- The work folder's `run/boot.sh <name> [seconds] [VAR=value ...]` runs the
  build headless with its own host copy (`build/vihost`), the build's pipeline
  archive (`DM_PSO_ARCHIVE`, the `_build/run/pso_archive` the NSP script
  prebuilt; without it a run from another folder prebuilds 24,487 pairs again
  before the first frame) and `DM_PRESENT_LINK=0`. Without the latter, a
  window covered mid-run presents about once a second and the game ran at
  about 12 fps.
- A fresh save reaches the bedroom with Scarlet's route: `DM_KBD=Taylor` and
  `DM_KEYS="f300:A,f600:LUp+LLeft~0.3,f660:A,f1000:A,f1300:A*90/90,f10300:LDown~2"`.
  It picks a different look than on Scarlet. The flyover plays around present
  frame 6,000, the get-up prompt around 9,900, and the player stands in the
  bedroom from about 10,600.
- `run/save_ref` is the autosave from that route; it loads at the desk. Then
  `DM_KEYS="f300:A*5/150"` gets up; the left stick walks, the right stick
  turns the camera, X opens the main menu.
- **Observed, not a fault:** holding the right stick toward the wall by the
  bed turns the camera into the wall: about 90 frames (3 s) are black (the void
  behind the room set) with the wall's lit edge at the right, while the
  "Now saving" overlay keeps drawing, and the camera comes back when the
  player moves. This looks like the game's own camera collision; it has not
  been compared with a Switch.

## Open

- iPhone gameplay, device memory and touch controls are untested; no IPA has
  been built. Build its iOS shaders with Scarlet's iOS libraries as prefill
  (`DMSH_PREFILL=<Scarlet Mac root>=<Scarlet iOS root>`) when they are on
  disk.
- Update 4.0.0 (`v786432`) is in the NSP folder but not registered. Scarlet's
  4.0.0 copy was damaged ([Scarlet, Files and builds](../0100A3D008C5C000/README.md#files-and-builds));
  whether Violet's is intact has not been checked.
- Outdoor exploration and battles have not been validated, as on Scarlet.
- [The freeze in Trinity's rendezvous](../../../docs/reference/threads.md#trinitys-rendezvous-loses-its-release-on-apple-cores)
  was reported here too, by its return addresses only. No main of this game is
  on the drive, so whether its completer matches the rewriter's rule is unchecked.
- [Conservative rasterization](../../../docs/reference/rendering.md#conservative-rasterization-remains-unimplemented)
  is unimplemented, as on Scarlet.

## Found on this game

The other findings are Scarlet's ([Found on this game](../0100A3D008C5C000/README.md#found-on-this-game)).

- [An unreadable unused base stops discovery after a readable update](../../../docs/reference/packing.md#an-unreadable-unused-base-stops-discovery-after-a-readable-update): the optional build ID probe is no longer fatal after a successful update read (resolved; [package evidence](#files-and-shaders)).
- [Bluetooth LE at boot](../../../docs/reference/services.md#bluetooth-le-at-boot): 3.0.1 (`v720896`, a derived profile) calls `nn::bluetooth::InitializeBle` a second after boot and aborted without the `bt` service; the host answers the BLE calls offline (resolved).
- [A recording that runs short before it writes into the game's memory](../../../docs/reference/nvn-objects.md#a-recording-that-runs-short-before-it-writes-into-the-games-memory): from 0d103787 the host stopped at the 1 GB cap of lent command memory at frame 1,939 ([PR #2713](https://github.com/seedds/nxnative/pull/2713), which found the cause; resolved).
