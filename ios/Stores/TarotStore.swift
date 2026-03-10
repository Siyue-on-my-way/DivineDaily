import Foundation

@MainActor
final class TarotStore: ObservableObject {
    @Published var selectedSpread: String = "single"
    @Published var question = ""
    @Published var cutPosition = 50
    @Published var shuffleTrace: [Int] = []

    @Published var isLoading = false
    @Published var result: DivinationResult?
    @Published var errorMessage: String?

    private let authStore: AuthStore
    private let service: DivinationService
    private var pollingTask: Task<Void, Never>?

    init(authStore: AuthStore) {
        self.authStore = authStore
        self.service = AppEnvironment.shared.makeDivinationService { [weak authStore] in
            Task { @MainActor in authStore?.logout() }
        }
    }

    deinit {
        pollingTask?.cancel()
    }

    func updateCutPosition(_ value: Int) {
        cutPosition = value
        shuffleTrace.append(value)
        if shuffleTrace.count > 100 {
            shuffleTrace.removeFirst(shuffleTrace.count - 100)
        }
    }

    func submitTarot() async {
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
            let first = try await service.startTarot(
                userId: userId,
                question: trimmed,
                spread: selectedSpread,
                cutPosition: cutPosition,
                shuffleTrace: shuffleTrace
            )

            if (first.status ?? "completed") == "completed", !first.summary.isEmpty {
                result = first
                isLoading = false
                return
            }

            startPolling(sessionId: first.sessionId)
        } catch {
            isLoading = false
            errorMessage = (error as? LocalizedError)?.errorDescription ?? "塔罗占卜失败"
        }
    }

    func reset() {
        pollingTask?.cancel()
        pollingTask = nil
        selectedSpread = "single"
        question = ""
        cutPosition = 50
        shuffleTrace = []
        isLoading = false
        result = nil
        errorMessage = nil
    }

    private func startPolling(sessionId: String) {
        pollingTask?.cancel()
        pollingTask = Task {
            let polled = try? await DivinationPollingHelper.pollResult(
                sessionId: sessionId,
                fetch: { id in try await self.service.getResult(sessionId: id) },
                isCompleted: { current in
                    let status = current.status ?? "completed"
                    return status == "completed" || (!current.summary.isEmpty && !current.cards.isEmpty)
                }
            )

            if let finalResult = polled {
                result = finalResult
                isLoading = false
                return
            }

            isLoading = false
            errorMessage = "塔罗解读超时，请重试"
        }
    }
}
