import Foundation

final class ShareService {
    private let client: HTTPClient

    init(client: HTTPClient) {
        self.client = client
    }

    func createShare(sessionId: String, expiresDays: Int? = 7, isPublic: Bool = true) async throws -> ShareResponse {
        let body = ShareCreateRequest(expires_days: expiresDays, is_public: isPublic)
        let dto: ShareResponseDTO = try await client.request(
            path: "shares/\(sessionId)/share",
            method: "POST",
            body: body,
            requiresAuth: true
        )
        return ShareResponse(dto: dto)
    }

    func getShareStats(sessionId: String) async throws -> ShareStats {
        let dto: ShareStatsDTO = try await client.request(
            path: "shares/session/\(sessionId)/stats",
            method: "GET",
            body: nil,
            requiresAuth: true
        )
        return ShareStats(dto: dto)
    }

    func deleteShare(shareToken: String) async throws {
        _ = try await client.requestVoid(
            path: "shares/\(shareToken)",
            method: "DELETE",
            body: nil,
            requiresAuth: true
        )
    }
}
