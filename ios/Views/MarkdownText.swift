import SwiftUI

struct MarkdownText: View {
    let markdown: String
    let fallback: String

    init(_ markdown: String, fallback: String = "") {
        self.markdown = markdown
        self.fallback = fallback
    }

    var body: some View {
        if let attributed = try? AttributedString(markdown: markdown) {
            Text(attributed)
        } else {
            Text(markdown.isEmpty ? fallback : markdown)
        }
    }
}
