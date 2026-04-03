import Foundation

enum DivinationPollingHelper {
    /// 轮询直到 `isCompleted` 为 true
    static func pollResult<T>(
        sessionId: String,
        fetch: (String) async throws -> T,
        isCompleted: (T) -> Bool,
        intervalSeconds: Double = 2.0,
        timeoutSeconds: Double = 60.0
    ) async throws -> T? {
        let start = Date()

        while Date().timeIntervalSince(start) < timeoutSeconds {
            let current = try await fetch(sessionId)
            if isCompleted(current) {
                return current
            }

            // 不阻塞主线程
            let nanos = UInt64(intervalSeconds * 1_000_000_000)
            try await Task.sleep(nanoseconds: nanos)
        }

        return nil
    }
}

