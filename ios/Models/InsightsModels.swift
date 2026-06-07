import Foundation

struct InsightsOverviewDTO: Decodable {
    let totalDivinations: Int?
    let thisWeekDivinations: Int?
    let avgQualityScore: Double?
    let mostCommonType: String?
    let successRate: Double?
    let qualityTrend: String?

    private enum CodingKeys: String, CodingKey {
        case totalDivinations = "total_divinations"
        case thisWeekDivinations = "this_week_divinations"
        case avgQualityScore = "avg_quality_score"
        case mostCommonType = "most_common_type"
        case successRate = "success_rate"
        case qualityTrend = "quality_trend"
    }
}

struct InsightsTypeDistributionItemDTO: Decodable {
    let type: String?
    let count: Int?
    let percentage: Double?
}

struct InsightsTypeDistributionResponseDTO: Decodable {
    let total: Int?
    let distribution: [InsightsTypeDistributionItemDTO]?
}

struct InsightsRecommendationItemDTO: Decodable {
    let title: String?
    let content: String?
    let priority: String?
}

struct InsightsRecommendationsResponseDTO: Decodable {
    let recommendations: [InsightsRecommendationItemDTO]?
}

struct InsightsOverview: Equatable {
    let totalDivinations: Int
    let thisWeekDivinations: Int
    let avgQualityScore: Double
    let mostCommonType: String
    let successRate: Double
    let qualityTrend: String

    init(dto: InsightsOverviewDTO) {
        totalDivinations = dto.totalDivinations ?? 0
        thisWeekDivinations = dto.thisWeekDivinations ?? 0
        avgQualityScore = dto.avgQualityScore ?? 0
        mostCommonType = dto.mostCommonType ?? "-"
        successRate = dto.successRate ?? 0
        qualityTrend = dto.qualityTrend ?? "stable"
    }
}

struct InsightsTypeDistributionItem: Equatable, Identifiable {
    let id = UUID()
    let type: String
    let count: Int
    let percentage: Double

    init(dto: InsightsTypeDistributionItemDTO) {
        type = dto.type ?? "other"
        count = dto.count ?? 0
        percentage = dto.percentage ?? 0
    }
}

struct InsightsRecommendationItem: Equatable, Identifiable {
    let id = UUID()
    let title: String
    let content: String
    let priority: String

    init(dto: InsightsRecommendationItemDTO) {
        title = dto.title ?? "建议"
        content = dto.content ?? ""
        priority = dto.priority ?? "normal"
    }
}
