import Foundation

final class DivinationService {
    private let client: HTTPClient

    init(client: HTTPClient) {
        self.client = client
    }

    func getHistory(
        limit: Int = 20,
        offset: Int = 0,
        eventType: String? = nil,
        version: String? = nil,
        status: String? = nil,
        startDate: String? = nil,
        endDate: String? = nil,
        orderBy: String? = nil,
        orderDirection: String? = nil
    ) async throws -> DivinationHistoryResponse {
        var queryItems: [URLQueryItem] = [
            URLQueryItem(name: "limit", value: String(limit)),
            URLQueryItem(name: "offset", value: String(offset))
        ]

        if let eventType, !eventType.isEmpty {
            queryItems.append(URLQueryItem(name: "event_type", value: eventType))
        }
        if let version, !version.isEmpty {
            queryItems.append(URLQueryItem(name: "version", value: version))
        }
        if let status, !status.isEmpty {
            queryItems.append(URLQueryItem(name: "status", value: status))
        }
        if let startDate, !startDate.isEmpty {
            queryItems.append(URLQueryItem(name: "start_date", value: startDate))
        }
        if let endDate, !endDate.isEmpty {
            queryItems.append(URLQueryItem(name: "end_date", value: endDate))
        }
        if let orderBy, !orderBy.isEmpty {
            queryItems.append(URLQueryItem(name: "order_by", value: orderBy))
        }
        if let orderDirection, !orderDirection.isEmpty {
            queryItems.append(URLQueryItem(name: "order_direction", value: orderDirection))
        }

        let response: DivinationHistoryResponse = try await client.request(
            path: "divinations/history",
            method: "GET",
            body: nil,
            queryItems: queryItems,
            requiresAuth: true
        )
        return response
    }

    func startIChing(userId: Int, question: String) async throws -> DivinationResult {
        let body = StartDivinationRequest(
            user_id: String(userId),
            question: question,
            version: "CN",
            orientation: "E",
            event_type: "fortune",
            spread: nil,
            context: nil
        )

        let dto: DivinationResultDTO = try await client.request(
            path: "divinations/start",
            method: "POST",
            body: body,
            requiresAuth: true
        )

        return DivinationResult(dto: dto)
    }

    func startTarot(
        userId: Int,
        question: String,
        spread: String,
        cutPosition: Int,
        shuffleTrace: [Int]
    ) async throws -> DivinationResult {
        let body = StartDivinationRequest(
            user_id: String(userId),
            question: question,
            version: "TAROT",
            orientation: "E",
            event_type: nil,
            spread: spread,
            context: DivinationContext(
                tarot_interaction: TarotInteraction(
                    spread: spread,
                    cut_position: cutPosition,
                    shuffle_trace: Array(shuffleTrace.suffix(20))
                )
            )
        )

        let dto: DivinationResultDTO = try await client.request(
            path: "divinations/start",
            method: "POST",
            body: body,
            requiresAuth: true
        )

        return DivinationResult(dto: dto)
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
}
