import Foundation

/// 简单 token 存储（开发阶段使用 UserDefaults；生产建议改 Keychain）
final class TokenStore {
    private let defaults = UserDefaults.standard

    private let accessTokenKey = "auth_token"
    private let refreshTokenKey = "auth_refresh_token"
    private let tokenTypeKey = "auth_token_type"

    func getAccessToken() -> String? {
        defaults.string(forKey: accessTokenKey)
    }

    func getRefreshToken() -> String? {
        defaults.string(forKey: refreshTokenKey)
    }

    func getTokenType() -> String? {
        defaults.string(forKey: tokenTypeKey)
    }

    func setTokens(accessToken: String, refreshToken: String?, tokenType: String?) {
        defaults.set(accessToken, forKey: accessTokenKey)
        if let refreshToken {
            defaults.set(refreshToken, forKey: refreshTokenKey)
        }
        if let tokenType {
            defaults.set(tokenType, forKey: tokenTypeKey)
        }
    }

    func clear() {
        defaults.removeObject(forKey: accessTokenKey)
        defaults.removeObject(forKey: refreshTokenKey)
        defaults.removeObject(forKey: tokenTypeKey)
    }
}

