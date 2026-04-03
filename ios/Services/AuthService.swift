import Foundation

final class AuthService {
    private let client: HTTPClient

    init(client: HTTPClient) {
        self.client = client
    }

    func login(username: String, password: String) async throws -> TokenResponseDTO {
        let body = LoginRequestDTO(username: username, password: password)
        let dto: TokenResponseDTO = try await client.request(
            path: "auth/login",
            method: "POST",
            body: body,
            requiresAuth: false
        )
        return dto
    }

    func register(username: String, email: String?, password: String, confirmPassword: String) async throws -> TokenResponseDTO {
        let body = RegisterRequestDTO(
            username: username,
            email: email,
            password: password,
            confirm_password: confirmPassword
        )
        let dto: TokenResponseDTO = try await client.request(
            path: "auth/register",
            method: "POST",
            body: body,
            requiresAuth: false
        )
        return dto
    }

    /// 刷新 token：后端刷新接口返回不含 user 信息，因此这里会额外调用 `/auth/me` 完成用户同步。
    func refreshToken() async throws -> (tokenResponse: TokenResponseDTO) {
        guard let refresh = AppEnvironment.shared.tokenStore.getRefreshToken() else {
            throw APIError.unauthorized
        }
        let body = RefreshTokenRequest(refresh_token: refresh)

        // /auth/refresh 返回：{ token, refresh_token, token_type }
        struct RefreshTokenResponseDTO: Decodable {
            let token: String
            let refresh_token: String
            let token_type: String?
        }

        let refreshDTO: RefreshTokenResponseDTO = try await client.request(
            path: "auth/refresh",
            method: "POST",
            body: body,
            requiresAuth: false
        )

        // 拉取当前用户
        let user: UserDTO = try await client.request(
            path: "auth/me",
            method: "GET",
            body: nil,
            requiresAuth: true
        )

        // 组装成统一返回结构
        let tokenResponse = TokenResponseDTO(
            token: refreshDTO.token,
            refresh_token: refreshDTO.refresh_token,
            token_type: refreshDTO.token_type,
            user: user
        )
        return (tokenResponse: tokenResponse)
    }

    func me() async throws -> UserDTO {
        // /auth/me 返回 UserResponse（即 UserDTO 结构）
        let user: UserDTO = try await client.request(
            path: "auth/me",
            method: "GET",
            body: nil,
            requiresAuth: true
        )
        return user
    }

    func logout() async throws {
        // /auth/logout 返回 {"message": "..."}，这里不关心响应体
        try await client.requestVoid(
            path: "auth/logout",
            method: "POST",
            body: nil,
            requiresAuth: true
        )
    }
}

