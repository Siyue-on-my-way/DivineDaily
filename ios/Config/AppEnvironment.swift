import Foundation

final class AppEnvironment {
    static let shared = AppEnvironment()

    let tokenStore: TokenStore

    private init() {
        self.tokenStore = TokenStore()
    }

    func makeHTTPClient(onUnauthorized: (() -> Void)? = nil) -> HTTPClient {
        HTTPClient(tokenStore: tokenStore, onUnauthorized: onUnauthorized)
    }

    func makeAuthService(onUnauthorized: (() -> Void)? = nil) -> AuthService {
        AuthService(client: makeHTTPClient(onUnauthorized: onUnauthorized))
    }

    func makeDivinationService(onUnauthorized: (() -> Void)? = nil) -> DivinationService {
        DivinationService(client: makeHTTPClient(onUnauthorized: onUnauthorized))
    }

    func makeFortuneService(onUnauthorized: (() -> Void)? = nil) -> FortuneService {
        FortuneService(client: makeHTTPClient(onUnauthorized: onUnauthorized))
    }

    func makeProfileService(onUnauthorized: (() -> Void)? = nil) -> ProfileService {
        ProfileService(client: makeHTTPClient(onUnauthorized: onUnauthorized))
    }

    func makeShareService(onUnauthorized: (() -> Void)? = nil) -> ShareService {
        ShareService(client: makeHTTPClient(onUnauthorized: onUnauthorized))
    }
}
