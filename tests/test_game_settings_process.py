"""The game page's settings live in a file no other process writes.

The game page runs in the `:play` process; the library, the port service and the last-launch record run in
the main one. SharedPreferences is not safe across processes - each process's write rewrites the whole file
from its own copy - so a drawer setting saved by the game page used to be dropped by the next main-process
write and read back as it was before. `PrefsStore.game` is the file that only the game page writes.

What is held here:
  1. the game store is a file of its own, not the app's (`nx2a`)
  2. it falls back to the app's file, so keys an older version saved there are still read
  3. it commits instead of applies: the game ends by killing its process
  4. every setting the drawer writes goes through it (a new one that does not would be lost the same way)
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KT = ROOT / 'android/app/src/main/java/com/nx/android'
STORE = KT / 'data/PrefsStore.kt'
ACTIVITY = KT / 'game/GameActivity.kt'


class GameSettingsProcessTest(unittest.TestCase):

    def setUp(self):
        self.store = STORE.read_text(encoding='utf-8')
        self.activity = ACTIVITY.read_text(encoding='utf-8')

    def test_the_game_store_is_its_own_file(self):
        self.assertIn('const val GAME_NAME = "nx2a.game"', self.store)
        self.assertIn('fun game(ctx: Context) = PrefsStore(ctx, GAME_NAME)', self.store)
        name = re.search(r'const val NAME = "([^"]+)"', self.store).group(1)
        game = re.search(r'const val GAME_NAME = "([^"]+)"', self.store).group(1)
        self.assertNotEqual(name, game, 'the game store must not share the app\'s file')

    def test_the_game_store_still_reads_what_an_older_version_saved(self):
        self.assertIn('legacy?.getString(key, null)', self.store)
        self.assertIn('legacy?.contains(key)', self.store)

    def test_the_game_store_commits_because_its_process_is_killed(self):
        commit = re.search(r'if \(file == NAME\) edit\.apply\(\) else edit\.(commit\(\))', self.store)
        self.assertIsNotNone(commit, 'a game-page write must commit, not apply')

    def test_every_setting_the_drawer_writes_uses_the_game_store(self):
        # the four per-game settings and the performance HUD: all built on the game page's file
        for cls in ('FrameGenSettings', 'RateSettings', 'MotionSettings', 'CheatSettings'):
            self.assertIn(f'{cls}(gamePrefs, it)', self.activity)
        self.assertIn('val gamePrefs = PrefsStore.game(this)', self.activity)
        for key in ('HUD_STATS', 'HUD_DEVICE', 'HUD_FIELDS', 'HUD_TEMP_F', 'EXTERNAL_DISPLAY'):
            self.assertIn(f'PrefsStore.game(this).put(PrefsStore.{key}', self.activity)
        self.assertIn('gamePrefs.bool(PrefsStore.HUD_STATS', self.activity)

    def test_the_game_store_is_not_used_for_what_the_main_process_owns(self):
        # the last launch, the keys file, the save root and the library's memory stay in the app's own file
        self.assertNotIn('PrefsStore.game(this).saveRoot', self.activity)
        self.assertNotIn('gamePrefs.writeKeys', self.activity)
        self.assertIn('padView = PadView(this, PrefsStore(this)', self.activity)


if __name__ == '__main__':
    unittest.main()
