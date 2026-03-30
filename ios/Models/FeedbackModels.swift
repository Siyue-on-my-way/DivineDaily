import Foundation

struct DivinationFeedbackRequest: Encodable {
    let session_id: String
    let feedback_type: String
    let rating: Int
    let comment: String?
    let tags: [String]?
    let is_helpful: Bool?
}

struct FeedbackResponseDTO: Decodable {
    let id: Int
    let message: String
    let success: Bool
}

struct FeedbackResponse: Equatable {
    let id: Int
    let message: String
    let success: Bool

    init(dto: FeedbackResponseDTO) {
        self.id = dto.id
        self.message = dto.message
        self.success = dto.success
    }
}
