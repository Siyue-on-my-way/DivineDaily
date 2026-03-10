import Foundation

struct AppUser: Codable, Equatable {
    let id: Int
    let username: String
    let email: String?
    let role: String?

    init(id: Int, username: String, email: String?, role: String?) {
        self.id = id
        self.username = username
        self.email = email
        self.role = role
    }

    init(dto: UserDTO) {
        self.init(id: dto.id, username: dto.username, email: dto.email, role: dto.role)
    }

    init(dto: CurrentUserResponse) {
        self.init(id: dto.id, username: dto.username, email: dto.email, role: dto.role)
    }
}
