import Foundation

@MainActor
final class HistoryDetailStore: ObservableObject {
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var result: DivinationResult?
    @Published var isSaving = false
    @Published var isSharing = false
    @Published var shareURL: String?

    private let service: DivinationService
    private let shareService: ShareService
    private let saveService: SaveService

    init(authStore: AuthStore) {
        self.service = AppEnvironment.shared.makeDivinationService { [weak authStore] in
            Task { @MainActor in authStore?.logout() }
        }
        self.shareService = AppEnvironment.shared.makeShareService { [weak authStore] in
            Task { @MainActor in authStore?.logout() }
        }
        self.saveService = AppEnvironment.shared.makeSaveService { [weak authStore] in
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

    func createShare(sessionId: String) async {
        guard !sessionId.isEmpty else {
            errorMessage = "无效的会话ID"
            return
        }

        isSharing = true
        errorMessage = nil
        shareURL = nil
        defer { isSharing = false }

        do {
            let response = try await shareService.createShare(sessionId: sessionId, expiresDays: 30, isPublic: true)
            shareURL = response.url
        } catch {
            errorMessage = (error as? LocalizedError)?.errorDescription ?? "创建分享失败"
        }
    }

    func saveResult(sessionId: String) async {
        guard !sessionId.isEmpty else {
            errorMessage = "无效的会话ID"
            return
        }

        isSaving = true
        errorMessage = nil
        defer { isSaving = false }

        do {
            try await saveService.save(sessionId: sessionId)
        } catch {
            errorMessage = (error as? LocalizedError)?.errorDescription ?? "保存失败"
        }
    }

    func resetActions() {
        isSaving = false
        isSharing = false
        shareURL = nil
        errorMessage = nil
    }
}
