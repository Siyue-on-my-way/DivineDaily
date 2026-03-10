import Foundation

@MainActor
final class AuthStore: ObservableObject {
    @Published var isLoading = false
    @Published var isAuthenticated = false
    @Published var user: AppUser?
    @Published var errorMessage: String?

    private let env = AppEnvironment.shared
    var tokenStore: TokenStore { env.tokenStore }
    private lazy var authService = env.makeAuthService { [weak self] in
        Task { @MainActor in self?.logout() }
    }

    func bootstrap() async {
        isLoading = true
        defer { isLoading = false }

        guard let localUser = tokenStore.currentUser else {
            isAuthenticated = false
            user = nil
            return
        }

        user = localUser

        let meSucceeded = await fetchMeAndPersistSession()
        if meSucceeded {
            return
        }

        let refreshSucceeded = await tryRefreshIfPossible()
        if refreshSucceeded {
            _ = await fetchMeAndPersistSession()
            return
        }

        logout()
    }

    func login(username: String, password: String) async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }

        do {
            let response = try await authService.login(username: username, password: password)
            let appUser = AppUser(dto: response.user)
            tokenStore.saveSession(
                accessToken: response.token,
                refreshToken: response.refresh_token,
                user: appUser
            )
            user = appUser
            isAuthenticated = true
        } catch {
            errorMessage = (error as? LocalizedError)?.errorDescription ?? "登录失败"
            isAuthenticated = false
        }
    }

    func register(username: String, email: String, password: String) async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }

        do {
            let response = try await authService.register(username: username, email: email, password: password)
            let appUser = AppUser(dto: response.user)
            tokenStore.saveSession(
                accessToken: response.token,
                refreshToken: response.refresh_token,
                user: appUser
            )
            user = appUser
            isAuthenticated = true
        } catch {
            errorMessage = (error as? LocalizedError)?.errorDescription ?? "注册失败"
            isAuthenticated = false
        }
    }

    func logout() {
        tokenStore.clear()
        isAuthenticated = false
        user = nil
        errorMessage = nil
    }

    @discardableResult
    func refreshIfNeeded() async -> Bool {
        await tryRefreshIfPossible()
    }

    private func fetchMeAndPersistSession() async -> Bool {
        guard let accessToken = tokenStore.accessToken,
              !accessToken.isEmpty else {
            return false
        }

        do {
            let me = try await authService.me()
            let confirmedUser = AppUser(dto: me)
            tokenStore.saveSession(
                accessToken: accessToken,
                refreshToken: tokenStore.refreshToken ?? "",
                user: confirmedUser
            )
            user = confirmedUser
            isAuthenticated = true
            return true
        } catch {
            return false
        }
    }

    private func tryRefreshIfPossible() async -> Bool {
        guard let refreshToken = tokenStore.refreshToken else {
            return false
        }

        do {
            let refreshed = try await authService.refresh(refreshToken: refreshToken)
            tokenStore.updateTokens(
                accessToken: refreshed.token,
                refreshToken: refreshed.refresh_token
            )
            let me = try await authService.me()
            let appUser = AppUser(dto: me)
            tokenStore.updateUser(appUser)
            user = appUser
            isAuthenticated = true
            return true
        } catch {
            return false
        }
    }
}
