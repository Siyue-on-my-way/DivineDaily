import Foundation

struct DivinationPollingHelper {
    static func pollResult(
        sessionId: String,
        maxAttempts: Int = 30,
        intervalNanoseconds: UInt64 = 1_000_000_000,
        fetch: @escaping (String) async throws -> DivinationResult,
        isCompleted: @escaping (DivinationResult) -> Bool
    ) async throws -> DivinationResult? {
        for _ in 0..<maxAttempts {
            if Task.isCancelled { return nil }

            do {
                let current = try await fetch(sessionId)
                if isCompleted(current) {
                    return current
                }
            } catch {
                // 轮询期间忽略瞬时错误
            }

            try? await Task.sleep(nanoseconds: intervalNanoseconds)
        }

        return nil
    }
}
