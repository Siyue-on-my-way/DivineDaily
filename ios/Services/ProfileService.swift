import Foundation

final class ProfileService {
    private let client: HTTPClient

    init(client: HTTPClient) {
        self.client = client
    }

    func getMyProfile() async throws -> UserProfile {
        let dto: UserProfileDTO = try await client.request(
            path: "profile",
            method: "GET",
            body: nil,
            requiresAuth: true
        )
        return UserProfile(dto: dto)
    }

    func updateMyProfile(birthDate: String, birthTime: String?) async throws -> UserProfile {
        let body = UserProfileUpdateRequest(birth_date: birthDate, birth_time: birthTime)
        let dto: UserProfileDTO = try await client.request(
            path: "profile",
            method: "PUT",
            body: body,
            requiresAuth: true
        )
        return UserProfile(dto: dto)
    }
}
