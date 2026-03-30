import Foundation

final class SaveService {
    private let client: HTTPClient

    init(client: HTTPClient) {
        self.client = client
    }

    func save(sessionId: String) async throws {
        _ = try await client.requestVoid(
            path: "divinations/\(sessionId)/save",
            method: "POST",
            body: nil,
            requiresAuth: true
        )
    }
}
