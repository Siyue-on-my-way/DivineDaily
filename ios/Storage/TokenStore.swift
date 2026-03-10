import Foundation

final class TokenStore {
    private enum Keys {
        static let accessToken = "dd.accessToken"
        static let refreshToken = "dd.refreshToken"
        static let user = "dd.user"
    }

    var accessToken: String? {
        UserDefaults.standard.string(forKey: Keys.accessToken)
    }

    var refreshToken: String? {
        UserDefaults.standard.string(forKey: Keys.refreshToken)
    }

    var currentUser: AppUser? {
        guard let data = UserDefaults.standard.data(forKey: Keys.user) else { return nil }
        return try? JSONDecoder().decode(AppUser.self, from: data)
    }

    func saveSession(accessToken: String, refreshToken: String, user: AppUser) {
        UserDefaults.standard.set(accessToken, forKey: Keys.accessToken)
        UserDefaults.standard.set(refreshToken, forKey: Keys.refreshToken)
        let data = try? JSONEncoder().encode(user)
        UserDefaults.standard.set(data, forKey: Keys.user)
    }

    func updateTokens(accessToken: String, refreshToken: String) {
        UserDefaults.standard.set(accessToken, forKey: Keys.accessToken)
        UserDefaults.standard.set(refreshToken, forKey: Keys.refreshToken)
    }

    func updateUser(_ user: AppUser) {
        let data = try? JSONEncoder().encode(user)
        UserDefaults.standard.set(data, forKey: Keys.user)
    }

    func clear() {
        UserDefaults.standard.removeObject(forKey: Keys.accessToken)
        UserDefaults.standard.removeObject(forKey: Keys.refreshToken)
        UserDefaults.standard.removeObject(forKey: Keys.user)
    }
}
