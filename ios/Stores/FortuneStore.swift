import Foundation

@MainActor
final class FortuneStore: ObservableObject {
    @Published var isLoading = false
    @Published var errorMessage: String?

    @Published var today: FortuneInfo?
    @Published var history: [FortuneInfo] = []

    private let authStore: AuthStore
    private let service: FortuneService

    init(authStore: AuthStore) {
        self.authStore = authStore
        self.service = AppEnvironment.shared.makeFortuneService { [weak authStore] in
            Task { @MainActor in authStore?.logout() }
        }
    }

    func loadToday() async {
        guard authStore.isAuthenticated else {
            errorMessage = "请先登录"
            return
        }

        isLoading = true
        errorMessage = nil
        defer { isLoading = false }

        do {
            let dto = try await service.generateToday()
            today = FortuneInfo(dto: dto)
        } catch {
            errorMessage = (error as? LocalizedError)?.errorDescription ?? "加载今日运势失败"
        }
    }

    func loadHistory(limit: Int, skip: Int) async {
        guard authStore.isAuthenticated else {
            errorMessage = "请先登录"
            return
        }

        isLoading = true
        errorMessage = nil
        defer { isLoading = false }

        do {
            let dtos = try await service.listHistory(skip: skip, limit: limit)
            history = dtos.map(FortuneInfo.init)
        } catch {
            errorMessage = (error as? LocalizedError)?.errorDescription ?? "加载运势历史失败"
        }
    }
}

