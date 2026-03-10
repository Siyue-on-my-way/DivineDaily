import Foundation

enum DateTextFormatter {
    private static let isoParsers: [ISO8601DateFormatter] = {
        let f1 = ISO8601DateFormatter()
        f1.formatOptions = [.withInternetDateTime, .withFractionalSeconds]

        let f2 = ISO8601DateFormatter()
        f2.formatOptions = [.withInternetDateTime]

        return [f1, f2]
    }()

    private static let displayFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "zh_CN")
        formatter.dateFormat = "yyyy-MM-dd HH:mm"
        return formatter
    }()

    static func displayDateTime(from raw: String?) -> String {
        guard let raw, !raw.isEmpty else { return "" }

        for parser in isoParsers {
            if let date = parser.date(from: raw) {
                return displayFormatter.string(from: date)
            }
        }

        return raw
    }

    static func truncatedText(_ text: String, maxLength: Int = 120) -> String {
        guard text.count > maxLength else { return text }
        let end = text.index(text.startIndex, offsetBy: maxLength)
        return String(text[..<end]) + "..."
    }
}
