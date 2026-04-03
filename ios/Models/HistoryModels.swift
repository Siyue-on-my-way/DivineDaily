import Foundation

struct DivinationHistoryResultDataDTO: Decodable {
    let outcome: String?
    let title: String?
    let summary: String?
    let detail: String?
    let processing_type: String?
}

struct DivinationHistorySessionDTO: Decodable {
    let id: String?
    let question: String?
    let version: String?
    let status: String?
    let created_at: String?

    // 后端可能同时提供明文摘要/详解和结构化 result_data
    let result_summary: String?
    let result_detail: String?
    let result_data: DivinationHistoryResultDataDTO?
}

struct DivinationHistoryListResponseDTO: Decodable {
    let sessions: [DivinationHistorySessionDTO]
    let total: Int
    let limit: Int
    let offset: Int
    let has_more: Bool
}

struct DivinationHistoryItem: Identifiable, Equatable {
    let id: String
    let question: String
    let outcome: String
    let version: String
    let createdAt: String
    let summary: String

    init(dto: DivinationHistorySessionDTO) {
        self.id = dto.id ?? ""
        self.question = dto.question ?? ""
        self.version = dto.version ?? ""
        self.createdAt = dto.created_at ?? ""

        // outcome 通常在 result_data.outcome 或 result_summary 里
        self.outcome = dto.result_data?.outcome ?? ""
        self.summary = dto.result_data?.summary ?? dto.result_summary ?? ""
    }
}

