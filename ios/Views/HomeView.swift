import SwiftUI

struct HomeView: View {
    @EnvironmentObject private var authStore: AuthStore

    var body: some View {
        NavigationView {
            List {
                Section {
                    VStack(alignment: .leading, spacing: 6) {
                        Text("你好，\(authStore.user?.username ?? "用户")")
                            .font(.headline)
                        Text("Phase 2.1：塔罗+历史详情+每日运势")
                            .font(.footnote)
                            .foregroundColor(.secondary)
                    }
                    .padding(.vertical, 4)
                }

                Section("占卜") {
                    NavigationLink {
                        IChingDivinationView(authStore: authStore)
                    } label: {
                        Label("周易占卜", systemImage: "sparkles")
                    }

                    NavigationLink {
                        TarotFlowView(authStore: authStore)
                    } label: {
                        Label("塔罗占卜", systemImage: "rectangle.stack.fill")
                    }
                }

                Section("数据") {
                    NavigationLink {
                        HistoryView(authStore: authStore)
                    } label: {
                        Label("历史记录", systemImage: "clock.arrow.circlepath")
                    }

                    NavigationLink {
                        FortuneView(authStore: authStore)
                    } label: {
                        Label("每日运势", systemImage: "sun.max.fill")
                    }
                }

                Section("账号与分享") {
                    NavigationLink {
                        ProfileView(authStore: authStore)
                    } label: {
                        Label("个人资料", systemImage: "person.crop.circle")
                    }

                    NavigationLink {
                        ShareView(authStore: authStore)
                    } label: {
                        Label("创建分享", systemImage: "square.and.arrow.up")
                    }
                }

                Section {
                    Button(role: .destructive) {
                        authStore.logout()
                    } label: {
                        Text("退出登录")
                    }
                }
            }
            .navigationTitle("DivineDaily")
        }
        .navigationViewStyle(.stack)
    }
}
