import Foundation

struct DailyFortuneDTO: Decodable {
    let overall_score: Int
    let wealth_score: Int
    let career_score: Int
    let love_score: Int
    let health_score: Int
    let content: String
    let lucky_color: String
    let lucky_number: Int
    let lucky_direction: String
    let lucky_time: String
    let yi: String
    let ji: String
    let solar_term: String
    let festival: String
}

struct DailyFortune: Equatable {
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
    let solarTerm: String
    let festival: String

    init(dto: DailyFortuneDTO) {
        self.overallScore = dto.overall_score
        self.wealthScore = dto.wealth_score
        self.careerScore = dto.career_score
        self.loveScore = dto.love_score
        self.healthScore = dto.health_score
        self.content = dto.content
        self.luckyColor = dto.lucky_color
        self.luckyNumber = dto.lucky_number
        self.luckyDirection = dto.lucky_direction
        self.luckyTime = dto.lucky_time
        self.yi = dto.yi
        self.ji = dto.ji
        self.solarTerm = dto.solar_term
        self.festival = dto.festival
    }
}
