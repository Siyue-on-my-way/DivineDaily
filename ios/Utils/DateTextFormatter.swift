import Foundation

/// 将服务端返回的时间字符串做一个“尽量可读”的展示格式
enum DateTextFormatter {
    static func format(_ raw: String) -> String {
        // 兜底：原样返回
        if raw.isEmpty { return "-" }

        // 常见的 ISO8601 格式
        let iso = ISO8601DateFormatter()
        iso.formatOptions = [.withInternetDateTime, .withFractionalSeconds]

        if let date = iso.date(from: raw) {
            let fmt = DateFormatter()
            fmt.dateFormat = "yyyy-MM-dd HH:mm"
            return fmt.string(from: date)
        }

        // 另一种 ISO8601（无小数秒）
        let iso2 = ISO8601DateFormatter()
        iso2.formatOptions = [.withInternetDateTime]
        if let date = iso2.date(from: raw) {
            let fmt = DateFormatter()
            fmt.dateFormat = "yyyy-MM-dd HH:mm"
            return fmt.string(from: date)
        }

        return raw
    }
}

