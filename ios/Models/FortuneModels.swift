import Foundation

struct DailyFortuneInfoDTO: Decodable {
    let overall_score: Int?
    let wealth_score: Int?
    let career_score: Int?
    let love_score: Int?
    let health_score: Int?

    let content: String?
    let lucky_color: String?
    let lucky_number: Int?
    let lucky_direction: String?
    let lucky_time: String?

    let yi: String?
    let ji: String?
}

struct FortuneInfo: Equatable {
    let overallScore: Int
    let wealthScore: Int
    let careerScore: Int
    let loveScore: Int
    let healthScore: Int

    let content: String
    let luckyColor: String
    let luckyNumber: Int
    let luckyDirection: String
    let luckyTime: String

    let yi: String
    let ji: String

    init(dto: DailyFortuneInfoDTO) {
        self.overallScore = dto.overall_score ?? 0
        self.wealthScore = dto.wealth_score ?? 0
        self.careerScore = dto.career_score ?? 0
        self.loveScore = dto.love_score ?? 0
        self.healthScore = dto.health_score ?? 0

        self.content = dto.content ?? ""
        self.luckyColor = dto.lucky_color ?? ""
        self.luckyNumber = dto.lucky_number ?? 0
        self.luckyDirection = dto.lucky_direction ?? ""
        self.luckyTime = dto.lucky_time ?? ""

        self.yi = dto.yi ?? ""
        self.ji = dto.ji ?? ""
    }
}

