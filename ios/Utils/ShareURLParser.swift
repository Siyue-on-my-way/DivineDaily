import Foundation

/// 从系统 `onOpenURL` 或用户粘贴的字符串中解析分享 token
enum ShareURLParser {
    /// 从 URL 解析（Universal Links、前端页 `/share/{token}`、自定义 scheme 等）
    static func shareToken(from url: URL) -> String? {
        let path = url.path

        if let range = path.range(of: "/share/") {
            let rest = String(path[range.upperBound...])
                .trimmingCharacters(in: .whitespacesAndNewlines)
            if !rest.isEmpty { return rest.split(separator: "/").first.map(String.init) ?? rest }
        }

        let parts = path.split(separator: "/").map(String.init)
        if let i = parts.lastIndex(of: "shares"), i + 1 < parts.count {
            let t = parts[i + 1]
            if t != "share" && !t.isEmpty { return t }
        }

        // divinedaily://share/<token> 或 divinedaily://share/<token>（host=share）
        if url.scheme?.lowercased() == "divinedaily", url.host?.lowercased() == "share" {
            let p = url.path.trimmingCharacters(in: CharacterSet(charactersIn: "/"))
            if !p.isEmpty { return p.split(separator: "/").first.map(String.init) ?? p }
        }

        return nil
    }

    /// 用户粘贴「纯 token」或「完整 https 链接」
    static func token(from userInput: String) -> String {
        let trimmed = userInput.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return "" }

        if let url = URL(string: trimmed), url.scheme != nil {
            if let t = shareToken(from: url) { return t }
        }

        return trimmed
    }
}
