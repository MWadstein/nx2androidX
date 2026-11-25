"""The gate's dispatch runs on the host stack, and a crash leaves a trace.

A guest thread's stack can be nearly spent: Fire Emblem: Three Houses has a thread with a 4 KB
stack and 1.8 KB left, and the host's printf (__vfprintf's frame is 0x2c0 bytes) ran off its end -
SIGSEGV one page below the guest's stack. The dispatch now runs on the thread's host stack (the one
the take-over functions use); the gate's own frame stays on the guest's stack, because the handler
writes the guest's registers back into it and a thread stopped inside an SVC reads its context from
it. A thread that is already on a host stack stays where it is.

And the crash report's first line goes out at once: the app's stderr is line-buffered and that line
has no newline of its own, so a crash that kills the process before the newline (the Android host:
the driver's compiler faults inside the crash handler) left the log without any trace of it.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
HOST = ROOT / 'nxnative/dm/host'


class GateStack(unittest.TestCase):
    def test_the_dispatch_is_called_through_the_host_stack(self):
        entry = (HOST / 'entry.S').read_text(encoding='utf-8')
        self.assertIn('_dm_gate_call:', entry)             # the gate's dispatch, on the host stack
        self.assertIn('bl _dm_gate_stack', entry)          # which asks for the thread's host stack
        self.assertIn('bl _dm_gate_call', entry)           # the gate itself goes through it
        self.assertIn('bl _gate_dispatch', entry)          # and the dispatch is still the gate's

    def test_the_host_stack_is_the_one_the_take_over_functions_use(self):
        big = (HOST / 'hle_bigstack.c').read_text(encoding='utf-8')
        self.assertIn('uintptr_t dm_gate_stack(uintptr_t sp)', big)
        self.assertIn('dm_bigstack_top(sp)', big)          # the stack the take-over functions use


class CrashReport(unittest.TestCase):
    def test_the_first_line_is_flushed(self):
        crash = (HOST / 'crash.c').read_text(encoding='utf-8')
        first = crash.index('fprintf(stderr, "[dm] CRASH sig=%d", sig);')
        self.assertIn('fflush(stderr);', crash[first:first + 400])   # the line goes out before the process dies


if __name__ == '__main__':
    unittest.main()
