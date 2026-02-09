package com.divinedaily.ui

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.divinedaily.BuildConfig
import com.divinedaily.data.CreateDivinationRequest
import com.divinedaily.data.DivinationResult
import com.divinedaily.data.FollowUpAnswer
import com.divinedaily.data.Network
import com.divinedaily.domain.AppVersion
import com.divinedaily.domain.EventType
import com.divinedaily.domain.recommendedOrientation
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

data class UiState(
    val version: AppVersion = AppVersion.CN,
    val eventType: EventType = EventType.Decision,
    val question: String = "",
    val orientation: String = recommendedOrientation(AppVersion.CN, EventType.Decision),
    val baseUrl: String = BuildConfig.API_BASE_URL,
    val loading: Boolean = false,
    val submittingFollowUp: Boolean = false,
    val result: DivinationResult? = null,
    val lastSessionId: String? = null,
    val error: String? = null
)

class MainViewModel : ViewModel() {
    var uiState: UiState by mutableStateOf(UiState())
        private set

    fun setVersion(v: AppVersion) {
        uiState = uiState.copy(version = v, error = null)
        setOrientation(recommendedOrientation(uiState.version, uiState.eventType))
    }

    fun setEventType(t: EventType) {
        uiState = uiState.copy(eventType = t, error = null)
        setOrientation(recommendedOrientation(uiState.version, uiState.eventType))
    }

    fun setQuestion(q: String) {
        uiState = uiState.copy(question = q, error = null)
    }

    fun setOrientation(o: String) {
        uiState = uiState.copy(orientation = o)
    }

    fun setBaseUrl(url: String) {
        uiState = uiState.copy(baseUrl = url.trim(), error = null)
    }

    fun reset() {
        uiState = UiState(version = uiState.version)
    }

    fun startDivination() {
        val question = uiState.question.trim()
        if (question.isEmpty()) return

        viewModelScope.launch {
            uiState = uiState.copy(loading = true, submittingFollowUp = false, result = null, error = null)
            try {
                val session = Network.api(uiState.baseUrl).startDivination(
                    CreateDivinationRequest(
                        userId = "android_guest",
                        question = question,
                        eventType = uiState.eventType.apiValue,
                        version = uiState.version.apiValue,
                        orientation = uiState.orientation
                    )
                )
                uiState = uiState.copy(lastSessionId = session.id)
                delay(800)
                fetchResult(session.id)
            } catch (t: Throwable) {
                uiState = uiState.copy(loading = false, error = t.message ?: "Failed to start")
            }
        }
    }

    fun retryFetchResult() {
        val sessionId = uiState.lastSessionId ?: return
        viewModelScope.launch {
            fetchResult(sessionId)
        }
    }

    fun submitFollowUp(answer: String) {
        val result = uiState.result ?: return
        val q = result.followUpQuestion ?: return
        val trimmed = answer.trim()
        if (trimmed.isEmpty()) return

        viewModelScope.launch {
            uiState = uiState.copy(submittingFollowUp = true, error = null)
            try {
                Network.api(uiState.baseUrl).submitFollowUp(
                    FollowUpAnswer(sessionId = result.sessionId, questionId = q.id, answer = trimmed)
                )
                delay(600)
                fetchResult(result.sessionId)
            } catch (t: Throwable) {
                uiState = uiState.copy(submittingFollowUp = false, error = t.message ?: "Failed to submit")
            }
        }
    }

    private suspend fun fetchResult(sessionId: String) {
        try {
            val res = Network.api(uiState.baseUrl).getResult(sessionId)
            uiState = uiState.copy(loading = false, submittingFollowUp = false, result = res, error = null)
        } catch (t: Throwable) {
            uiState = uiState.copy(loading = false, submittingFollowUp = false, error = t.message ?: "Failed to fetch result")
        }
    }
}
