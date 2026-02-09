package com.divinedaily.domain

enum class AppVersion(val apiValue: String) {
    CN("CN"),
    Global("Global")
}

enum class EventType(val apiValue: String) {
    Decision("decision"),
    Relationship("relationship"),
    Career("career")
}

fun recommendedOrientation(version: AppVersion, eventType: EventType): String {
    return when (version) {
        AppVersion.CN -> when (eventType) {
            EventType.Decision -> "East (震)"
            EventType.Career -> "South (离)"
            EventType.Relationship -> "East (震)"
        }
        AppVersion.Global -> when (eventType) {
            EventType.Decision -> "East (Air)"
            EventType.Career -> "South (Fire)"
            EventType.Relationship -> "North (Earth)"
        }
    }
}

