"""The Android exporter keeps huge bindless binding numbers inside the packed reflection."""
import ast
from pathlib import Path
import re
import struct
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / 'nxnative/dm/android/tools'
sys.path.insert(0, str(TOOLS))


def exporter():
    source = TOOLS / 'shader_vk.py'
    tree = ast.parse(source.read_text())
    names = {'OP_DECORATE', 'DEC_BINDING', 'TEX_BASE', 'SSBO', 'KIND', 'DESC', 'SAMP_NONE'}
    nodes = [n for n in tree.body if
             isinstance(n, ast.FunctionDef) and n.name in ('classify', 'refl_bin', 'compact_bindings') or
             isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in names or
                 isinstance(t, ast.Tuple) and any(isinstance(v, ast.Name) and v.id in names for v in t.elts)
                 for t in n.targets)]
    env = {'re': re, 'struct': struct, 'GAME': {}}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(source), 'exec'), env)
    return env


def spirv_with_bindings(*bindings):
    words = [0x07230203, 0x00010000, 0, 100, 0]
    for i, binding in enumerate(bindings, 1):
        words += [(4 << 16) | 71, i, 33, binding]  # OpDecorate <id> Binding <number>
    return struct.pack(f'<{len(words)}I', *words)


class BindlessReflection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.export = exporter()

    def test_compact_bindings_renumbers_spirv_and_reflection_together(self):
        spv = spirv_with_bindings(1052688, 4, 1048580)
        binds = [{'name': f'res{i}', 'type': 'ubo', 'binding': b, 'count': 1}
                 for i, b in enumerate((1052688, 4, 1048580))]
        res = {'cbufs': [{'binding': 1052688}], 'textures': [{'binding': 4}],
               'images': [{'binding': 1048580}]}
        spv, binds, res = self.export['compact_bindings'](spv, binds, res)
        self.assertEqual([b['binding'] for b in binds], [3, 1, 2])  # sorted by old value
        self.assertEqual(res['cbufs'][0]['binding'], 3)
        self.assertEqual(res['textures'][0]['binding'], 1)
        w = struct.unpack(f'<{len(spv) // 4}I', spv)
        self.assertEqual([w[i + 3] for i in (5, 9, 13)], [3, 1, 2])

    def test_bindless_cb0_40000000_arrays_become_32_slot_dynamic_arrays(self):
        self.export['GAME']['android_dynamic_slots'] = 'on'
        for name, kind in [('ps_t2d_cb0_40000000', 'texd'), ('ps_s_cb0_40000000', 'sampd')]:
            with self.subTest(name=name):
                b = {'name': name, 'type': 'sampler' if kind == 'sampd' else 'image',
                     'binding': 2, 'count': 32}
                e = self.export['classify']('ps', b, {})
                self.assertEqual(e['kind'], kind)
                self.assertEqual(e['count'], 32)
                packed = self.export['refl_bin']([e], b'', [1, 1, 1])
                self.assertEqual(len(packed), 40)  # 20-byte header + one 20-byte dmsv_bind
                self.assertEqual(struct.unpack_from('<H', packed, 26)[0], 32)  # count

    def test_large_array_length_alone_does_not_imply_dynamic_handles(self):
        b = {'name': 'ps_t2d_cb0_40000000', 'type': 'image', 'binding': 2, 'count': 1048576}
        e = self.export['classify']('ps', b, {})
        self.assertEqual(e['kind'], '?')

    def test_reflection_header_counts_only_records_that_fit(self):
        good = {'kind': 'tex', 'type': 'image', 'binding': 2, 'count': 32}
        bad = dict(good, binding=0x10000)
        packed = self.export['refl_bin']([good, bad], b'', [1, 1, 1])
        self.assertEqual(struct.unpack_from('<I', packed, 0)[0], 1)
        self.assertEqual(len(packed), 40)


if __name__ == '__main__':
    unittest.main()
