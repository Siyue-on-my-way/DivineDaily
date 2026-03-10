import SwiftUI

struct ShareView: View {
    @StateObject private var store: ShareStore
    @StateObject private var historyStore: HistoryStore
    @State private var sessionIdInput: String = ""
    @State private var sessionSearchKeyword: String = ""
    @State private var expiresDays: Int = 7
    @State private var isPublic: Bool = true

    init(authStore: AuthStore) {
        _store = StateObject(wrappedValue: ShareStore(authStore: authStore))
        _historyStore = StateObject(wrappedValue: HistoryStore(authStore: authStore))
    }

    var body: some View {
        Form {
            SessionSelectorSection(
                items: historyStore.items,
                selectedSessionId: $sessionIdInput,
                keyword: $sessionSearchKeyword
            )

            Section("创建分享") {
                TextField("session_id", text: $sessionIdInput)
                    .textInputAutocapitalization(.never)
                    .autocorrectionDisabled()

                Stepper("有效期：\(expiresDays) 天", value: $expiresDays, in: 1...30)

                Toggle("公开分享", isOn: $isPublic)

                Button("生成分享链接") {
                    Task {
                        await store.createShare(
                            sessionId: sessionIdInput,
                            expiresDays: expiresDays,
                            isPublic: isPublic
                        )
                    }
                }
                .buttonStyle(.borderedProminent)
                .disabled(sessionIdInput.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)

                Button("刷新分享统计") {
                    Task { await store.loadStats(sessionId: sessionIdInput) }
                }
                .disabled(sessionIdInput.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
            }

            if let url = store.generatedURL {
                Section("分享链接") {
                    Text(url)
                        .font(.footnote)
                        .textSelection(.enabled)

                    ShareLink(item: url) {
                        Label("系统分享", systemImage: "square.and.arrow.up")
                    }
                }
            }

            if let stats = store.stats {
                Section("分享统计") {
                    HStack {
                        Text("分享数量")
                        Spacer()
                        Text("\(stats.totalShares)")
                            .foregroundColor(.secondary)
                    }
                    HStack {
                        Text("总浏览量")
                        Spacer()
                        Text("\(stats.totalViews)")
                            .foregroundColor(.secondary)
                    }
                }

                Section("分享列表") {
                    if stats.shares.isEmpty {
                        Text("暂无分享记录")
                            .foregroundColor(.secondary)
                    }

                    ForEach(stats.shares) { item in
                        VStack(alignment: .leading, spacing: 6) {
                            Text(item.url)
                                .font(.footnote)
                                .textSelection(.enabled)

                            HStack {
                                Text("浏览：\(item.viewCount)")
                                if item.isExpired {
                                    Text("已过期")
                                        .foregroundColor(.orange)
                                }
                                Spacer()
                                Button("删除") {
                                    Task {
                                        await store.deleteShare(shareToken: item.token, sessionId: sessionIdInput)
                                    }
                                }
                                .foregroundColor(.red)
                            }
                            .font(.caption)
                            .foregroundColor(.secondary)
                        }
                    }
                }
            }

            if let error = store.errorMessage {
                Section {
                    CommonErrorBanner(message: error)
                }
            }
        }
        .navigationTitle("分享")
        .overlay {
            if store.isLoading {
                ProgressView("处理中...")
            }
        }
        .task {
            await historyStore.load()
        }
    }
}
