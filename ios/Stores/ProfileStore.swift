import Foundation

@MainActor
final class ProfileStore: ObservableObject {
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var profile: UserProfile?

    private let authStore: AuthStore
    private let service: ProfileService

    init(authStore: AuthStore) {
        self.authStore = authStore
        self.service = AppEnvironment.shared.makeProfileService { [weak authStore] in
            Task { @MainActor in authStore?.logout() }
        }
    }

    func load() async {
        guard authStore.isAuthenticated else {
            errorMessage = "请先登录"
            return
        }

        isLoading = true
        errorMessage = nil
        defer { isLoading = false }

        do {
            let dto = try await service.getMyProfile()
            profile = UserProfile(dto: dto)
        } catch {
            errorMessage = (error as? LocalizedError)?.errorDescription ?? "加载档案失败"
        }
    }
}

