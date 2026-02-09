package com.divinedaily.ui.theme

import androidx.compose.material3.ColorScheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import com.divinedaily.domain.AppVersion

private val CnLight: ColorScheme = lightColorScheme(
    primary = Color(0xFFB33A3A),
    secondary = Color(0xFF5C6BC0),
    background = Color(0xFFFFFBF5),
    surface = Color(0xFFFFFFFF)
)

private val GlobalLight: ColorScheme = lightColorScheme(
    primary = Color(0xFF5E35B1),
    secondary = Color(0xFF00897B),
    background = Color(0xFF0E0B16),
    surface = Color(0xFF1A1526),
    onBackground = Color(0xFFEDE7F6),
    onSurface = Color(0xFFEDE7F6)
)

private val GlobalDark: ColorScheme = darkColorScheme(
    primary = Color(0xFFB39DDB),
    secondary = Color(0xFF80CBC4),
    background = Color(0xFF0E0B16),
    surface = Color(0xFF1A1526)
)

@Composable
fun DivineDailyTheme(version: AppVersion, content: @Composable () -> Unit) {
    val scheme = when (version) {
        AppVersion.CN -> CnLight
        AppVersion.Global -> GlobalDark
    }
    MaterialTheme(colorScheme = scheme, content = content)
}

