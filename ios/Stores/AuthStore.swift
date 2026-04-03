import Foundation

@MainActor
final class AuthStore: ObservableObject {
    @Published private(set) var user: AppUser?
    @Published private(set) var isAuthenticated: Bool = false

    private let tokenStore: TokenStore
    private let service: AuthService

    init() {
        self.tokenStore = AppEnvironment.shared.tokenStore
        self.service = AppEnvironment.shared.makeAuthService { [weak self] in
            self?.logout()
        }

        // 启动时先做“粗同步”：只根据 token 是否存在判断是否可能已登录。
        self.isAuthenticated = tokenStore.getAccessToken() != nil
    }

    func syncUser() async {
        guard tokenStore.getAccessToken() != nil else {
            logout()
            return
        }

        do {
            let meDTO = try await service.me()
            self.user = AppUser(dto: meDTO)
            self.isAuthenticated = true
        } catch {
            logout()
        }
    }

    func login(username: String, password: String) async throws {
        let dto = try await service.login(username: username, password: password)
        tokenStore.setTokens(
            accessToken: dto.token,
            refreshToken: dto.refresh_token,
            tokenType: dto.token_type
        )
        self.user = AppUser(dto: dto.user)
        self.isAuthenticated = true
    }

    func register(username: String, email: String?, password: String, confirmPassword: String) async throws {
        let dto = try await service.register(
            username: username,
            email: email,
            password: password,
            confirmPassword: confirmPassword
        )
        tokenStore.setTokens(
            accessToken: dto.token,
            refreshToken: dto.refresh_token,
            tokenType: dto.token_type
        )
        self.user = AppUser(dto: dto.user)
        self.isAuthenticated = true
    }

    func logout() {
        tokenStore.clear()
        user = nil
        isAuthenticated = false
    }
}

