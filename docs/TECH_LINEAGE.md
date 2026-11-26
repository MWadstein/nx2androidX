# Tech lineage and attribution

This fork is one branch of a family of native Switch-player projects. The map
below records where each layer came from and which sources our own commits drew
on. It is the companion to [NOTICE.md](../NOTICE.md) (licenses and copyright) and
[UPSTREAM_SYNC.md](UPSTREAM_SYNC.md) (the repeatable diff commands).

## The family tree

| Project | Role | Built on | License / source |
|---|---|---|---|
| [seedds/nxnative](https://github.com/seedds/nxnative) | The engine core: NSO rewriter, Horizon HLE host, NVN rendering, shader tools. Most of the "play a Switch game natively" technology lives here. | — | MIT, `Copyright (c) 2026 seedds`; our read-only remote `upstream-nxnative` tracks `main` (`e257bade` at last fetch). Our `nxnative/` subtree started at `6034fca`. |
| [shirai91/nx2android](https://github.com/shirai91/nx2android) | The Android port of nxnative: app, on-device file access, Vulkan backend, packaging. | seedds/nxnative | README says "MIT, as nxnative"; GitHub metadata has no root license. Our read-only remote `upstream-nx2android` tracks `main` (`2b6c4eeb` at last fetch); merge base `7cd66c36`. |
| [zFitness/nx2androidX](https://github.com/zFitness/nx2androidX) (also published as `MWadstein/nx2androidX`) | **This fork.** Keeps nx2android's Android app and adds the on-device porter/CLI/rootfs flow. Its README says "Port your own Nintendo Switch games to Android, natively". | shirai91/nx2android | GPL-3.0-or-later; see [NOTICE.md](../NOTICE.md). |
| [igawa6/peanuts-native](https://github.com/igawa6/peanuts-native) | A sibling Android fork: same core idea, plus a second-screen companion, incremental on-device builds and a 76-game catalog. **Not** built on this fork. | [Banana Native](https://git.eden-emu.dev/moceure/BananaNative), which is based on seedds/nxnative; it follows nx2android findings | The repository's LICENSE is MIT with copyrights for seedds, Swap2-Native contributors and EddizEge; the APK/shader translator as a whole is GPL-3.0-or-later. `PEANUTS.md` calls peanuts a thin overlay on BananaNative and states `upstream/android` is Banana Native and `peanuts` is the overlay. |
| [Banana Native](https://git.eden-emu.dev/moceure/BananaNative) | Peanuts' immediate upstream; Android launcher and host based on seedds/nxnative. | seedds/nxnative | MIT for the nxnative-derived part; GPL-3.0-or-later where LSFG / GPL shader code is linked. |
| Ryujinx, Eden, switch2mac, Anka Native, kartnative, nsz, etc. | Component libraries and findings credited by the projects above. | — | Listed in [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md) and in the upstream NOTICE files. |

In short: **nxnative = native ARM engine core; nx2android = Android layer on
that core; nx2androidX = our fork, adding on-device porting; peanuts-native =
a sibling Android fork on Banana Native, not a descendant of ours.** We borrow
generic fixes from all of them and credit the source in each commit.

## How we attribute

For every change copied or closely modelled on another project, the commit
message carries one of these lines:

```
Upstream: owner/repo@<full sha> (PR #n, author)
Follows:  owner/repo#n or <URL>    -- finding/design used, no code copied
Co-authored-by: Name <email>       -- when code was taken verbatim
```

`Upstream:` means implementation was ported from that commit. `Follows:` means
we read the finding and wrote our own code. Older pushed commits keep their
original messages; this file and the commit bodies below are the authority for
their provenance. We do not push upstream or open PRs unless explicitly asked.

## Provenance of our commits

| Our commit | Source | What was used |
|---|---|---|
| `315bb402` save root | Follows [shirai91/nx2android#281](https://github.com/shirai91/nx2android/pull/281) / [#538](https://github.com/shirai91/nx2android/pull/538) (custom save folder). | Feature concept; implementation is ours. One root, no copy/fallback. |
| `b262b8c1` Vulkan cache identity | Related upstream: [shirai91/nx2android@965387d4](https://github.com/shirai91/nx2android/commit/965387d45b6e4aa5b3df4c307e876e29ed135f6d) and [@92b0b4ad](https://github.com/shirai91/nx2android/commit/92b0b4ad57c75763d63e9cb65158e835eb85f087). | Independent fix for the same class of stale-cache crash; no code copied. |
| `96736e84` NVN queue raster origin | Upstream [seedds/nxnative@9b2f0851](https://github.com/seedds/nxnative/commit/9b2f08511800e10b64a383e276b455cf630d13a5), author seedds, from the Xeno 2 bring-up. | `origin_ll` captured at `nvnQueueInitialize`, selected per submission; adapted from Metal to our Vulkan front-face rule. |
| `aec6524a` Unreal 62 GB region | Follows [shirai91/nx2android#484](https://github.com/shirai91/nx2android/pull/484) (from zFitness PR #104). | `game_args -SwitchVirtualAddressSpaceSize=2048` plus a build-keyed Unreal cut; adapted to our tree. |
| `f6bb85ea` ARH2 + NVN2 shader readers | Upstream [seedds/nxnative@b32d0bf3](https://github.com/seedds/nxnative/commit/b32d0bf3b5fa7ddc8e0d9d006f3bad82ac82bd5c) for the Xeno X shader tables; from peanuts-native: [11ae83f3](https://github.com/igawa6/peanuts-native/commit/11ae83f315935acc23573b70542862301dc68c0b) (Banana Native import), [264df1fe](https://github.com/igawa6/peanuts-native/commit/264df1fe487333ad02e1291926557675615d1d54) (`Program.cs` Android fields) and [b9a9e406](https://github.com/igawa6/peanuts-native/commit/b9a9e406aa44ab8d9e2a37f9b338df9dab11b86e) (locked translator DLLs), all by igawa6. | ARH2/mixed Maxwell/NVN2 HCPS reader, Ampere C# sources, `Program.cs`, prebuilt DLLs; the Ampere decoder itself comes via peanuts from switch2mac/`nx2_lower` (Eglantine), GPL-3.0-or-later. |
| `9ed96fc3` keep AST optimizer off | Follows [seedds/nxnative#1415](https://github.com/seedds/nxnative/issues/1415). | `debug: True` for rare HCPS programs that otherwise throw `InvalidCastException`. |
| `7fbbf8fd` swkbd byte count | Upstream [seedds/nxnative PR #120](https://github.com/seedds/nxnative/pull/120), author huangzhuangchao, head `40b8a164a3f43087baafc24fa7995a7698342e3e`; the equivalent merged commit [fa69e20a](https://github.com/seedds/nxnative/commit/fa69e20a280413d56e64edcb8736bf9329957f77) explicitly left this half out. | Write the actual text-area byte count into `String{+8}`; our code implements the PR body's item 1 with tests. |
| `6a102740` device-shared pool memory | Upstream [seedds/nxnative@4861fb03](https://github.com/seedds/nxnative/commit/4861fb03e4668e16a95f49fad07eb40905df0cba), author seedds. | `dm_device_share()` refcounted ranges; unmap/shrink over live NVN pool storage refused with `0xD401`. |
| `227ff1f9` Xeno X 60 fps | Source: [FPSLocker-Warehouse 1.0.2 YAML](https://raw.githubusercontent.com/masagrator/FPSLocker-Warehouse/v4/SaltySD/plugins/FPSLocker/patches/0100453019AA8000/2A720C7CE5C84905.yaml). | The build's `ALL_FPS`, dynamicSpeed, camera/battle/fog/overdrive rows; assembler fixes are ours. |
| `94345391` movie EOS held inputs | Upstream [seedds/nxnative@637f3fa76](https://github.com/seedds/nxnative/commit/637f3fa76). | Return client-held inputs after EOS without decoding; portable source-order test replacing the Apple-framework C test. |
| `e36abd81` NVN host segment sizing | Upstream [seedds/nxnative@fc6c0a2a1](https://github.com/seedds/nxnative/commit/fc6c0a2a1). | `hostseg_size()`, 4 KB small grants, size-matched reuse, overflow by segment end. |
| `b508ba20` audio update lock / release notifier | Upstream [seedds/nxnative@c76a4242d](https://github.com/seedds/nxnative/commit/c76a4242d) and [@521906039](https://github.com/seedds/nxnative/commit/521906039). | Acquire-release disarm; `UpdateImpl` at +0x2d8 scan for newer SDKs. |
| `4fb4df2c` zstd dictionary frames | Upstream [seedds/nxnative@eb858ec51](https://github.com/seedds/nxnative/commit/eb858ec51ad65f95d6df6ecfb67bff853e3f07d3). | The dictionary half only; the frame-size half was already present locally. |
| `11d91b5d` Unreal bindless reflection | Our own fix, informed by the shader dumps. | `compact_bindings()` and 32-slot dynamic arrays; no external code. |
| `951cde79` Allow damaged builds | Follows the existing `nx_extract --allow-damaged` flag and the SMRPG damage report. | Porter plumbing and app checkbox are ours. |
| `b70c76e6`, `6676410a`, `d5c9d2a9`, `b70c76e6` etc. | Our own inventory of the read-only remotes. | Docs and skipped-fix rationale; no code copied. |
| Windows build fixes (`fix/build-from-source-windows`) | Our own branch in this fork. | Symlink handling, prebuilt C# tools/adrenotools, executable bits, runtime libs. |

The upstream sync shortlist and the reason each skipped fix was skipped are
recorded in [UPSTREAM_SYNC.md](UPSTREAM_SYNC.md), especially the "Considered
and skipped" section. The deferred stale-save-handle fix is `9a4a3c5f8`.
