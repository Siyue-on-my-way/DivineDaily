import Foundation

struct ShareLinkItem: Identifiable {
    let id = UUID()
    let url: URL

    init?(urlString: String) {
        guard let url = URL(string: urlString) else { return nil }
        self.url = url
    }
}
