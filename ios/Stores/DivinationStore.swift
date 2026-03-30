import Foundation

@MainActor
final class DivinationStore: ObservableObject {
    @Published var question = ""
    @Published var isLoading = false
    @Published var result: DivinationResult?
    @Published var errorMessage: String?
    @Published var isSaving = false
    @Published var isSharing = false
    @Published var shareURL: String?

    private let authStore: AuthStore
    private let service: DivinationService
    private let shareService: ShareService
    private let saveService: SaveService
    private var pollingTask: Task<Void, Never>?

    init(authStore: AuthStore) {
        self.authStore = authStore
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

    deinit {
        pollingTask?.cancel()
    }

    func submitIChingQuestion() async {
        guard let userId = authStore.user?.id else {
            errorMessage = "请先登录"
            return
        }

        let trimmed = question.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else {
            errorMessage = "请输入问题"
            return
        }

        isLoading = true
        errorMessage = nil
        result = nil

        do {
            let firstResult = try await service.startIChing(userId: userId, question: trimmed)

            // 低质量问题可能直接返回完整结果
            if (firstResult.status ?? "completed") == "completed", !firstResult.summary.isEmpty {
                result = firstResult
                isLoading = false
                return
            }

            startPolling(sessionId: firstResult.sessionId)
        } catch {
            isLoading = false
            errorMessage = (error as? LocalizedError)?.errorDescription ?? "占卜失败"
        }
    }

    func reset() {
        pollingTask?.cancel()
        pollingTask = nil
        question = ""
        result = nil
        errorMessage = nil
        isLoading = false
        isSaving = false
        isSharing = false
        shareURL = nil
    }

    func createShare() async {
        guard let sessionId = result?.sessionId, !sessionId.isEmpty else {
            errorMessage = "无有效占卜记录"
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

    func saveResult() async {
        guard let sessionId = result?.sessionId, !sessionId.isEmpty else {
            errorMessage = "无有效占卜记录"
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

    private func startPolling(sessionId: String) {
        pollingTask?.cancel()
        pollingTask = Task {
            let polled = try? await DivinationPollingHelper.pollResult(
                sessionId: sessionId,
                fetch: { id in try await self.service.getResult(sessionId: id) },
                isCompleted: { current in
                    let status = current.status ?? "completed"
                    return status == "completed" || (!current.summary.isEmpty && !current.detail.isEmpty)
                }
            )

            if let finalResult = polled {
                result = finalResult
                isLoading = false
                return
            }

            isLoading = false
            errorMessage = "占卜超时，请重试"
        }
    }
}
