// What the tests that link hle_nvn.c and hle_bigstack.c without the host need of it: weak definitions, so a test that defines its own keeps it
#include <stdint.h>
__attribute__((weak)) uint64_t g_t0_ns;   // process start time (host main.c), read by hle_nvn's per-frame timing
__attribute__((weak)) int dm_guest_as_contains(uintptr_t address) { (void)address; return 0; }   // no guest address space (hle_bigstack.c)
__attribute__((weak)) void dm_device_share(const void *p, uint64_t size, int share) { (void)p; (void)size; (void)share; }   // no SVC layer (hle_svc.c), told of each pool's storage by hle_nvn
