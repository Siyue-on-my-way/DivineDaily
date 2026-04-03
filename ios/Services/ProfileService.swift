import Foundation

final class ProfileService {
    private let client: HTTPClient

    init(client: HTTPClient) {
        self.client = client
    }

    func getMyProfile() async throws -> UserProfileDTO {
        let dto: UserProfileDTO = try await client.request(
            path: "profile",
            method: "GET",
            body: nil,
            requiresAuth: true
        )
        return dto
    }

    func updateMyProfile(_ request: UserProfileUpdateRequest) async throws -> UserProfileDTO {
        let dto: UserProfileDTO = try await client.request(
            path: "profile",
            method: "PUT",
            body: request,
            requiresAuth: true
        )
        return dto
    }
}

