import Foundation

final class ShareService {
    private let client: HTTPClient

    init(client: HTTPClient) {
        self.client = client
    }

    func createShare(sessionId: String, expiresDays: Int?, isPublic: Bool) async throws -> ShareCreateResponse {
        struct ShareCreateRequest: Encodable {
            let expires_days: Int?
            let is_public: Bool
        }

        let request = ShareCreateRequest(expires_days: expiresDays, is_public: isPublic)

        let dto: ShareCreateResponseDTO = try await client.request(
            path: "shares/\(sessionId)/share",
            method: "POST",
            body: request,
            requiresAuth: true
        )

        return ShareCreateResponse(dto: dto)
    }

    /// 公开接口：无需登录
    func fetchShareContent(shareToken: String) async throws -> ShareContentResponseDTO {
        try await client.request(
            path: "shares/\(shareToken)",
            method: "GET",
            body: nil,
            requiresAuth: false
        )
    }

    /// 登录接口：获取某个会话的分享统计
    func fetchShareStats(sessionId: String) async throws -> ShareStatsResponse {
        let dto: ShareStatsResponseDTO = try await client.request(
            path: "shares/session/\(sessionId)/stats",
            method: "GET",
            body: nil,
            requiresAuth: true
        )
        return ShareStatsResponse(dto: dto)
    }
}

