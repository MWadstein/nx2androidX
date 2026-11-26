"""The app does not carry the game profiles: they are imported by the player, and the tools that read a profile find them there."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('phone_assets', Path(__file__).resolve().parents[1] / 'packaging/android-apk/build_assets.py')
assets = importlib.util.module_from_spec(spec)
spec.loader.exec_module(assets)


class ApkProfilesTest(unittest.TestCase):
    def test_a_profile_folder_is_the_one_named_after_a_title_id(self):
        self.assertTrue(assets.in_profile_dir(Path('nxnative/dm/games/0100000000010000/game.tsv')))
        self.assertTrue(assets.in_profile_dir(Path('nxnative/dm/games/0100000000010000')))
        self.assertFalse(assets.in_profile_dir(Path('nxnative/dm/games/game.tsv')))
        self.assertFalse(assets.in_profile_dir(Path('nxnative/dm/games/settings.tsv')))
        self.assertFalse(assets.in_profile_dir(Path('nxnative/dm/android/tools/android_profile.py')))
        self.assertFalse(assets.in_profile_dir(Path('porter/profiles.py')))

    def test_the_copy_leaves_the_profiles_out_and_keeps_the_tools(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'nxnative/dm/games'
            (source / '0100000000010000').mkdir(parents=True)
            (source / '0100000000010000' / 'game.tsv').write_text('title_id\t0100000000010000\n')
            (source / '0100000000010000' / 'shader_map.tsv').write_text('a\tb\n')
            (source / 'game.py').write_text('# the profile loader\n')
            (source / 'settings.tsv').write_text('# the settings\n')
            assets.copy_tree(root, root / 'out')
            out = root / 'out/nxnative/dm/games'
            self.assertTrue((out / 'game.py').is_file())          # the tools that read a profile travel
            self.assertTrue((out / 'settings.tsv').is_file())
            self.assertFalse((out / '0100000000010000').exists())   # the profiles do not

    def test_the_phone_translator_gets_this_trees_assemblies_not_its_launcher(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'nxnative/dm/gfx/tools/dmsh_xlate_bin'
            source.mkdir(parents=True)
            (source / 'dmsh_xlate.dll').write_bytes(b'ampere')
            (source / 'Ryujinx.Graphics.Shader.dll').write_bytes(b'ampere shader')
            dst = root / 'tool/tools/dmsh_xlate'
            dst.mkdir(parents=True)
            (dst / 'dmsh_xlate').write_bytes(b'phone launcher')
            (dst / 'dmsh_xlate.dll').write_bytes(b'old')
            old_assets = assets.REPO
            assets.REPO = root
            try:
                assets.translator_dlls(root / 'tool')
            finally:
                assets.REPO = old_assets
            self.assertEqual((dst / 'dmsh_xlate.dll').read_bytes(), b'ampere')
            self.assertEqual((dst / 'Ryujinx.Graphics.Shader.dll').read_bytes(), b'ampere shader')
            self.assertEqual((dst / 'dmsh_xlate').read_bytes(), b'phone launcher')


if __name__ == '__main__':
    unittest.main()
