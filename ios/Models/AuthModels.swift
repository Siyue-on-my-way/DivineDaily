import Foundation

struct LoginRequest: Encodable {
    let username: String
    let password: String
}

struct RegisterRequest: Encodable {
    let username: String
    let email: String
    let password: String
}

struct RefreshTokenRequest: Encodable {
    let refresh_token: String
}

struct TokenResponse: Decodable {
    let token: String
    let refresh_token: String
    let user: UserDTO
}

struct RefreshTokenResponse: Decodable {
    let token: String
    let refresh_token: String
    let token_type: String
}

struct UserDTO: Decodable {
    let id: Int
    let username: String
    let email: String?
    let role: String?
}

struct CurrentUserResponse: Decodable {
    let id: Int
    let username: String
    let email: String?
    let role: String?
}
