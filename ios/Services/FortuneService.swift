import Foundation

final class FortuneService {
    private let client: HTTPClient

    init(client: HTTPClient) {
        self.client = client
    }

    func generateToday(targetDate: String? = nil) async throws -> DailyFortuneInfoDTO {
        // Note: 这里直接拼 query（HTTPClient 已支持 path 内 query）
        let query = targetDate.map { "?target_date=\($0)" } ?? ""
        let path = "daily_fortune\(query)"

        let dto: DailyFortuneInfoDTO = try await client.request(
            path: path,
            method: "POST",
            body: nil,
            requiresAuth: true
        )
        return dto
    }

    func listHistory(skip: Int, limit: Int) async throws -> [DailyFortuneInfoDTO] {
        let path = "daily_fortune/history?skip=\(skip)&limit=\(limit)"
        let dtos: [DailyFortuneInfoDTO] = try await client.request(
            path: path,
            method: "GET",
            body: nil,
            requiresAuth: true
        )
        return dtos
    }
}

