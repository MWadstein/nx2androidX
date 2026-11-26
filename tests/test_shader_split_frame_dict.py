import os
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'nxnative/dm/gfx/tools'))
os.environ.setdefault('DM_GAME', '01004D300C5AE000')

import shader_split  # noqa: E402


class ShaderSplitFrameDictTest(unittest.TestCase):
    def test_dict_id_is_read_from_the_frame_header(self):
        frame = bytes.fromhex('28b52ffd') + bytes([0x01, 0x00, 0x2a]) + b'rest'
        self.assertEqual(shader_split.zs_dict_id(frame), 42)
        self.assertEqual(shader_split.zs_dict_id(bytes.fromhex('28b52ffd') + b'\x00\x00'), 0)

    def test_size_prefixed_frame_is_opened_only_when_its_own_size_agrees(self):
        raw = b'hello shader code'
        frame = shader_split.zstd_mod().compress(raw)
        good = len(raw).to_bytes(4, 'little') + frame
        self.assertEqual(shader_split.unsized(good, 'test'), raw)
        bad = (len(raw) + 1).to_bytes(4, 'little') + frame
        self.assertEqual(shader_split.unsized(bad, 'test'), bad)

    def test_unknown_dictionary_is_reported_not_fatal(self):
        frame = bytes.fromhex('28b52ffd') + bytes([0x01, 0x00, 0x2a]) + b'rest'
        data = (16).to_bytes(4, 'little') + frame
        self.assertEqual(shader_split.unsized(data, 'test'), data)


if __name__ == '__main__':
    unittest.main()
