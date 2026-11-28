"""Maximum performance is a GPU preset, never a hidden frame-rate override."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAWER = ROOT / 'android/app/src/main/java/com/nx/android/game/overlay/GameDrawer.kt'
STRINGS = ROOT / 'android/app/src/main/res/values/strings.xml'


class MaximumPerformancePresetTest(unittest.TestCase):
    def test_the_preset_does_not_change_the_frame_rate(self):
        text = DRAWER.read_text(encoding='utf-8')
        start = text.index('// GPU 最高频的一键开关')
        end = text.index('if (rateSupported)', start)
        block = text[start:end]
        self.assertNotIn('onPick(', block)
        self.assertNotIn('RatePin(60)', block)
        self.assertNotIn('RatePin(0)', block)
        self.assertIn('GpuTurbo.ON', block)
        self.assertIn('GpuTurbo.OFF', block)

    def test_the_hint_promises_to_keep_the_players_frame_rate(self):
        text = STRINGS.read_text(encoding='utf-8')
        match = re.search(r'<string name="drawer_max_performance_hint">(.*?)</string>', text)
        self.assertIsNotNone(match)
        hint = match.group(1)
        self.assertIn('without changing your frame-rate setting', hint)
        self.assertNotIn('Pins 60 FPS', hint)


if __name__ == '__main__':
    unittest.main()
