import Foundation

struct AppUser: Identifiable, Equatable {
    let id: String
    let username: String
    let email: String?
    let phone: String?
    let nickname: String?
    let avatar: String?
    let role: String
    let status: Int?
    let createdAt: String?

    init(dto: UserDTO) {
        self.id = String(dto.id)
        self.username = dto.username
        self.email = dto.email
        self.phone = dto.phone
        self.nickname = dto.nickname
        self.avatar = dto.avatar
        self.role = String(describing: dto.role)
        self.status = dto.status
        self.createdAt = dto.created_at
    }
}

