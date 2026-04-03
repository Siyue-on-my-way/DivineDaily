import Foundation

final class DivinationService {
    private let client: HTTPClient

    init(client: HTTPClient) {
        self.client = client
    }

    func startIChing(userId: String, question: String) async throws -> DivinationResult {
        let request = StartDivinationRequest(
            user_id: userId,
            question: question,
            version: "CN",
            orientation: "E",
            event_type: nil,
            spread: nil,
            context: nil
        )

        let accepted: DivinationTaskAcceptedDTO = try await client.request(
            path: "divinations/start",
            method: "POST",
            body: request,
            requiresAuth: true
        )

        // 后端为异步任务模型：先返回 processing，再由轮询获取结果
        return DivinationResult(dto: DivinationResultDTO(
            session_id: accepted.session_id,
            status: accepted.status ?? "processing",
            outcome: nil,
            title: nil,
            spread: nil,
            summary: nil,
            detail: nil,
            created_at: accepted.created_at,
            processing_type: nil,
            hexagram_info: nil,
            cards: nil,
            daily_fortune: nil,
            quality: nil,
            yarrow_trace: nil
        ))
    }

    func startTarot(
        userId: String,
        question: String,
        spread: String,
        cutPosition: Int,
        shuffleTrace: [Int]
    ) async throws -> DivinationResult {
        let tarotInteraction = TarotInteraction(
            spread: spread,
            cut_position: cutPosition,
            shuffle_trace: shuffleTrace
        )
        let context = DivinationContext(tarot_interaction: tarotInteraction)

        let request = StartDivinationRequest(
            user_id: userId,
            question: question,
            version: "TAROT",
            orientation: "E",
            event_type: nil,
            spread: spread,
            context: context
        )

        let accepted: DivinationTaskAcceptedDTO = try await client.request(
            path: "divinations/start",
            method: "POST",
            body: request,
            requiresAuth: true
        )

        // 后端为异步任务模型：先返回 processing，再由轮询获取结果
        return DivinationResult(dto: DivinationResultDTO(
            session_id: accepted.session_id,
            status: accepted.status ?? "processing",
            outcome: nil,
            title: nil,
            spread: spread,
            summary: nil,
            detail: nil,
            created_at: accepted.created_at,
            processing_type: nil,
            hexagram_info: nil,
            cards: nil,
            daily_fortune: nil,
            quality: nil,
            yarrow_trace: nil
        ))
    }

    func getResult(sessionId: String) async throws -> DivinationResult {
        let dto: DivinationResultDTO = try await client.request(
            path: "divinations/\(sessionId)",
            method: "GET",
            body: nil,
            requiresAuth: true
        )
        return DivinationResult(dto: dto)
    }

    // GET /divinations/history
    func listHistory(
        limit: Int,
        offset: Int,
        eventType: String?,
        version: String?,
        status: String?,
        startDate: String?,
        endDate: String?,
        orderBy: String?,
        orderDirection: String?
    ) async throws -> DivinationHistoryListResponseDTO {
        var queryItems: [URLQueryItem] = [
            URLQueryItem(name: "limit", value: String(limit)),
            URLQueryItem(name: "offset", value: String(offset))
        ]

        if let eventType, !eventType.isEmpty { queryItems.append(URLQueryItem(name: "event_type", value: eventType)) }
        if let version, !version.isEmpty { queryItems.append(URLQueryItem(name: "version", value: version)) }
        if let status, !status.isEmpty { queryItems.append(URLQueryItem(name: "status", value: status)) }
        if let startDate, !startDate.isEmpty { queryItems.append(URLQueryItem(name: "start_date", value: startDate)) }
        if let endDate, !endDate.isEmpty { queryItems.append(URLQueryItem(name: "end_date", value: endDate)) }
        if let orderBy, !orderBy.isEmpty { queryItems.append(URLQueryItem(name: "order_by", value: orderBy)) }
        if let orderDirection, !orderDirection.isEmpty { queryItems.append(URLQueryItem(name: "order_direction", value: orderDirection)) }

        var components = URLComponents()
        components.queryItems = queryItems
        let query = components.percentEncodedQuery ?? ""
        let path = query.isEmpty ? "divinations/history" : "divinations/history?\(query)"

        let dto: DivinationHistoryListResponseDTO = try await client.request(
            path: path,
            method: "GET",
            body: nil,
            requiresAuth: true
        )
        return dto
    }

    // MARK: - Local helper

    private struct DivinationTaskAcceptedDTO: Decodable {
        let accepted: Bool
        let session_id: String
        let status: String?
        let status_url: String?
        let message: String?
        let created_at: String?
    }
}
