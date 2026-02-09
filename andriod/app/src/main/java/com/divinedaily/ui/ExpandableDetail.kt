package com.divinedaily.ui

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Card
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.divinedaily.domain.AppVersion

@Composable
fun ExpandableDetail(version: AppVersion, detail: String) {
    var expanded by remember { mutableStateOf(false) }
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(modifier = Modifier.padding(12.dp)) {
            TextButton(onClick = { expanded = !expanded }) {
                Text(text = if (expanded) {
                    if (version == AppVersion.CN) "收起详细报告" else "Hide Full Report"
                } else {
                    if (version == AppVersion.CN) "查看详细报告" else "View Full Report"
                })
            }
            if (expanded) {
                Text(text = detail)
            }
        }
    }
}

