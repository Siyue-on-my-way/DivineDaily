import Foundation

final class InsightsService {
    private let client: HTTPClient

    init(client: HTTPClient) {
        self.client = client
    }

    func getOverview() async throws -> InsightsOverview {
        let dto: InsightsOverviewDTO = try await client.request(
            path: "insights/overview",
            method: "GET",
            body: nil,
            requiresAuth: true
        )
        return InsightsOverview(dto: dto)
    }

    func getTypeDistribution() async throws -> [InsightsTypeDistributionItem] {
        let dto: InsightsTypeDistributionResponseDTO = try await client.request(
            path: "insights/type-distribution",
            method: "GET",
            body: nil,
            requiresAuth: true
        )
        return (dto.distribution ?? []).map(InsightsTypeDistributionItem.init)
    }

    func getRecommendations() async throws -> [InsightsRecommendationItem] {
        let dto: InsightsRecommendationsResponseDTO = try await client.request(
            path: "insights/recommendations",
            method: "GET",
            body: nil,
            requiresAuth: true
        )
        return (dto.recommendations ?? []).map(InsightsRecommendationItem.init)
    }
}
