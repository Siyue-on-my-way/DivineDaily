import SwiftUI

struct AuthGateView: View {
    @EnvironmentObject private var authStore: AuthStore

    var body: some View {
        Group {
            if authStore.isAuthenticated {
                HomeView()
            } else {
                LoginView(authStore: authStore)
            }
        }
        .task {
            // token 存在但用户信息还没同步时，拉取一下 /auth/me
            if authStore.isAuthenticated && authStore.user == nil {
                await authStore.syncUser()
            }
        }
    }
}

