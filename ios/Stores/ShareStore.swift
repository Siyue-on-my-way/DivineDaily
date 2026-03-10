import Foundation

@MainActor
final class ShareStore: ObservableObject {
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var generatedURL: String?
    @Published var stats: ShareStats?

    private let service: ShareService

    init(authStore: AuthStore) {
        self.service = AppEnvironment.shared.makeShareService { [weak authStore] in
            Task { @MainActor in authStore?.logout() }
        }
    }

    func createShare(sessionId: String, expiresDays: Int? = 7, isPublic: Bool = true) async {
        guard !sessionId.isEmpty else {
            errorMessage = "无效的会话ID"
            return
        }

        isLoading = true
        errorMessage = nil
        generatedURL = nil
        defer { isLoading = false }

        do {
            let response = try await service.createShare(sessionId: sessionId, expiresDays: expiresDays, isPublic: isPublic)
            generatedURL = response.url
            await loadStats(sessionId: sessionId)
        } catch {
            errorMessage = (error as? LocalizedError)?.errorDescription ?? "创建分享失败"
        }
    }

    func loadStats(sessionId: String) async {
        guard !sessionId.isEmpty else { return }

        do {
            stats = try await service.getShareStats(sessionId: sessionId)
        } catch {
            errorMessage = (error as? LocalizedError)?.errorDescription ?? "加载分享统计失败"
        }
    }

    func deleteShare(shareToken: String, sessionId: String) async {
        guard !shareToken.isEmpty else { return }

        do {
            try await service.deleteShare(shareToken: shareToken)
            if generatedURL?.contains(shareToken) == true {
                generatedURL = nil
            }
            await loadStats(sessionId: sessionId)
        } catch {
            errorMessage = (error as? LocalizedError)?.errorDescription ?? "删除分享失败"
        }
    }
}
