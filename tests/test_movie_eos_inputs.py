"""The held-input-after-EOS fix must not decode or signal for returned inputs."""
from pathlib import Path
import unittest

SRC = Path(__file__).resolve().parents[1] / 'nxnative/dm/host/hle_movie.c'


def body():
    s = SRC.read_text(encoding='utf-8')
    i = s.index('h_movie_SendIn')
    i = s.index('{', i)
    depth = 0
    for j in range(i, len(s)):
        if s[j] == '{':
            depth += 1
        elif s[j] == '}':
            depth -= 1
            if depth == 0:
                return s[i + 1:j]
    raise AssertionError('unbalanced h_movie_SendIn')


class MovieEosHeldInputs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.b = body()

    def test_eos_accepts_only_owned_inputs(self):
        self.assertIn('if (d->in_eos) {', self.b)
        self.assertIn('if (!d->inown[i] && !d->instale[i])', self.b)

    def test_held_input_is_returned_without_decode_or_signal(self):
        p = self.b.index('if (!d->inown[i] && !d->instale[i])')
        q = self.b.index('return 0;', p)
        part = self.b[p:q]
        self.assertIn('d->infree[d->ninfree++] = i', part)
        self.assertNotIn('md_pump(', part)
        self.assertNotIn('md_event(', part)

    def test_ownership_is_cleared_before_return(self):
        p = self.b.index('if (!d->inown[i] && !d->instale[i])')
        q = self.b.index('return 0;', p)
        self.assertLess(self.b.index('d->inown[i] =', p), q)
        self.assertLess(self.b.index('d->instale[i] =', p), q)

    def test_in_eos_is_set_only_after_the_packet_is_queued(self):
        queue = self.b.index('d->pend[d->npend].in = i')
        eos = self.b.index('d->in_eos = 1;')
        self.assertLess(queue, eos)

    def test_full_queue_is_checked_before_any_ownership_change(self):
        full = self.b.index('d->npend == MD_NIN')
        clear = self.b.index('d->inown[i] = d->instale[i] = 0; d->in_ns')
        self.assertLess(full, clear)


if __name__ == '__main__':
    unittest.main()
