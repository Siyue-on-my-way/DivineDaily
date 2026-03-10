import Foundation

actor RefreshTokenCoordinator {
    private var inFlightTask: Task<Bool, Error>?

    func refresh(using operation: @escaping () async throws -> Bool) async throws -> Bool {
        if let task = inFlightTask {
            return try await task.value
        }

        let task = Task { try await operation() }
        inFlightTask = task
        defer { inFlightTask = nil }
        return try await task.value
    }
}

final class HTTPClient {
    private let session: URLSession
    private let tokenStore: TokenStore
    private let onUnauthorized: (() -> Void)?
    private let refreshCoordinator = RefreshTokenCoordinator()

    init(tokenStore: TokenStore, onUnauthorized: (() -> Void)? = nil) {
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = AppConfig.requestTimeout
        config.timeoutIntervalForResource = AppConfig.requestTimeout
        self.session = URLSession(configuration: config)
        self.tokenStore = tokenStore
        self.onUnauthorized = onUnauthorized
    }

    func request<T: Decodable>(
        path: String,
        method: String = "GET",
        body: Encodable? = nil,
        queryItems: [URLQueryItem] = [],
        requiresAuth: Bool = false
    ) async throws -> T {
        let data = try await rawRequest(path: path, method: method, body: body, queryItems: queryItems, requiresAuth: requiresAuth)

        do {
            return try JSONDecoder().decode(T.self, from: data)
        } catch {
            throw APIError.decoding(error)
        }
    }

    @discardableResult
    func requestVoid(
        path: String,
        method: String = "GET",
        body: Encodable? = nil,
        queryItems: [URLQueryItem] = [],
        requiresAuth: Bool = false
    ) async throws -> Data {
        try await rawRequest(path: path, method: method, body: body, queryItems: queryItems, requiresAuth: requiresAuth)
    }

    private func rawRequest(
        path: String,
        method: String,
        body: Encodable?,
        queryItems: [URLQueryItem],
        requiresAuth: Bool
    ) async throws -> Data {
        do {
            return try await performRequest(
                path: path,
                method: method,
                body: body,
                queryItems: queryItems,
                requiresAuth: requiresAuth
            )
        } catch APIError.unauthorized {
            let refreshed = try await refreshCoordinator.refresh { [weak self] in
                guard let self else { return false }
                guard requiresAuth else { return false }
                return try await self.refreshTokenIfPossible()
            }

            if requiresAuth, refreshed {
                return try await performRequest(
                    path: path,
                    method: method,
                    body: body,
                    queryItems: queryItems,
                    requiresAuth: requiresAuth
                )
            }

            onUnauthorized?()
            throw APIError.unauthorized
        }
    }

    private func performRequest(
        path: String,
        method: String,
        body: Encodable?,
        queryItems: [URLQueryItem],
        requiresAuth: Bool
    ) async throws -> Data {
        guard let url = buildURL(path: path, queryItems: queryItems) else {
            throw APIError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        if requiresAuth {
            guard let token = tokenStore.accessToken else {
                throw APIError.unauthorized
            }
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        if let body {
            request.httpBody = try JSONEncoder().encode(AnyEncodable(body))
        }

        let data: Data
        let response: URLResponse

        do {
            (data, response) = try await session.data(for: request)
        } catch {
            throw APIError.network(error)
        }

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }

        if (200 ..< 300).contains(httpResponse.statusCode) {
            return data
        }

        if httpResponse.statusCode == 401 {
            throw APIError.unauthorized
        }

        let message = (try? JSONDecoder().decode(APIErrorResponse.self, from: data).detail) ?? ""
        throw APIError.server(statusCode: httpResponse.statusCode, message: message)
    }

    private func buildURL(path: String, queryItems: [URLQueryItem]) -> URL? {
        guard let baseURL = URL(string: path, relativeTo: AppConfig.baseURL) else {
            return nil
        }

        guard !queryItems.isEmpty else {
            return baseURL
        }

        guard var components = URLComponents(url: baseURL, resolvingAgainstBaseURL: true) else {
            return nil
        }

        var merged = components.queryItems ?? []
        merged.append(contentsOf: queryItems)
        components.queryItems = merged
        return components.url
    }

    private func refreshTokenIfPossible() async throws -> Bool {
        guard let refreshToken = tokenStore.refreshToken else {
            return false
        }

        let refreshBody = RefreshTokenRequest(refresh_token: refreshToken)

        guard let url = buildURL(path: "auth/refresh", queryItems: []) else {
            throw APIError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(refreshBody)

        let data: Data
        let response: URLResponse
        do {
            (data, response) = try await session.data(for: request)
        } catch {
            throw APIError.network(error)
        }

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }

        guard (200 ..< 300).contains(httpResponse.statusCode) else {
            return false
        }

        do {
            let tokenResponse = try JSONDecoder().decode(RefreshTokenResponse.self, from: data)
            tokenStore.updateTokens(accessToken: tokenResponse.token, refreshToken: tokenResponse.refresh_token)
            return true
        } catch {
            throw APIError.decoding(error)
        }
    }
}

private struct AnyEncodable: Encodable {
    private let encodeFn: (Encoder) throws -> Void

    init(_ wrapped: Encodable) {
        self.encodeFn = wrapped.encode
    }

    func encode(to encoder: Encoder) throws {
        try encodeFn(encoder)
    }
}

private struct APIErrorResponse: Decodable {
    let detail: String
}
