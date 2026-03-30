import Foundation

@MainActor
final class FeedbackStore: ObservableObject {
    @Published var isSubmitting = false
    @Published var errorMessage: String?
    @Published var submitted = false

    private let service: FeedbackService

    init(authStore: AuthStore) {
        self.service = AppEnvironment.shared.makeFeedbackService { [weak authStore] in
            Task { @MainActor in authStore?.logout() }
        }
    }

    func submitDivinationFeedback(
        sessionId: String,
        rating: Int,
        comment: String?,
        tags: [String]?,
        isHelpful: Bool?
    ) async {
        guard !sessionId.isEmpty else {
            errorMessage = "无效的会话ID"
            return
        }

        isSubmitting = true
        errorMessage = nil
        defer { isSubmitting = false }

        do {
            let response = try await service.submitDivinationFeedback(
                sessionId: sessionId,
                rating: rating,
                comment: comment,
                tags: tags,
                isHelpful: isHelpful
            )
            submitted = response.success
        } catch {
            errorMessage = (error as? LocalizedError)?.errorDescription ?? "提交反馈失败"
        }
    }

    func reset() {
        submitted = false
        errorMessage = nil
        isSubmitting = false
    }
}
