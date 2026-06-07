import SwiftUI

struct HomeView: View {
    @EnvironmentObject private var authStore: AuthStore

    var body: some View {
        NavigationStack {
            List {
                Section("占卜") {
                    NavigationLink {
                        IChingDivinationView(authStore: authStore)
                    } label: {
                        Text("周易占卜（起卦）")
                    }

                    NavigationLink {
                        TarotFlowView(authStore: authStore)
                    } label: {
                        Text("塔罗占卜")
                    }
                }

                Section("运势与记录") {
                    NavigationLink {
                        FortuneView(authStore: authStore)
                    } label: {
                        Text("每日运势")
                    }

                    NavigationLink {
                        HistoryView(authStore: authStore)
                    } label: {
                        Text("占卜历史")
                    }

                    NavigationLink {
                        InsightsView(authStore: authStore)
                    } label: {
                        Text("我的洞察")
                    }
                }

                Section("分享") {
                    NavigationLink {
                        ShareEntryView()
                    } label: {
                        Text("打开分享链接")
                    }
                }

                Section("用户") {
                    NavigationLink {
                        ProfileView(authStore: authStore)
                    } label: {
                        Text("用户档案")
                    }

                    Button(role: .destructive) {
                        authStore.logout()
                    } label: {
                        Text("退出登录")
                    }
                }
            }
            .navigationTitle("首页")
        }
    }
}

