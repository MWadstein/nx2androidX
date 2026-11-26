import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'nxnative/dm/host/hle_audren.c'


class AudioUpdateLockTest(unittest.TestCase):
    def test_lock_is_read_from_update_then_update_impl(self):
        src = SOURCE.read_text(encoding='utf-8')
        body = src[src.index('static int update_lock('):]
        body = body[:body.index('static Result render_once(')]
        self.assertIn('AudioRenderSystem6UpdateE', body)
        self.assertIn('AudioRenderSystem10UpdateImplE', body)
        self.assertNotIn('!gen20 && update_lock', body)

    def test_notifier_disarms_with_acquire_release(self):
        src = (ROOT / 'nxnative/dm/host/hle_audio.c').read_text(encoding='utf-8')
        self.assertIn(
            'atomic_exchange_explicit(&a->notify_armed, 0, memory_order_acq_rel);',
            src,
        )


if __name__ == '__main__':
    unittest.main()
