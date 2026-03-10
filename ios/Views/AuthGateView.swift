import SwiftUI

struct AuthGateView: View {
    @EnvironmentObject private var authStore: AuthStore

    var body: some View {
        Group {
            if authStore.isLoading {
                ProgressView("加载中...")
            } else if authStore.isAuthenticated {
                HomeView()
            } else {
                LoginView()
            }
        }
    }
}
