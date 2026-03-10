import Foundation

struct StartDivinationRequest: Encodable {
    let user_id: String
    let question: String
    let version: String
    let orientation: String
    let event_type: String?
    let spread: String?
    let context: DivinationContext?
}

struct DivinationContext: Encodable {
    let tarot_interaction: TarotInteraction?
}

struct TarotInteraction: Encodable {
    let spread: String
    let cut_position: Int
    let shuffle_trace: [Int]
}

struct DivinationResultDTO: Decodable {
    let session_id: String
    let status: String?
    let outcome: String?
    let title: String?
    let spread: String?
    let summary: String?
    let detail: String?
    let created_at: String?
    let processing_type: String?
    let hexagram_info: HexagramInfoDTO?
    let cards: [TarotCardDTO]?
    let daily_fortune: DailyFortuneEmbeddedDTO?
    let quality: DivinationQualityDTO?
}

struct DailyFortuneEmbeddedDTO: Decodable {
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

struct DivinationQualityDTO: Decodable {
    let level: String?
    let reason: String?
    let suggestions: [String]?
}

struct HexagramInfoDTO: Decodable {
    let number: Int?
    let name: String?
    let upper_trigram: String?
    let lower_trigram: String?
    let outcome: String?
    let summary: String?
    let detail: String?
    let wuxing: String?
    let changing_lines: [Int]?
    let line_values: [Int]?
}

struct TarotCardDTO: Decodable {
    let name: String?
    let name_en: String?
    let position: String?
    let is_reversed: Bool?
    let meaning: String?
}

struct DivinationResult: Equatable {
    let sessionId: String
    let status: String?
    let outcome: String?
    let title: String?
    let spread: String?
    let summary: String
    let detail: String
    let createdAt: String?
    let processingType: String?
    let hexagramInfo: HexagramInfo?
    let cards: [TarotCard]
    let dailyFortune: DailyFortuneEmbedded?
    let quality: DivinationQuality?

    init(dto: DivinationResultDTO) {
        self.sessionId = dto.session_id
        self.status = dto.status
        self.outcome = dto.outcome
        self.title = dto.title
        self.spread = dto.spread
        self.summary = dto.summary ?? ""
        self.detail = dto.detail ?? ""
        self.createdAt = dto.created_at
        self.processingType = dto.processing_type
        self.hexagramInfo = dto.hexagram_info.map(HexagramInfo.init)
        self.cards = (dto.cards ?? []).map(TarotCard.init)
        self.dailyFortune = dto.daily_fortune.map(DailyFortuneEmbedded.init)
        self.quality = dto.quality.map(DivinationQuality.init)
    }
}

struct DailyFortuneEmbedded: Equatable {
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

    init(dto: DailyFortuneEmbeddedDTO) {
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

struct DivinationQuality: Equatable {
    let level: String
    let reason: String
    let suggestions: [String]

    init(dto: DivinationQualityDTO) {
        self.level = dto.level ?? ""
        self.reason = dto.reason ?? ""
        self.suggestions = dto.suggestions ?? []
    }
}

struct HexagramInfo: Equatable {
    let number: Int?
    let name: String?
    let upperTrigram: String?
    let lowerTrigram: String?
    let outcome: String?
    let summary: String?
    let detail: String?
    let wuxing: String?
    let changingLines: [Int]
    let lineValues: [Int]

    init(dto: HexagramInfoDTO) {
        self.number = dto.number
        self.name = dto.name
        self.upperTrigram = dto.upper_trigram
        self.lowerTrigram = dto.lower_trigram
        self.outcome = dto.outcome
        self.summary = dto.summary
        self.detail = dto.detail
        self.wuxing = dto.wuxing
        self.changingLines = dto.changing_lines ?? []
        self.lineValues = dto.line_values ?? []
    }
}

struct TarotCard: Equatable {
    let name: String
    let englishName: String
    let position: String
    let isReversed: Bool
    let meaning: String

    init(dto: TarotCardDTO) {
        self.name = dto.name ?? ""
        self.englishName = dto.name_en ?? ""
        self.position = dto.position ?? ""
        self.isReversed = dto.is_reversed ?? false
        self.meaning = dto.meaning ?? ""
    }
}
