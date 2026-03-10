import Foundation

final class FortuneService {
    private let client: HTTPClient

    init(client: HTTPClient) {
        self.client = client
    }

    func getTodayFortune() async throws -> DailyFortune {
        let dto: DailyFortuneDTO = try await client.request(
            path: "daily_fortune",
            method: "POST",
            body: nil,
            requiresAuth: true
        )
        return DailyFortune(dto: dto)
    }

    func getFortuneHistory(limit: Int = 30, skip: Int = 0) async throws -> [DailyFortune] {
        let dto: [DailyFortuneDTO] = try await client.request(
            path: "daily_fortune/history",
            method: "GET",
            body: nil,
            queryItems: [
                URLQueryItem(name: "limit", value: String(limit)),
                URLQueryItem(name: "skip", value: String(skip))
            ],
            requiresAuth: true
        )
        return dto.map(DailyFortune.init)
    }
}
