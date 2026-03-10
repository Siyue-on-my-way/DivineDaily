import Foundation

@MainActor
final class FortuneStore: ObservableObject {
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var today: DailyFortune?
    @Published var history: [DailyFortune] = []

    private let service: FortuneService

    init(authStore: AuthStore) {
        self.service = AppEnvironment.shared.makeFortuneService { [weak authStore] in
            Task { @MainActor in authStore?.logout() }
        }
    }

    func loadToday() async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }

        do {
            today = try await service.getTodayFortune()
        } catch {
            errorMessage = (error as? LocalizedError)?.errorDescription ?? "获取每日运势失败"
        }
    }

    func loadHistory(limit: Int = 10, skip: Int = 0) async {
        do {
            history = try await service.getFortuneHistory(limit: limit, skip: skip)
        } catch {
            errorMessage = (error as? LocalizedError)?.errorDescription ?? "获取运势历史失败"
        }
    }
}
