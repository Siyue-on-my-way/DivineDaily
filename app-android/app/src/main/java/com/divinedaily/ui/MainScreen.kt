package com.divinedaily.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.ExposedDropdownMenuBox
import androidx.compose.material3.ExposedDropdownMenuDefaults
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.rememberTopAppBarState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.unit.dp
import com.divinedaily.domain.AppVersion
import com.divinedaily.domain.EventType
import com.divinedaily.domain.recommendedOrientation

@Composable
fun MainScreen(vm: MainViewModel) {
    val state = vm.uiState
    val scroll = rememberScrollState()

    Column(modifier = Modifier.fillMaxWidth()) {
        TopBar(
            version = state.version,
            onVersionChange = vm::setVersion,
            onReset = vm::reset
        )

        Column(
            modifier = Modifier
                .fillMaxWidth()
                .verticalScroll(scroll)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            InputCard(
                baseUrl = state.baseUrl,
                onBaseUrlChange = vm::setBaseUrl,
                question = state.question,
                onQuestionChange = vm::setQuestion,
                eventType = state.eventType,
                onEventTypeChange = vm::setEventType,
                version = state.version,
                onStart = vm::startDivination,
                enabled = !state.loading && !state.submittingFollowUp
            )

            OrientationCard(
                version = state.version,
                eventType = state.eventType
            )

            if (state.error != null) {
                Card(modifier = Modifier.fillMaxWidth()) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text(text = state.error)
                        Spacer(modifier = Modifier.height(8.dp))
                        TextButton(onClick = { vm.retryFetchResult() }) {
                            Text(text = if (state.version == AppVersion.CN) "重试" else "Retry")
                        }
                    }
                }
            }

            if (state.result != null) {
                ResultCard(
                    version = state.version,
                    result = state.result,
                    submittingFollowUp = state.submittingFollowUp,
                    onSubmitFollowUp = vm::submitFollowUp
                )
            } else if (state.loading) {
                Card(modifier = Modifier.fillMaxWidth()) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text(text = if (state.version == AppVersion.CN) "起卦中…" else "Divining…")
                    }
                }
            }
        }
    }

    LaunchedEffect(state.version, state.eventType) {
        vm.setOrientation(recommendedOrientation(state.version, state.eventType))
    }
}

@Composable
private fun OrientationCard(version: AppVersion, eventType: EventType) {
    val recommended = recommendedOrientation(version, eventType)
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(text = if (version == AppVersion.CN) "仪式感步骤" else "Ritual Step")
            Text(text = if (version == AppVersion.CN) "推荐朝向：$recommended" else "Recommended orientation: $recommended")
            CompassCard(version = version)
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun TopBar(version: AppVersion, onVersionChange: (AppVersion) -> Unit, onReset: () -> Unit) {
    TopAppBar(
        title = { Text(text = if (version == AppVersion.CN) "DivineDaily · 每日一卦" else "DivineDaily · Oracle") },
        actions = {
            TextButton(onClick = onReset) {
                Text(text = if (version == AppVersion.CN) "清空" else "Reset")
            }
        },
        scrollBehavior = androidx.compose.material3.TopAppBarDefaults.pinnedScrollBehavior(rememberTopAppBarState())
    )
    VersionSwitcher(version = version, onVersionChange = onVersionChange)
    HorizontalDivider()
}

@Composable
private fun VersionSwitcher(version: AppVersion, onVersionChange: (AppVersion) -> Unit) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(text = if (version == AppVersion.CN) "版本" else "Version")
        Spacer(modifier = Modifier.width(12.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(onClick = { onVersionChange(AppVersion.CN) }, enabled = version != AppVersion.CN) {
                Text(text = "CN")
            }
            Button(onClick = { onVersionChange(AppVersion.Global) }, enabled = version != AppVersion.Global) {
                Text(text = "Global")
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun InputCard(
    baseUrl: String,
    onBaseUrlChange: (String) -> Unit,
    question: String,
    onQuestionChange: (String) -> Unit,
    eventType: EventType,
    onEventTypeChange: (EventType) -> Unit,
    version: AppVersion,
    onStart: () -> Unit,
    enabled: Boolean
) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
            var expanded by remember { mutableStateOf(false) }

            Text(text = if (version == AppVersion.CN) "后端地址" else "API Base URL")
            OutlinedTextField(
                value = baseUrl,
                onValueChange = onBaseUrlChange,
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
                keyboardOptions = KeyboardOptions(imeAction = ImeAction.Next),
                placeholder = { Text(text = "http://<host>:8080/") }
            )

            Text(text = if (version == AppVersion.CN) "所求之事" else "Topic")
            ExposedDropdownMenuBox(expanded = expanded, onExpandedChange = { expanded = it }) {
                OutlinedTextField(
                    value = when (eventType) {
                        EventType.Decision -> if (version == AppVersion.CN) "决策" else "Decision"
                        EventType.Relationship -> if (version == AppVersion.CN) "感情" else "Relationship"
                        EventType.Career -> if (version == AppVersion.CN) "事业" else "Career"
                    },
                    onValueChange = {},
                    modifier = Modifier
                        .menuAnchor()
                        .fillMaxWidth(),
                    readOnly = true,
                    trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = expanded) }
                )
                ExposedDropdownMenu(expanded = expanded, onDismissRequest = { expanded = false }) {
                    DropdownMenuItem(
                        text = { Text(text = if (version == AppVersion.CN) "决策 (做不做/选哪个)" else "Decision (Yes/No)") },
                        onClick = {
                            onEventTypeChange(EventType.Decision)
                            expanded = false
                        }
                    )
                    DropdownMenuItem(
                        text = { Text(text = if (version == AppVersion.CN) "感情 (缘分/关系)" else "Relationship") },
                        onClick = {
                            onEventTypeChange(EventType.Relationship)
                            expanded = false
                        }
                    )
                    DropdownMenuItem(
                        text = { Text(text = if (version == AppVersion.CN) "事业 (工作/学业)" else "Career") },
                        onClick = {
                            onEventTypeChange(EventType.Career)
                            expanded = false
                        }
                    )
                }
            }

            Text(text = if (version == AppVersion.CN) "心中疑惑" else "Your Question")
            OutlinedTextField(
                value = question,
                onValueChange = onQuestionChange,
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
                keyboardOptions = KeyboardOptions(imeAction = ImeAction.Done),
                placeholder = { Text(text = if (version == AppVersion.CN) "请诚心默念您的问题…" else "What is on your mind?") }
            )

            Button(onClick = onStart, enabled = enabled && question.trim().isNotEmpty(), modifier = Modifier.fillMaxWidth()) {
                Text(text = if (version == AppVersion.CN) "诚心起卦" else "Reveal Fate")
            }
        }
    }
}
