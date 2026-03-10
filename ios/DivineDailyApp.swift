import SwiftUI

@main
struct DivineDailyApp: App {
    @StateObject private var authStore = AuthStore()

    var body: some Scene {
        WindowGroup {
            AuthGateView()
                .environmentObject(authStore)
                .task {
                    await authStore.bootstrap()
                }
        }
    }
}
