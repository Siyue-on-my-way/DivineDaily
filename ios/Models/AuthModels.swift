import Foundation

struct UserDTO: Decodable {
    let id: Int
    let username: String
    let email: String?
    let phone: String?
    let nickname: String?
    let avatar: String?
    let role: String
    let status: Int?
    let created_at: String?

    enum CodingKeys: String, CodingKey {
        case id
        case username
        case email
        case phone
        case nickname
        case avatar
        case role
        case status
        case created_at
    }
}

struct TokenResponseDTO: Decodable {
    let token: String
    let refresh_token: String
    let token_type: String?
    let user: UserDTO

    enum CodingKeys: String, CodingKey {
        case token
        case refresh_token
        case token_type
        case user
    }
}

struct RefreshTokenRequest: Encodable {
    let refresh_token: String
}

struct LoginRequestDTO: Encodable {
    let username: String
    let password: String
}

struct RegisterRequestDTO: Encodable {
    let username: String
    let email: String?
    let password: String
    let confirm_password: String
}

struct MeResponseDTO: Decodable {
    let user: UserDTO
}

