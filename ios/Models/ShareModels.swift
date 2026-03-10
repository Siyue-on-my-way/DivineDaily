import Foundation

struct ShareCreateRequest: Encodable {
    let expires_days: Int?
    let is_public: Bool
}

struct ShareResponseDTO: Decodable {
    let share_token: String
    let share_url: String
    let created_at: String
    let expires_at: String?
}

struct ShareResponse: Equatable {
    let token: String
    let url: String
    let createdAt: String
    let expiresAt: String?

    init(dto: ShareResponseDTO) {
        self.token = dto.share_token
        self.url = dto.share_url
        self.createdAt = dto.created_at
        self.expiresAt = dto.expires_at
    }
}

struct ShareStatsDTO: Decodable {
    let total_shares: Int
    let total_views: Int
    let shares: [ShareItemDTO]
}

struct ShareItemDTO: Decodable {
    let share_token: String
    let share_url: String
    let view_count: Int
    let created_at: String
    let expires_at: String?
    let is_expired: Bool
}

struct ShareStats: Equatable {
    let totalShares: Int
    let totalViews: Int
    let shares: [ShareItem]

    init(dto: ShareStatsDTO) {
        self.totalShares = dto.total_shares
        self.totalViews = dto.total_views
        self.shares = dto.shares.map(ShareItem.init)
    }
}

struct ShareItem: Equatable, Identifiable {
    let id: String
    let token: String
    let url: String
    let viewCount: Int
    let createdAt: String
    let expiresAt: String?
    let isExpired: Bool

    init(dto: ShareItemDTO) {
        self.id = dto.share_token
        self.token = dto.share_token
        self.url = dto.share_url
        self.viewCount = dto.view_count
        self.createdAt = dto.created_at
        self.expiresAt = dto.expires_at
        self.isExpired = dto.is_expired
    }
}
