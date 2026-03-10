import Foundation

struct DivinationHistoryResponse: Decodable {
    let sessions: [DivinationHistoryItemDTO]
    let total: Int
    let limit: Int
    let offset: Int
    let has_more: Bool
}

struct DivinationHistoryItemDTO: Decodable {
    let id: String
    let question: String?
    let version: String?
    let status: String?
    let outcome: String?
    let summary: String?
    let created_at: String?
}

struct DivinationHistoryItem: Identifiable, Equatable {
    let id: String
    let question: String
    let version: String
    let status: String
    let outcome: String
    let summary: String
    let createdAtRaw: String
    let createdAt: String

    var isCompleted: Bool {
        status.lowercased() == "completed"
    }

    init(dto: DivinationHistoryItemDTO) {
        self.id = dto.id
        self.question = dto.question ?? ""
        self.version = dto.version ?? ""
        self.status = dto.status ?? ""
        self.outcome = dto.outcome ?? ""
        self.summary = dto.summary ?? ""
        self.createdAtRaw = dto.created_at ?? ""
        self.createdAt = DateTextFormatter.displayDateTime(from: dto.created_at)
    }
}
