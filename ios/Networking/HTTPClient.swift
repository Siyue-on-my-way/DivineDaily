import Foundation

/// 通用 HTTP 客户端（JSON 编码/解码 + 自动鉴权刷新 + 错误解析）
final class HTTPClient {
    private let tokenStore: TokenStore
    private let onUnauthorized: (() -> Void)?
    private let refreshCoordinator = TokenRefreshCoordinator()

    init(tokenStore: TokenStore, onUnauthorized: (() -> Void)? = nil) {
        self.tokenStore = tokenStore
        self.onUnauthorized = onUnauthorized
    }

    private func makeURL(path: String) -> URL {
        let trimmedPath = path.hasPrefix("/") ? String(path.dropFirst()) : path
        // 支持在 path 中直接携带 query（例如：`history?limit=10&offset=0`）
        if trimmedPath.contains("?") {
            let base = AppConfig.apiBaseURL.absoluteString
            let separator = base.hasSuffix("/") ? "" : "/"
            return URL(string: "\(base)\(separator)\(trimmedPath)")!
        }

        return AppConfig.apiBaseURL.appendingPathComponent(trimmedPath)
    }

    func request<T: Decodable>(
        path: String,
        method: String,
        body: Encodable? = nil,
        requiresAuth: Bool
    ) async throws -> T {
        let (data, status) = try await performRequest(
            path: path,
            method: method,
            body: body,
            requiresAuth: requiresAuth,
            hasRetriedAfterRefresh: false
        )

        guard (200...299).contains(status) else {
            throw parseAPIError(statusCode: status, data: data)
        }

        do {
            return try JSONDecoder().decode(T.self, from: data)
        } catch {
            throw APIError.decodingError("响应解析失败，请稍后重试")
        }
    }

    func requestVoid(
        path: String,
        method: String,
        body: Encodable? = nil,
        requiresAuth: Bool
    ) async throws {
        let _: EmptyResponse = try await request(
            path: path,
            method: method,
            body: body,
            requiresAuth: requiresAuth
        )
    }

    private func performRequest(
        path: String,
        method: String,
        body: Encodable?,
        requiresAuth: Bool,
        hasRetriedAfterRefresh: Bool
    ) async throws -> (Data, Int) {
        let request = try makeRequest(path: path, method: method, body: body, requiresAuth: requiresAuth)

        let data: Data
        let response: URLResponse
        do {
            (data, response) = try await URLSession.shared.data(for: request)
        } catch {
            throw APIError.networkError("网络连接失败，请检查网络后重试")
        }

        let status = (response as? HTTPURLResponse)?.statusCode ?? -1

        // 仅对需要鉴权的请求进行自动刷新重试，且只重试一次
        if status == 401, requiresAuth, !hasRetriedAfterRefresh {
            do {
                _ = try await refreshCoordinator.refresh(using: self)
                return try await performRequest(
                    path: path,
                    method: method,
                    body: body,
                    requiresAuth: requiresAuth,
                    hasRetriedAfterRefresh: true
                )
            } catch {
                tokenStore.clear()
                onUnauthorized?()
                throw APIError.unauthorized
            }
        }

        // 重试后依然401，视为登录失效
        if status == 401 {
            tokenStore.clear()
            onUnauthorized?()
            throw APIError.unauthorized
        }

        return (data, status)
    }

    private func makeRequest(
        path: String,
        method: String,
        body: Encodable?,
        requiresAuth: Bool
    ) throws -> URLRequest {
        let url = makeURL(path: path)
        var request = URLRequest(url: url)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("application/json", forHTTPHeaderField: "Accept")

        if requiresAuth, let token = tokenStore.getAccessToken() {
            let tokenType = tokenStore.getTokenType() ?? "bearer"
            let prefix = tokenType.lowercased() == "bearer" ? "Bearer" : tokenType
            request.setValue("\(prefix) \(token)", forHTTPHeaderField: "Authorization")
        }

        if let body {
            let encoder = JSONEncoder()
            request.httpBody = try encoder.encode(EncodableWrapper(body))
        }

        return request
    }

    private func parseAPIError(statusCode: Int, data: Data) -> APIError {
        if statusCode == 403 {
            return .forbidden
        }

        let dto = try? JSONDecoder().decode(APIErrorDTO.self, from: data)
        let detail = dto?.detail ?? dto?.message
        return .serverError(statusCode: statusCode, detail: detail)
    }

    fileprivate func performTokenRefresh() async throws -> RefreshedTokens {
        guard let refreshToken = tokenStore.getRefreshToken() else {
            throw APIError.unauthorized
        }

        struct RefreshTokenRequest: Encodable {
            let refresh_token: String
        }

        struct RefreshTokenResponseDTO: Decodable {
            let token: String
            let refresh_token: String
            let token_type: String?
        }

        let requestBody = RefreshTokenRequest(refresh_token: refreshToken)

        let (data, status) = try await performRequest(
            path: "auth/refresh",
            method: "POST",
            body: requestBody,
            requiresAuth: false,
            hasRetriedAfterRefresh: true
        )

        guard (200...299).contains(status) else {
            throw parseAPIError(statusCode: status, data: data)
        }

        let refreshDTO: RefreshTokenResponseDTO
        do {
            refreshDTO = try JSONDecoder().decode(RefreshTokenResponseDTO.self, from: data)
        } catch {
            throw APIError.decodingError("刷新登录状态失败，请重新登录")
        }

        tokenStore.setTokens(
            accessToken: refreshDTO.token,
            refreshToken: refreshDTO.refresh_token,
            tokenType: refreshDTO.token_type
        )

        return RefreshedTokens(
            accessToken: refreshDTO.token,
            refreshToken: refreshDTO.refresh_token,
            tokenType: refreshDTO.token_type
        )
    }

    /// 兼容 `requestVoid`：当不关心响应体时，用这个解码占位
    private struct EmptyResponse: Decodable {}

    /// 将任意 `Encodable` 值封装到一个 concrete `Encodable` 里
    private struct EncodableWrapper: Encodable {
        private let encodeBlock: (Encoder) throws -> Void

        init(_ value: Encodable) {
            self.encodeBlock = { encoder in
                try value.encode(to: encoder)
            }
        }

        func encode(to encoder: Encoder) throws {
            try encodeBlock(encoder)
        }
    }
}

private struct RefreshedTokens {
    let accessToken: String
    let refreshToken: String
    let tokenType: String?
}

private actor TokenRefreshCoordinator {
    private var inFlightRefresh: Task<RefreshedTokens, Error>?

    func refresh(using client: HTTPClient) async throws -> RefreshedTokens {
        if let inFlightRefresh {
            return try await inFlightRefresh.value
        }

        let task = Task { try await client.performTokenRefresh() }
        inFlightRefresh = task

        do {
            let tokens = try await task.value
            inFlightRefresh = nil
            return tokens
        } catch {
            inFlightRefresh = nil
            throw error
        }
    }
}
