package com.divinedaily.ui

import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.lifecycle.viewmodel.compose.viewModel
import com.divinedaily.ui.theme.DivineDailyTheme

@Composable
fun DivineDailyApp() {
    val vm: MainViewModel = viewModel()
    DivineDailyTheme(version = vm.uiState.version) {
        Surface(modifier = Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) {
            MainScreen(vm = vm)
        }
    }
}
