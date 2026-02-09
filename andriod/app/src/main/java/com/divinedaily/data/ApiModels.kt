package com.divinedaily.data

import com.squareup.moshi.Json

data class CreateDivinationRequest(
    @Json(name = "user_id") val userId: String,
    val question: String,
    @Json(name = "event_type") val eventType: String,
    val version: String,
    val orientation: String
)

data class DivinationSession(
    val id: String,
    @Json(name = "user_id") val userId: String,
    val version: String,
    val question: String,
    @Json(name = "event_type") val eventType: String,
    val orientation: String?,
    @Json(name = "follow_up_count") val followUpCount: Int?
)

data class SceneAdviceItem(
    val title: String,
    val content: String,
    val type: String
)

data class FollowUpQuestion(
    val id: String,
    @Json(name = "session_id") val sessionId: String,
    val question: String,
    val options: List<String>?
)

data class DivinationResult(
    @Json(name = "session_id") val sessionId: String,
    val summary: String,
    val detail: String,
    @Json(name = "scene_advice") val sceneAdvice: List<SceneAdviceItem>?,
    @Json(name = "needs_follow_up") val needsFollowUp: Boolean,
    @Json(name = "follow_up_question") val followUpQuestion: FollowUpQuestion?
)

data class FollowUpAnswer(
    @Json(name = "session_id") val sessionId: String,
    @Json(name = "question_id") val questionId: String,
    val answer: String
)

