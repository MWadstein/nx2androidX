package com.nx.android.data

import com.nx.android.data.drivers.Drivers
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.io.File
import java.util.zip.ZipEntry
import java.util.zip.ZipOutputStream

/** The driver's own metadata: what it says about itself, and the folder it gets */
class DriversTest {

    @Test
    fun `the metadata says the name, the version and the library`() {
        val meta = Drivers.parseMeta(
            """{"schemaVersion":1,"name":"Turnip Gen8 V39","description":"Turnip A8xx Android/Bionic",
               "author":"StevenMXZ","packageVersion":"34","vendor":"Mesa","driverVersion":"Vulkan 1.4.367",
               "minApi":28,"libraryName":"libvulkan_freedreno.so"}""")
        assertEquals("Turnip Gen8 V39", meta?.name)
        assertEquals("Vulkan 1.4.367", meta?.version)
        assertEquals("Mesa", meta?.vendor)
        assertEquals("libvulkan_freedreno.so", meta?.library)
    }

    @Test
    fun `a metadata without a name or without a library is no metadata`() {
        assertNull(Drivers.parseMeta("""{"libraryName":"libvulkan_freedreno.so"}"""))
        assertNull(Drivers.parseMeta("""{"name":"Turnip Gen8 V39"}"""))
        assertNull(Drivers.parseMeta("not json at all"))
    }

    @Test
    fun `the folder name comes from the driver's own name`() {
        assertEquals("Turnip_Gen8_V39", Drivers.idOf("Turnip Gen8 V39"))
        assertEquals("Turnip_27.0.0-R2", Drivers.idOf("Turnip 27.0.0-R2"))
        // two builds whose names differ only in punctuation stay two folders
        assertEquals("Turnip_Gen8_V39-patched", Drivers.idOf("Turnip Gen8 V39-patched"))
        assertEquals("Turnip_Gen8_V39", Drivers.idOf("Turnip Gen8 V39"))
    }

    @Test
    fun `an archive is unpacked into a folder of its own`() {
        val stage = File.createTempFile("nx2a-driver", "").let { it.delete(); it.mkdirs(); it }
        try {
            val meta = Drivers.unpack(ByteArrayInputStream(archive("meta.json" to META_JSON, "libvulkan_freedreno.so" to "DRV")),
                stage)
            assertEquals("Turnip Gen8 V39", meta.name)
            assertEquals("Vulkan 1.4.367", meta.version)
            assertEquals("libvulkan_freedreno.so", meta.library)
            assertTrue(File(stage, "libvulkan_freedreno.so").isFile)
            assertTrue(File(stage, "meta.json").isFile)
            assertEquals("Turnip_Gen8_V39", Drivers.idOf(meta.name))
        } finally {
            stage.deleteRecursively()
        }
    }

    @Test
    fun `an ELF for this device is accepted but a wrong-ABI or fake library is refused`() {
        val arm64 = arrayOf("arm64-v8a")
        val good = elf("libvulkan_freedreno.so", cls = 2, machine = 183)
        val otherCpu = elf("libvulkan_freedreno.so", cls = 2, machine = 62)
        val notElf = File.createTempFile("nx2a-no-elf", ".so").apply { writeText("not a driver") }
        val wrongName = elf("libvulkan_freedreno.txt", cls = 2, machine = 183)
        try {
            assertNull(Drivers.validateLibrary(good, arm64))
            assertEquals(Drivers.Refusal.WRONG_ABI, Drivers.validateLibrary(otherCpu, arm64))
            assertEquals(Drivers.Refusal.BAD_ELF, Drivers.validateLibrary(notElf, arm64))
            assertEquals(Drivers.Refusal.NOT_A_DRIVER, Drivers.validateLibrary(wrongName, arm64))
            // with no ABI list (JVM tests that write placeholder libraries) the machine check is skipped
            assertNull(Drivers.validateLibrary(otherCpu, emptyArray()))
        } finally {
            good.parentFile?.deleteRecursively()
            otherCpu.parentFile?.deleteRecursively()
            wrongName.parentFile?.deleteRecursively()
            notElf.delete()
        }
    }

    @Test
    fun `an archive without a driver is refused`() {
        val stage = File.createTempFile("nx2a-driver", "").let { it.delete(); it.mkdirs(); it }
        try {
            val e = runCatching { Drivers.unpack(ByteArrayInputStream(archive("readme.txt" to "no driver here")), stage) }
            assertTrue(e.isFailure)
        } finally {
            stage.deleteRecursively()
        }
    }

    /** A file with a real ELF header (and enough bytes to be more than a placeholder). */
    private fun elf(name: String, cls: Int, machine: Int): File {
        val dir = java.nio.file.Files.createTempDirectory("nx2a-elf").toFile()
        val f = File(dir, name)
        val head = ByteArray(20)
        head[0] = 0x7F.toByte(); head[1] = 'E'.code.toByte(); head[2] = 'L'.code.toByte(); head[3] = 'F'.code.toByte()
        head[4] = cls.toByte(); head[5] = 1
        head[18] = (machine and 0xFF).toByte(); head[19] = (machine shr 8).toByte()
        java.io.RandomAccessFile(f, "rw").use { it.write(head); it.setLength(8192) }
        return f
    }

    private fun archive(vararg entries: Pair<String, String>): ByteArray {
        val out = ByteArrayOutputStream()
        ZipOutputStream(out).use { z ->
            for ((name, body) in entries) {
                z.putNextEntry(ZipEntry(name)); z.write(body.toByteArray()); z.closeEntry()
            }
        }
        return out.toByteArray()
    }

    private companion object {
        const val META_JSON = """{"schemaVersion":1,"name":"Turnip Gen8 V39","vendor":"Mesa",""" +
            """"driverVersion":"Vulkan 1.4.367","minApi":28,"libraryName":"libvulkan_freedreno.so"}"""
    }
}
