"""Regression checks for APK builds run from a worktree.

The shell wrapper shares one cache between worktrees, but the Python helpers
used to default to their own checkout-local .cache unless the wrapper passed
the shared path explicitly. That made clean worktree builds fail even though
the main checkout had every downloaded asset.
"""
from pathlib import Path
import importlib.util
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
BUILD_APK = ROOT / "packaging" / "android-apk" / "build_apk.sh"
SPEC = importlib.util.spec_from_file_location(
    "build_nx_extract", ROOT / "packaging" / "android-apk" / "build_nx_extract.py"
)
BUILD_NX_EXTRACT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILD_NX_EXTRACT)


class ApkBuildPaths(unittest.TestCase):
    def test_helpers_use_the_shared_cache(self):
        script = BUILD_APK.read_text(encoding="utf-8")
        self.assertIn('--toolchain "$cache/toolchain" --cache "$cache"', script)
        self.assertIn('--finalize --cache "$cache"', script)
        self.assertIn('build_nx_extract.py" --out "$cache/assets/tool/tools/nx_extract"', script)

    def test_windows_wrapper_does_not_force_stale_csharp_tools(self):
        wrapper = (ROOT / "devtools" / "build_apk.ps1").read_text(encoding="utf-8")
        self.assertNotIn("$env:NX2A_CSHARP_PREBUILT =", wrapper)
        self.assertNotIn("Remove-Item Env:DOTNET", wrapper)

    def test_cross_published_apphost_uses_the_target_rid_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            linux = out / "nx_extract"
            linux.write_bytes(b"")
            self.assertEqual(
                BUILD_NX_EXTRACT.apphost(out, "nx_extract", "linux-arm64"), linux
            )
            windows = out / "dmsh_xlate.exe"
            windows.write_bytes(b"")
            self.assertEqual(
                BUILD_NX_EXTRACT.apphost(out, "dmsh_xlate", "win-x64"), windows
            )
            self.assertIsNone(BUILD_NX_EXTRACT.apphost(out, "missing", "linux-arm64"))


if __name__ == "__main__":
    unittest.main()
