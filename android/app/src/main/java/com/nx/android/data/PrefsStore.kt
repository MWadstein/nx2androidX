package com.nx.android.data

import android.content.Context
import android.content.SharedPreferences
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import dagger.hilt.android.qualifiers.ApplicationContext
import javax.inject.Inject
import javax.inject.Singleton
import org.json.JSONArray
import org.json.JSONObject

/**
 * The tool's saved settings: every key in one place, and the path the whole UI reads (the keys file) as
 * observable state — a write goes to disk at once, a read is a Compose read. The key names and their meanings
 * are the old app's, unchanged: an update keeps its settings.
 */
@Singleton
class PrefsStore private constructor(
    @ApplicationContext private val ctx: Context,
    private val file: String,
) {

    /** Hilt's one instance: the app's own settings file ([NAME]), written by the main process. */
    @Inject
    constructor(@ApplicationContext ctx: Context) : this(ctx, NAME)

    companion object {
        // the prefs file's name (the app's own settings, one file)
        const val NAME = "nx2a"
        // the game page's own file: only the `:play` process writes it (see [game])
        const val GAME_NAME = "nx2a.game"

        /**
         * The game page's store (the `:play` process). SharedPreferences is not safe across processes: each
         * process keeps its own copy of a file, and the main process's next write (the library's scan, the
         * port history, the last launch) rewrites the whole file from its stale copy, dropping what the game
         * page just wrote - the drawer's settings then read back as they were before the change.
         *
         * So the game page writes a file of its own, which no other process ever writes. Reads fall back to
         * [NAME]: the keys an older version saved there are still seen, and the next change saves them here.
         * Writes commit, because the game ends by killing its process and a queued apply() dies with it.
         */
        fun game(ctx: Context) = PrefsStore(ctx, GAME_NAME)
        // the old app's key, unchanged
        const val KEYS = "keys"
        // the imported firmware package (a zip): its file name; the unpacked copy is in the app's own folder
        const val FIRMWARE = "firmware"
        // the old app's global port options: a game without its own config keeps them as the defaults
        const val LEGACY_TOUCH = "touch"
        const val LEGACY_FPS60 = "fps60"
        const val LEGACY_EXPERIMENTAL = "experimental"
        // the app's own language: "" follows the phone, "zh" and "en" are the player's own choice
        const val LANG = "lang"
        // the library's memory
        const val LIB_CONFIGS = "lib.configs"
        const val LIB_PORTS = "lib.ports"
        // title ID → the data pack's path the last time it was seen (for the storage page's "out of reach")
        const val LIB_PACKS = "lib.packs"
        // title ID → the source file the game was last built from (for the rebuild button)
        const val LIB_SOURCES = "lib.sources"
        // the imported packs: the folder's path → the game it holds (the path is its identity)
        const val LIB_IMPORTED = "lib.imported"
        const val LIB_MEMORIES_MIGRATED = "lib.memories.migrated"
        // the guided setup
        const val OB_STEP = "ob.step"
        const val OB_LATER = "ob.later"
        const val OB_COMPLETED = "ob.completed"
        // the open-source notice: the player has seen it (once is enough)
        const val OSS_NOTICE_SHOWN = "oss.notice.shown"
        // the port: the interruption marker and the history
        const val PORT_RUNNING = "port.running"
        const val PLAYER_LAST_START = "player.lastStart"
        // the running game's identity: the ledger reads it back on a cold start (PLAYER_LAST_START is
        // the crash detection's own marker and is not touched by the ledger)
        const val PLAYER_TITLE_ID = "player.titleId"
        const val PLAYER_NAME = "player.name"
        const val PORT_STARTED_AT = "port.startedAt"
        const val PORT_HISTORY = "port.history"
        const val PORT_COMPLETED = "port.completed"
        // the performance HUD: the two lines and what the performance one shows
        const val HUD_STATS = "hud.stats"
        const val HUD_DEVICE = "hud.device"
        const val HUD_FIELDS = "hud.fields"
        const val HUD_TEMP_F = "hud.temp.f"
        // the external display: the game goes to a wired display and the phone becomes the gamepad
        const val EXTERNAL_DISPLAY = "display.external"
        // the file provider: the app's own folders are handed to the file managers (on by default)
        const val FILE_PROVIDER = "file.provider"
        // the assistant's in-game entry: the slim handle on the game screen's right edge (on by default)
        const val AGENT_BADGE = "agent.badge"
        // the single save root: blank means the app's own files/save, otherwise a chosen folder
        const val SAVE_ROOT = "save.root"
    }

    val prefs: SharedPreferences = ctx.getSharedPreferences(file, Context.MODE_PRIVATE)

    /** The main process's file: only the game page's store falls back to it (older versions wrote there) */
    private val legacy: SharedPreferences? =
        if (file == NAME) null else ctx.getSharedPreferences(NAME, Context.MODE_PRIVATE)

    /** prod.keys 的路径：库的发起前提、设置页、引导都读它；picker 与引导写它（一份，就是这一个） */
    var keys by mutableStateOf(str(KEYS))
        private set

    fun writeKeys(path: String) {
        keys = path.trim()
        write { putString(KEYS, keys) }
    }

    /** The chosen save folder, or "" for the app's internal default. A Compose read. */
    var saveRoot by mutableStateOf(str(SAVE_ROOT))
        private set

    fun writeSaveRoot(path: String) {
        val value = path.trim().trimEnd('/')
        saveRoot = value
        write { putString(SAVE_ROOT, value) }
    }

    fun clearSaveRoot() {
        saveRoot = ""
        write { remove(SAVE_ROOT) }
    }

    // ---- 通用读写（引导与库的记忆；键名见常量） ----

    fun str(key: String, def: String = ""): String =
        prefs.getString(key, null) ?: legacy?.getString(key, null) ?: def

    fun bool(key: String, def: Boolean = false): Boolean = when {
        prefs.contains(key) -> prefs.getBoolean(key, def)
        legacy?.contains(key) == true -> legacy.getBoolean(key, def)
        else -> def
    }

    /**
     * 写一次。[NAME] 走 apply()（主进程活在玩家的操作里，写盘不必挡路）；游戏页的文件当场 commit()——
     * 游戏结束就是结束进程，排队的写来不及落盘。
     */
    private fun write(change: SharedPreferences.Editor.() -> Unit) {
        val edit = prefs.edit()
        edit.change()
        if (file == NAME) edit.apply() else edit.commit()
    }

    fun put(key: String, value: String?) = write { putString(key, value) }

    fun put(key: String, value: Boolean) = write { putBoolean(key, value) }

    // ---- JSON（历史、按游戏配置、产物映射） ----

    fun json(key: String): JSONObject = try {
        JSONObject(str(key, "{}"))
    } catch (e: Exception) {
        JSONObject()
    }

    fun putJson(key: String, o: JSONObject) = write { putString(key, o.toString()) }

    fun array(key: String): JSONArray = try {
        JSONArray(str(key, "[]"))
    } catch (e: Exception) {
        JSONArray()
    }

    fun putArray(key: String, a: JSONArray) = write { putString(key, a.toString()) }
}
