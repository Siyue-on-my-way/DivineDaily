import Foundation

struct UserProfileDTO: Decodable {
    let id: Int
    let user_id: Int

    let nickname: String?
    let avatar: String?
    let gender: String?
    let birth_date: String?
    let birth_time: String?
    let birth_place: String?
    let preferred_divination: String?
    let notification_enabled: Bool?
    let notification_time: String?
    let bio: String?
    let interests: String?

    let lunar_birth: String
    let animal: String
    let zodiac_sign: String
    let bazi: String
    let created_at: String?
    let updated_at: String?
}

struct UserProfile: Equatable {
    let id: Int
    let userId: Int

    let nickname: String?
    let avatar: String?
    let gender: String?
    let birthDate: String?
    let birthTime: String?
    let birthPlace: String?

    let preferredDivination: String?
    let notificationEnabled: Bool?
    let notificationTime: String?
    let bio: String?
    let interests: String?

    let lunarBirth: String
    let animal: String
    let zodiacSign: String
    let bazi: String
    let createdAt: String?
    let updatedAt: String?

    init(dto: UserProfileDTO) {
        self.id = dto.id
        self.userId = dto.user_id

        self.nickname = dto.nickname
        self.avatar = dto.avatar
        self.gender = dto.gender
        self.birthDate = dto.birth_date
        self.birthTime = dto.birth_time
        self.birthPlace = dto.birth_place

        self.preferredDivination = dto.preferred_divination
        self.notificationEnabled = dto.notification_enabled
        self.notificationTime = dto.notification_time
        self.bio = dto.bio
        self.interests = dto.interests

        self.lunarBirth = dto.lunar_birth
        self.animal = dto.animal
        self.zodiacSign = dto.zodiac_sign
        self.bazi = dto.bazi
        self.createdAt = dto.created_at
        self.updatedAt = dto.updated_at
    }
}

struct UserProfileUpdateRequest: Encodable {
    let nickname: String?
    let avatar: String?
    let gender: String?
    let birth_date: String?
    let birth_time: String?
    let birth_place: String?
    let preferred_divination: String?
    let notification_enabled: Bool?
    let notification_time: String?
    let bio: String?
    let interests: String?
}

