"""Android translator jobs must keep the host capabilities shader_vk.py declares.

The NVN2 translator rewrite removed Accessor's Android overrides, enabled the
AST optimizer switch globally, and switched Maxwell jobs to NVN2's full texture
pools. The host still sends render_scale/viewport_mask and transform-feedback
metadata and binds Maxwell dynamic arrays slot by slot, so those changes alter
SPIR-V and replay reflection even when the shader extraction keys are identical.
"""
import ast
import os
from pathlib import Path
import struct
import tempfile
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'nxnative/dm/android/tools/shader_vk.py'
PROGRAM = ROOT / 'nxnative/dm/gfx/tools/dmsh_xlate/Program.cs'
MAGIC = bytes.fromhex('34127698')


def load_job_for():
    tree = ast.parse(SOURCE.read_text(encoding='utf-8'))
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'job_for')
    env = {
        'os': os,
        'struct': struct,
        'SB_ALIGN': 256,
        'SUBGROUP': 128,
        'GATHER_BIAS': 8,
        'FACTS': {},
        'NVN2_STAGE_INDEX': {'ps': 4},
        'vertex_ab': lambda key, code, ctl: None,
        'xfb_layout': lambda key, ctl: None,
    }
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(SOURCE), 'exec'), env)
    return env


class AndroidTranslatorCompat(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='nx2a_android_xlate_')
        self.addCleanup(self.tmp.cleanup)
        self.work = self.tmp.name
        self.code = bytes(range(0x80))
        self.record = b'BTCDBTCD' + bytes(0x30) + self.code + MAGIC + bytes(0x800)

    def job(self, nvn2):
        env = load_job_for()
        env['dmsh_ampere'] = SimpleNamespace(
            is_nvn2=lambda ctl: nvn2,
            c1_segment=lambda ctl, code: b'',
            inst_len=lambda ctl: len(self.code),
            early_fragment_tests=lambda ctl: False,
        )
        return env['job_for']('0123456789abcdef', 'ps', self.record, self.work)[0]

    def test_maxwell_jobs_keep_the_ast_optimizer_enabled(self):
        job = self.job(False)
        self.assertIs(job['debug'], False)
        self.assertIs(job['viewport_mask'], False)
        self.assertIs(job['render_scale'], False)

    def test_nvn2_jobs_keep_the_hcps_optimizer_workaround(self):
        job = self.job(True)
        self.assertIs(job['debug'], True)
        self.assertEqual(job['arch'], 'sm86')
        self.assertEqual(job['stage_bank'], 29)
        self.assertIs(job['viewport_mask'], False)
        self.assertIs(job['render_scale'], False)

    def test_android_host_capability_overrides_remain_in_the_translator(self):
        source = PROGRAM.read_text(encoding='utf-8')
        for signature in (
            'public int QueryGeometryPassthroughAttributeMask()',
            'public bool QueryHostSupportsViewportMask()',
            'public bool QueryHostSupportsRenderScale()',
            'public bool QueryTransformFeedbackEnabled()',
            'public ReadOnlySpan<byte> QueryTransformFeedbackVaryingLocations(int bufferIndex)',
            'public int QueryTransformFeedbackStride(int bufferIndex)',
        ):
            with self.subTest(signature=signature):
                self.assertIn(signature, source)

    def test_maxwell_keeps_android_dynamic_array_limits(self):
        source = PROGRAM.read_text(encoding='utf-8')
        self.assertIn('public int QuerySamplerArrayLengthFromPool() => (string)_job["arch"] == "sm86" ? 1 << 12 : 32;', source)
        self.assertIn('public int QueryTextureArrayLengthFromBuffer(int slot) => (string)_job["arch"] == "sm86" && slot == 2 ? C2HandleWords : 32;', source)
        self.assertIn('public int QueryTextureArrayLengthFromPool() => (string)_job["arch"] == "sm86" ? 1 << 20 : 32;', source)


if __name__ == '__main__':
    unittest.main()
