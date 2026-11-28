"""Prewarm progress must count every recorded pipeline exactly once."""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import unittest

from csrc import REPO, function, unit


DM = REPO / 'nxnative/dm'


STUBS = r'''
#define _GNU_SOURCE
#include <assert.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/resource.h>
#include <unistd.h>
#include <vulkan/vulkan_core.h>

#define PIPE_PENDING ((VkPipeline)(uintptr_t)2)
typedef struct { uint64_t key[3]; int raster_discard; } pkey;
typedef struct { int set; VkDescriptorSetLayout dsl; } vkshader_t;
typedef struct { size_t klen; } nvn_hmap;
static nvn_hmap g_pipes;
static struct { VkDevice dev; } V;
static pkey *g_pw;
static size_t g_pw_n;
static volatile size_t g_pw_next, g_pw_done;
static pthread_mutex_t g_pipe_mu = PTHREAD_MUTEX_INITIALIZER;

static int cached[256], built[256], pending[256], missing_shader;
static atomic_int build_calls, put_calls, destroy_calls;
static void *nvn_hm_get(nvn_hmap *map, const void *key) {
    assert(map == &g_pipes);
    size_t i = ((const pkey *)key)->key[0];
    assert(i < 256);
    if (pending[i]) return PIPE_PENDING;
    return cached[i] || built[i] ? (void *)1 : NULL;
}
static void nvn_hm_put(nvn_hmap *map, const void *key, void *value) {
    assert(map == &g_pipes && value != (void *)1 && value != PIPE_PENDING);
    size_t i = ((const pkey *)key)->key[0];
    pending[i] = 0;
    built[i] = 1;
    atomic_fetch_add(&put_calls, 1);
}
static vkshader_t *vk_shader(uint64_t key, int stage) {
    (void)stage;
    if (missing_shader && key == 2) return NULL;
    static vkshader_t shader;
    shader.set = 0;
    shader.dsl = (VkDescriptorSetLayout)(uintptr_t)7;
    return &shader;
}
static VkPipelineLayout vk_pipeline_layout(VkDescriptorSetLayout *layouts, int count) {
    assert(count == 1 && layouts[0] == (VkDescriptorSetLayout)(uintptr_t)7);
    return (VkPipelineLayout)(uintptr_t)9;
}
static VkPipeline build_pipeline(const pkey *key, VkPipelineLayout layout, vkshader_t *const stages[3]) {
    assert(layout == (VkPipelineLayout)(uintptr_t)9 && stages[0]);
    size_t i = key->key[0];
    built[i] = 1;
    atomic_fetch_add(&build_calls, 1);
    return (VkPipeline)(uintptr_t)(i + 2);
}
static void vkDestroyPipeline(VkDevice device, VkPipeline pipeline, const VkAllocationCallbacks *callbacks) {
    assert(device == VK_NULL_HANDLE && pipeline != (VkPipeline)(uintptr_t)1 && !callbacks);
    atomic_fetch_add(&destroy_calls, 1);
}
#define VKLOG(...) ((void)0)
'''

PROBE = r'''
static void *worker(void *unused) { prewarm_thread(unused); return NULL; }
int main(int argc, char **argv) {
    assert(argc == 2);
    int mode = atoi(argv[1]);
    g_pw_n = mode == 2 || mode == 4 ? 1 : mode == 3 ? 128 : 4;
    g_pw = calloc(g_pw_n, sizeof *g_pw);
    assert(g_pw);
    for (size_t i = 0; i < g_pw_n; i++) g_pw[i].key[0] = i + 1;
    if (mode == 0) {
        for (size_t i = 0; i < g_pw_n; i++) cached[i + 1] = 1;
    } else if (mode == 1) {
        missing_shader = 1;
        g_pw[2].key[0] = 0;       // no vertex shader: rejected, but still complete
        g_pw[3].raster_discard = 1;
    } else if (mode == 2) {
        // build_pipeline fills built[], so the second lookup sees a duplicate winner.
    } else if (mode == 4) {
        pending[1] = 1;       // an async queue marker is not a completed pipeline
    }
    pthread_t threads[4];
    int count = mode == 3 ? 4 : 1;
    for (int i = 0; i < count; i++) assert(!pthread_create(&threads[i], NULL, worker, NULL));
    for (int i = 0; i < count; i++) assert(!pthread_join(threads[i], NULL));
    assert(g_pw_done == g_pw_n);
    if (mode == 0) {
        assert(atomic_load(&build_calls) == 0 && atomic_load(&put_calls) == 0);
    } else if (mode == 1) {
        assert(atomic_load(&build_calls) == 2 && atomic_load(&put_calls) == 2);
    } else if (mode == 2) {
        assert(atomic_load(&build_calls) == 1 && atomic_load(&put_calls) == 0);
        assert(atomic_load(&destroy_calls) == 1);
    } else if (mode == 4) {
        assert(atomic_load(&build_calls) == 1 && atomic_load(&put_calls) == 1);
        assert(atomic_load(&destroy_calls) == 0 && built[1] && !pending[1]);
    } else {
        assert(atomic_load(&build_calls) == 128 && atomic_load(&put_calls) == 128);
        for (size_t i = 0; i < g_pw_n; i++) assert(built[i + 1]);
    }
    free(g_pw);
    return 0;
}
'''


@unittest.skipUnless(shutil.which('cc') and os.name != 'nt', 'POSIX C compiler required')
class PrewarmProgress(unittest.TestCase):
    def check_mode(self, mode):
        source = unit(DM / 'android/gfx_vk_exec.c')
        progress = function(source, 'static void prewarm_progress(void) {', 'prewarm progress')
        worker = function(source, 'static void *prewarm_thread(void *arg) {', 'prewarm worker')
        code = STUBS + progress + worker + PROBE
        with tempfile.TemporaryDirectory(prefix='nx2a_prewarm_') as tmp:
            path = Path(tmp)
            (path / 'test.c').write_text(code, encoding='utf-8')
            subprocess.run([
                'cc', '-std=gnu11', '-Wall', '-Wextra', '-Werror', '-pthread',
                '-I' + str(DM / 'third_party/vulkan-headers/include'),
                str(path / 'test.c'), '-o', str(path / 'test'),
            ], check=True)
            subprocess.run([str(path / 'test'), str(mode)], check=True)

    def test_cached_records_complete_progress(self): self.check_mode(0)
    def test_rejected_records_complete_progress(self): self.check_mode(1)
    def test_duplicate_build_completes_progress(self): self.check_mode(2)
    def test_workers_complete_each_record_once(self): self.check_mode(3)
    def test_pending_pipeline_is_built_before_completion(self): self.check_mode(4)


class PrewarmSource(unittest.TestCase):
    def test_start_is_once_guarded(self):
        source = unit(DM / 'android/gfx_vk_exec.c')
        start = function(source, 'static void prewarm_start(void) {', 'prewarm start')
        self.assertIn('static pthread_once_t once = PTHREAD_ONCE_INIT;', start)
        self.assertIn('pthread_once(&once, prewarm_start_once);', start)

    def test_vulkan_init_is_once_guarded(self):
        source = (DM / 'android/gfx_vk_core.c').read_text(encoding='utf-8')
        init = function(source, 'void vk_init(void) {', 'Vulkan init')
        self.assertIn('static pthread_once_t once = PTHREAD_ONCE_INIT;', init)
        self.assertIn('pthread_once(&once, vk_init_once);', init)

    def test_worker_failure_does_not_wait_forever(self):
        source = unit(DM / 'android/gfx_vk_exec.c')
        start = function(source, 'static void prewarm_start_once(void) {', 'prewarm start once')
        self.assertIn('if (!pthread_create(&t, &a, prewarm_thread, NULL)) created++;', start)
        self.assertIn('created ? 1 : -1', start)

    def test_prewarm_does_not_duplicate_recorded_pipelines(self):
        source = unit(DM / 'android/gfx_vk_exec.c')
        worker = function(source, 'static void *prewarm_thread(void *arg) {', 'prewarm worker')
        self.assertNotIn('pipe_record(k)', worker)

    def test_status_waits_for_replay_and_never_starts_early(self):
        source = unit(DM / 'android/gfx_vk_exec.c')
        status = function(source, 'int vk_prewarm_status(int *done, int *total) {', 'prewarm status')
        self.assertIn('__ATOMIC_ACQUIRE', status)
        self.assertIn('started == 0 ? -2 : -1', status)
        self.assertNotIn('vk_prewarm_start', source)

    def test_ui_waits_for_replay_start(self):
        path = REPO / 'android/app/src/main/java/com/nx/android/game/GameActivity.kt'
        source = path.read_text(encoding='utf-8')
        wait = function(source, 'private fun beginPrewarmWait() {', 'prewarm wait')
        self.assertIn('if (s == -2L)', wait)
        self.assertNotIn('Native.prewarmStart()', wait)


if __name__ == '__main__':
    unittest.main()
