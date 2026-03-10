import Foundation

@MainActor
final class HistoryDetailStore: ObservableObject {
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var result: DivinationResult?

    private let service: DivinationService

    init(authStore: AuthStore) {
        self.service = AppEnvironment.shared.makeDivinationService { [weak authStore] in
            Task { @MainActor in authStore?.logout() }
        }
    }

    func load(sessionId: String) async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }

        do {
            result = try await service.getResult(sessionId: sessionId)
        } catch {
            errorMessage = (error as? LocalizedError)?.errorDescription ?? "加载详情失败"
        }
    }
}
