import SwiftUI

private struct ShareTokenPresentation: Identifiable {
    let id: String
    var token: String { id }
    init(_ token: String) { self.id = token }
}

@main
struct DivineDailyApp: App {
    @StateObject private var authStore = AuthStore()
    @State private var openedShare: ShareTokenPresentation?

    var body: some Scene {
        WindowGroup {
            AuthGateView()
                .environmentObject(authStore)
                .onOpenURL { url in
                    if let t = ShareURLParser.shareToken(from: url) {
                        openedShare = ShareTokenPresentation(t)
                    }
                }
                .fullScreenCover(item: $openedShare) { pres in
                    NavigationStack {
                        ShareView(shareTokenOrURL: pres.token, showDismissButton: true)
                    }
                }
        }
    }
}

