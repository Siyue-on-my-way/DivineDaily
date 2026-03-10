import SwiftUI

struct HistoryView: View {
    @EnvironmentObject private var authStore: AuthStore
    @StateObject private var store: HistoryStore

    @State private var eventType = ""
    @State private var version = ""
    @State private var status = ""

    init(authStore: AuthStore) {
        _store = StateObject(wrappedValue: HistoryStore(authStore: authStore))
    }

    var body: some View {
        List {
            Section("筛选") {
                Picker("类型", selection: $eventType) {
                    Text("全部").tag("")
                    Text("决策").tag("decision")
                    Text("事业").tag("career")
                    Text("感情").tag("relationship")
                    Text("运势").tag("fortune")
                    Text("知识").tag("knowledge")
                }

                Picker("版本", selection: $version) {
                    Text("全部").tag("")
                    Text("周易").tag("CN")
                    Text("塔罗").tag("TAROT")
                    Text("Global").tag("Global")
                }

                Picker("状态", selection: $status) {
                    Text("全部").tag("")
                    Text("进行中").tag("pending")
                    Text("已完成").tag("completed")
                    Text("失败").tag("failed")
                }

                Button("应用筛选") {
                    Task {
                        await store.applyFilters(eventType: eventType, version: version, status: status)
                    }
                }
            }

            if let error = store.errorMessage {
                Section {
                    CommonErrorBanner(message: error)
                }
            }

            Section("占卜记录（共 \(store.items.count)/\(store.total) 条）") {
                if store.items.isEmpty, !store.isLoading {
                    Text("暂无占卜历史")
                        .foregroundColor(.secondary)
                }

                ForEach(store.items) { item in
                    NavigationLink {
                        HistoryDetailView(authStore: authStore, item: item)
                    } label: {
                        VStack(alignment: .leading, spacing: 6) {
                            Text(item.question.isEmpty ? "（未命名问题）" : item.question)
                                .font(.subheadline)
                                .lineLimit(2)

                            HStack {
                                Text(item.outcome.isEmpty ? "已完成" : item.outcome)
                                    .font(.caption)
                                    .foregroundColor(.indigo)

                                if !item.version.isEmpty {
                                    Text("· \(item.version)")
                                        .font(.caption2)
                                        .foregroundColor(.secondary)
                                }

                                Spacer()
                                Text(item.createdAt)
                                    .font(.caption2)
                                    .foregroundColor(.secondary)
                            }
                        }
                        .padding(.vertical, 4)
                    }
                    .task {
                        await store.loadMoreIfNeeded(currentItem: item)
                    }
                }

                if store.isLoadingMore {
                    HStack {
                        Spacer()
                        ProgressView("加载更多...")
                        Spacer()
                    }
                }
            }
        }
        .overlay {
            if store.isLoading {
                ProgressView("加载中...")
            }
        }
        .navigationTitle("历史记录")
        .task {
            await store.load()
        }
        .refreshable {
            await store.load()
        }
    }
}

struct HistoryDetailView: View {
    @StateObject private var store: HistoryDetailStore
    @StateObject private var shareStore: ShareStore
    @State private var shareExpiresDays: Int = 7
    @State private var shareIsPublic: Bool = true
    let item: DivinationHistoryItem

    init(authStore: AuthStore, item: DivinationHistoryItem) {
        self.item = item
        _store = StateObject(wrappedValue: HistoryDetailStore(authStore: authStore))
        _shareStore = StateObject(wrappedValue: ShareStore(authStore: authStore))
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 12) {
                Text(item.question.isEmpty ? "（未命名问题）" : item.question)
                    .font(.title3)
                    .bold()

                if let error = store.errorMessage {
                    CommonErrorBanner(message: error)
                }

                if store.isLoading {
                    ProgressView("加载完整详情...")
                }

                if let result = store.result {
                    if let outcome = result.outcome, !outcome.isEmpty {
                        Text("结果：\(outcome)")
                            .foregroundColor(.indigo)
                    }

                    if let processingType = result.processingType, !processingType.isEmpty {
                        Text("处理流程：\(processingType)")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }

                    if !result.summary.isEmpty {
                        GroupBox("摘要") {
                            Text(result.summary)
                                .frame(maxWidth: .infinity, alignment: .leading)
                        }
                    }

                    if !result.detail.isEmpty {
                        GroupBox("详细解读") {
                            Text(result.detail)
                                .frame(maxWidth: .infinity, alignment: .leading)
                                .font(.footnote)
                                .foregroundColor(.secondary)
                        }
                    }

                    if let hexagram = result.hexagramInfo {
                        GroupBox("卦象信息") {
                            VStack(alignment: .leading, spacing: 6) {
                                Text("卦名：\(hexagram.name ?? "")")
                                if let number = hexagram.number {
                                    Text("卦序：\(number)")
                                }
                                if let upper = hexagram.upperTrigram, let lower = hexagram.lowerTrigram {
                                    Text("上卦 / 下卦：\(upper) / \(lower)")
                                }
                                if let wuxing = hexagram.wuxing, !wuxing.isEmpty {
                                    Text("五行：\(wuxing)")
                                }
                            }
                            .font(.footnote)
                            .foregroundColor(.secondary)
                            .frame(maxWidth: .infinity, alignment: .leading)
                        }
                    }

                    if !result.cards.isEmpty {
                        GroupBox("塔罗牌") {
                            VStack(alignment: .leading, spacing: 8) {
                                ForEach(Array(result.cards.enumerated()), id: \.offset) { _, card in
                                    VStack(alignment: .leading, spacing: 3) {
                                        HStack {
                                            Text(card.name)
                                                .font(.subheadline)
                                            if card.isReversed {
                                                Text("逆位")
                                                    .font(.caption2)
                                                    .padding(.horizontal, 6)
                                                    .padding(.vertical, 2)
                                                    .background(Color.orange.opacity(0.2))
                                                    .clipShape(Capsule())
                                            }
                                        }
                                        Text("位置：\(card.position)")
                                            .font(.caption2)
                                            .foregroundColor(.secondary)
                                        if !card.meaning.isEmpty {
                                            Text(card.meaning)
                                                .font(.caption)
                                                .foregroundColor(.secondary)
                                        }
                                    }
                                    Divider()
                                }
                            }
                            .frame(maxWidth: .infinity, alignment: .leading)
                        }
                    }

                    if let daily = result.dailyFortune {
                        GroupBox("每日运势") {
                            VStack(alignment: .leading, spacing: 6) {
                                Text("综合：\(daily.overallScore)")
                                Text("财运/事业/感情/健康：\(daily.wealthScore)/\(daily.careerScore)/\(daily.loveScore)/\(daily.healthScore)")
                                Text("幸运色：\(daily.luckyColor)  幸运数字：\(daily.luckyNumber)")
                                Text("方位：\(daily.luckyDirection)  时辰：\(daily.luckyTime)")
                                if !daily.content.isEmpty {
                                    Text(daily.content)
                                }
                            }
                            .font(.footnote)
                            .foregroundColor(.secondary)
                            .frame(maxWidth: .infinity, alignment: .leading)
                        }
                    }

                    if let quality = result.quality {
                        GroupBox("问题质量评估") {
                            VStack(alignment: .leading, spacing: 6) {
                                Text("等级：\(quality.level)")
                                if !quality.reason.isEmpty {
                                    Text("原因：\(quality.reason)")
                                }
                                if !quality.suggestions.isEmpty {
                                    Text("建议：\(quality.suggestions.joined(separator: "、"))")
                                }
                            }
                            .font(.footnote)
                            .foregroundColor(.secondary)
                            .frame(maxWidth: .infinity, alignment: .leading)
                        }
                    }
                } else if !item.summary.isEmpty {
                    GroupBox("摘要") {
                        Text(item.summary)
                            .frame(maxWidth: .infinity, alignment: .leading)
                    }
                }

                GroupBox("分享") {
                    VStack(alignment: .leading, spacing: 8) {
                        Stepper("有效期：\(shareExpiresDays) 天", value: $shareExpiresDays, in: 1...30)
                        Toggle("公开分享", isOn: $shareIsPublic)

                        Button("创建分享") {
                            Task {
                                await shareStore.createShare(
                                    sessionId: item.id,
                                    expiresDays: shareExpiresDays,
                                    isPublic: shareIsPublic
                                )
                            }
                        }
                        .buttonStyle(.borderedProminent)

                        if let url = shareStore.generatedURL {
                            Text(url)
                                .font(.footnote)
                                .textSelection(.enabled)
                            ShareLink(item: url) {
                                Label("系统分享", systemImage: "square.and.arrow.up")
                            }
                        }

                        if let shareError = shareStore.errorMessage {
                            CommonErrorBanner(message: shareError)
                        }
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                }

                Text("时间：\(item.createdAt)")
                    .font(.footnote)
                    .foregroundColor(.secondary)
            }
            .padding(16)
        }
        .navigationTitle("记录详情")
        .task {
            await store.load(sessionId: item.id)
        }
    }
}
