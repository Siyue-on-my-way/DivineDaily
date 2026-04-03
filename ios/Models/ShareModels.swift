import Foundation

// MARK: - 创建分享

struct ShareCreateResponseDTO: Decodable {
    let share_token: String?
    let share_url: String
    let created_at: String?
    let expires_at: String?
}

struct ShareCreateResponse: Equatable {
    let token: String?
    let url: String

    init(dto: ShareCreateResponseDTO) {
        self.token = dto.share_token
        self.url = dto.share_url
    }
}

// MARK: - 分享落地页（公开，无需登录）

struct ShareMetadataDTO: Decodable {
    let created_at: String?
    let view_count: Int?
    let is_expired: Bool?
}

/// 与后端 `ShareContentResponse.result` 对齐
struct ShareResultPayloadDTO: Decodable {
    let title: String?
    let outcome: String?
    let summary: String?
    let detail: String?
    let hexagram_info: HexagramInfoDTO?
    let cards: [TarotCardDTO]?
    let daily_fortune: DailyFortuneEmbeddedDTO?
}

struct ShareContentResponseDTO: Decodable {
    let share_token: String
    let question: String
    let result: ShareResultPayloadDTO
    let metadata: ShareMetadataDTO?
}

// MARK: - 分享统计（登录）

struct ShareStatsItemDTO: Decodable {
    let share_token: String?
    let share_url: String?
    let view_count: Int?
    let created_at: String?
    let expires_at: String?
    let is_expired: Bool?
}

struct ShareStatsResponseDTO: Decodable {
    let total_shares: Int?
    let total_views: Int?
    let shares: [ShareStatsItemDTO]?
}

struct ShareStatsItem: Equatable, Identifiable {
    let id: String
    let token: String
    let url: String
    let viewCount: Int
    let createdAt: String
    let expiresAt: String?
    let isExpired: Bool

    init(dto: ShareStatsItemDTO) {
        self.token = dto.share_token ?? ""
        self.id = token
        self.url = dto.share_url ?? ""
        self.viewCount = dto.view_count ?? 0
        self.createdAt = dto.created_at ?? ""
        self.expiresAt = dto.expires_at
        self.isExpired = dto.is_expired ?? false
    }
}

struct ShareStatsResponse: Equatable {
    let totalShares: Int
    let totalViews: Int
    let shares: [ShareStatsItem]

    init(dto: ShareStatsResponseDTO) {
        self.totalShares = dto.total_shares ?? 0
        self.totalViews = dto.total_views ?? 0
        self.shares = (dto.shares ?? []).map(ShareStatsItem.init)
    }
}

extension DivinationResult {
    /// 分享落地页：由 `GET /shares/{token}` 的 `result` 字段组装
    init(shareToken: String, payload: ShareResultPayloadDTO) {
        self.sessionId = shareToken
        self.status = "completed"
        self.outcome = payload.outcome
        self.title = payload.title
        self.spread = nil
        self.summary = payload.summary ?? ""
        self.detail = payload.detail ?? ""
        self.createdAt = nil
        self.processingType = nil
        self.hexagramInfo = payload.hexagram_info.map(HexagramInfo.init)
        self.cards = (payload.cards ?? []).map(TarotCard.init)
        self.dailyFortune = payload.daily_fortune.map(DailyFortuneEmbedded.init)
        self.quality = nil
        self.yarrowTrace = nil
    }
}

