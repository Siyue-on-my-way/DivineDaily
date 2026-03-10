import Foundation

final class AuthService {
    private let client: HTTPClient

    init(client: HTTPClient) {
        self.client = client
    }

    func login(username: String, password: String) async throws -> TokenResponse {
        let body = LoginRequest(username: username, password: password)
        return try await client.request(path: "auth/login", method: "POST", body: body)
    }

    func register(username: String, email: String, password: String) async throws -> TokenResponse {
        let body = RegisterRequest(username: username, email: email, password: password)
        return try await client.request(path: "auth/register", method: "POST", body: body)
    }

    func me() async throws -> CurrentUserResponse {
        try await client.request(path: "auth/me", requiresAuth: true)
    }

    func refresh(refreshToken: String) async throws -> RefreshTokenResponse {
        let body = RefreshTokenRequest(refresh_token: refreshToken)
        return try await client.request(path: "auth/refresh", method: "POST", body: body)
    }
}
