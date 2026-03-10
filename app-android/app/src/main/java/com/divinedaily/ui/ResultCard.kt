package com.divinedaily.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.weight
import androidx.compose.foundation.layout.width
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.divinedaily.data.DivinationResult
import com.divinedaily.domain.AppVersion

@Composable
fun ResultCard(
    version: AppVersion,
    result: DivinationResult,
    submittingFollowUp: Boolean,
    onSubmitFollowUp: (String) -> Unit
) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Text(text = if (version == AppVersion.CN) "卦象解读" else "Oracle Insight")
            Text(text = result.summary)

            val advice = result.sceneAdvice.orEmpty()
            if (advice.isNotEmpty()) {
                Text(text = if (version == AppVersion.CN) "生活锦囊" else "Actionable Advice")
                advice.forEach { item ->
                    Card(modifier = Modifier.fillMaxWidth()) {
                        Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                            Text(text = item.title)
                            Text(text = item.content)
                        }
                    }
                }
            }

            if (result.needsFollowUp && result.followUpQuestion != null) {
                Text(text = if (version == AppVersion.CN) "进一步探索" else "Deeper Insight Needed")
                Text(text = result.followUpQuestion.question)

                val options = result.followUpQuestion.options
                if (!options.isNullOrEmpty()) {
                    options.chunked(2).forEach { row ->
                        Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.fillMaxWidth()) {
                            row.forEach { opt ->
                                Button(
                                    onClick = { onSubmitFollowUp(opt) },
                                    enabled = !submittingFollowUp,
                                    modifier = Modifier.weight(1f)
                                ) {
                                    Text(text = opt)
                                }
                            }
                            if (row.size == 1) {
                                Spacer(modifier = Modifier.weight(1f))
                            }
                        }
                    }
                } else {
                    var answer by remember { mutableStateOf("") }
                    Row(modifier = Modifier.fillMaxWidth()) {
                        OutlinedTextField(
                            value = answer,
                            onValueChange = { answer = it },
                            modifier = Modifier.weight(1f),
                            placeholder = { Text(text = if (version == AppVersion.CN) "请输入…" else "Your answer…") }
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Button(onClick = { onSubmitFollowUp(answer) }, enabled = !submittingFollowUp && answer.isNotBlank()) {
                            Text(text = if (version == AppVersion.CN) "提交" else "Submit")
                        }
                    }
                }
                if (submittingFollowUp) {
                    Text(text = if (version == AppVersion.CN) "思考中…" else "Thinking…")
                }
            }

            ExpandableDetail(version = version, detail = result.detail)
        }
    }
}
