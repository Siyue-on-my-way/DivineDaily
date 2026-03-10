import Foundation

struct UserProfileDTO: Decodable {
    let id: Int
    let user_id: Int
    let birth_date: String?
    let birth_time: String?
    let lunar_birth: String?
    let animal: String?
    let zodiac_sign: String?
    let bazi: String?
}

struct UserProfileUpdateRequest: Encodable {
    let birth_date: String?
    let birth_time: String?
}

struct UserProfile: Equatable {
    let id: Int
    let userId: Int
    let birthDate: String
    let birthTime: String
    let lunarBirth: String
    let animal: String
    let zodiacSign: String
    let bazi: String

    init(dto: UserProfileDTO) {
        self.id = dto.id
        self.userId = dto.user_id
        self.birthDate = dto.birth_date ?? ""
        self.birthTime = dto.birth_time ?? ""
        self.lunarBirth = dto.lunar_birth ?? ""
        self.animal = dto.animal ?? ""
        self.zodiacSign = dto.zodiac_sign ?? ""
        self.bazi = dto.bazi ?? ""
    }
}
