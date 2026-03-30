import Foundation

final class FeedbackService {
    private let client: HTTPClient

    init(client: HTTPClient) {
        self.client = client
    }

    func submitDivinationFeedback(
        sessionId: String,
        rating: Int,
        comment: String?,
        tags: [String]?,
        isHelpful: Bool?
    ) async throws -> FeedbackResponse {
        let body = DivinationFeedbackRequest(
            session_id: sessionId,
            feedback_type: "accuracy",
            rating: rating,
            comment: comment,
            tags: tags,
            is_helpful: isHelpful
        )

        let dto: FeedbackResponseDTO = try await client.request(
            path: "feedback/divination",
            method: "POST",
            body: body,
            requiresAuth: true
        )

        return FeedbackResponse(dto: dto)
    }
}
