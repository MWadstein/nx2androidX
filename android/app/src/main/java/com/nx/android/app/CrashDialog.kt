package com.nx.android.app

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.nx.android.R
import com.nx.android.core.ui.LocalAppLocale
import com.nx.android.core.ui.theme.NxPalette

/**
 * 闪退的那个游戏：标题 ID 与名字（从账本里读回的「上一次启动」是谁）。
 */
data class CrashReport(val titleId: String, val name: String, val detail: String = "")

/**
 * 游戏闪退后的弹框：三条路，从轻到重。
 *
 * 重新构建（重编运行库再进一次）→ 重新移植（回构建页）→ 反馈（去仓库的 issue）。
 * 弹框只负责把路摆出来，走哪条由玩家定。
 */
@Composable
fun CrashDialog(
    crash: CrashReport,
    canRebuild: Boolean,
    onRebuild: () -> Unit,
    onPortAgain: () -> Unit,
    onReport: () -> Unit,
    onClose: () -> Unit,
) {
    val locale = LocalAppLocale.current
    AlertDialog(
        onDismissRequest = onClose,
        // 小屏上平台默认的弹框宽度太窄：让它按可用宽度铺开、两侧留 16dp 边距；大屏上封顶 520dp
        modifier = Modifier.padding(horizontal = 16.dp).widthIn(max = 520.dp).fillMaxWidth(),
        title = {
            Text(locale.str(R.string.crash_title), fontWeight = FontWeight.Bold)
        },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text(locale.str(R.string.crash_text, crash.name),
                     style = MaterialTheme.typography.bodyMedium)
                // The host's own last words, when it wrote them: a crash marker or a driver fallback.
                // The full backtrace stays in the pack's log — this is what the player needs to know now.
                if (crash.detail.isNotBlank()) {
                    Text(crash.detail, fontFamily = FontFamily.Monospace, fontSize = 11.sp,
                        color = NxPalette.Danger)
                }
            }
        },
        confirmButton = {
            Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                TextButton(onClick = onRebuild, enabled = canRebuild) {
                    Text(locale.str(R.string.crash_rebuild), color = NxPalette.Building)
                }
                TextButton(onClick = onPortAgain) {
                    Text(locale.str(R.string.crash_port_again))
                }
            }
        },
        dismissButton = {
            TextButton(onClick = onReport) {
                Text(locale.str(R.string.crash_report))
            }
        },
    )
}
