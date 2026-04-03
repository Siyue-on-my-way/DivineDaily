import SwiftUI
import UIKit

struct HistoryView: View {
    @EnvironmentObject private var authStore: AuthStore
    @StateObject private var store: HistoryStore

    @AppStorage("history.filter.eventType") private var eventType = ""
    @AppStorage("history.filter.version") private var version = ""
    @AppStorage("history.filter.status") private var status = ""
    @AppStorage("history.filter.startDate") private var startDate = ""
    @AppStorage("history.filter.endDate") private var endDate = ""
    @AppStorage("history.filter.orderBy") private var orderBy = "created_at"
    @AppStorage("history.filter.orderDirection") private var orderDirection = "desc"
    @State private var filterValidationMessage: String?
    @State private var showQuickFilterHint = false

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
                    Text("处理中").tag("processing")
                    Text("已完成").tag("completed")
                    Text("失败").tag("failed")
                }

                TextField("开始日期（YYYY-MM-DD）", text: $startDate)
                    .textInputAutocapitalization(.never)
                    .autocorrectionDisabled()
                TextField("结束日期（YYYY-MM-DD）", text: $endDate)
                    .textInputAutocapitalization(.never)
                    .autocorrectionDisabled()

                Picker("排序字段", selection: $orderBy) {
                    Text("创建时间").tag("created_at")
                    Text("更新时间").tag("updated_at")
                }

                Picker("排序方向", selection: $orderDirection) {
                    Text("降序").tag("desc")
                    Text("升序").tag("asc")
                }

                HStack(spacing: 12) {
                    Button("应用筛选") {
                        switch validateDateFilters(startDate: startDate, endDate: endDate) {
                        case .success:
                            filterValidationMessage = nil
                            Task {
                                await store.applyFilters(
                                    eventType: eventType,
                                    version: version,
                                    status: status,
                                    startDate: startDate,
                                    endDate: endDate,
                                    orderBy: orderBy,
                                    orderDirection: orderDirection
                                )
                            }
                        case .failure(let msg):
                            filterValidationMessage = msg
                        }
                    }
                    .buttonStyle(.borderedProminent)

                    Button("仅看失败") {
                        status = "failed"
                        filterValidationMessage = nil
                        showQuickFilterHint = true
                        Task {
                            await store.applyFilters(
                                eventType: eventType,
                                version: version,
                                status: status,
                                startDate: startDate,
                                endDate: endDate,
                                orderBy: orderBy,
                                orderDirection: orderDirection
                            )
                        }
                    }
                    .buttonStyle(.bordered)

                    Button("重置") {
                        resetFiltersToDefault()
                        filterValidationMessage = nil
                        Task {
                            await store.applyFilters(
                                eventType: eventType,
                                version: version,
                                status: status,
                                startDate: startDate,
                                endDate: endDate,
                                orderBy: orderBy,
                                orderDirection: orderDirection
                            )
                        }
                    }
                    .buttonStyle(.bordered)
                }
            }

            if let validationError = filterValidationMessage {
                Section {
                    CommonErrorBanner(message: validationError)
                }
            }

            if let error = store.errorMessage {
                Section {
                    CommonErrorBanner(message: error)
                }
            }

            Section("占卜记录（共 \(store.items.count)/\(store.total) 条）") {
                if store.items.isEmpty, !store.isLoading {
                    VStack(alignment: .leading, spacing: 6) {
                        Text("暂无符合条件的占卜记录")
                            .foregroundColor(.secondary)
                        Text("建议：清空筛选条件后重试，或先发起一次新的占卜。")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                    .padding(.vertical, 6)
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
                                Text(DateTextFormatter.format(item.createdAt))
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
            let initialValidation = validateDateFilters(startDate: startDate, endDate: endDate)
            switch initialValidation {
            case .success:
                filterValidationMessage = nil
                await store.applyFilters(
                    eventType: eventType,
                    version: version,
                    status: status,
                    startDate: startDate,
                    endDate: endDate,
                    orderBy: orderBy,
                    orderDirection: orderDirection
                )
            case .failure(let msg):
                filterValidationMessage = msg
                await store.applyFilters(
                    eventType: eventType,
                    version: version,
                    status: status,
                    startDate: "",
                    endDate: "",
                    orderBy: orderBy,
                    orderDirection: orderDirection
                )
            }
        }
        .refreshable {
            switch validateDateFilters(startDate: startDate, endDate: endDate) {
            case .success:
                filterValidationMessage = nil
                await store.applyFilters(
                    eventType: eventType,
                    version: version,
                    status: status,
                    startDate: startDate,
                    endDate: endDate,
                    orderBy: orderBy,
                    orderDirection: orderDirection
                )
            case .failure(let msg):
                filterValidationMessage = msg
            }
        }
        .alert("快捷筛选已生效", isPresented: $showQuickFilterHint) {
            Button("知道了", role: .cancel) {}
        } message: {
            Text("当前已切换为仅展示失败记录。")
        }
    }

    private func resetFiltersToDefault() {
        eventType = ""
        version = ""
        status = ""
        startDate = ""
        endDate = ""
        orderBy = "created_at"
        orderDirection = "desc"
    }

    private func validateDateFilters(startDate: String, endDate: String) -> Result<Void, String> {
        let trimmedStart = startDate.trimmingCharacters(in: .whitespacesAndNewlines)
        let trimmedEnd = endDate.trimmingCharacters(in: .whitespacesAndNewlines)

        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.dateFormat = "yyyy-MM-dd"
        formatter.timeZone = TimeZone(secondsFromGMT: 0)

        var parsedStart: Date?
        if !trimmedStart.isEmpty {
            guard let date = formatter.date(from: trimmedStart), formatter.string(from: date) == trimmedStart else {
                return .failure("开始日期格式无效，请使用 YYYY-MM-DD")
            }
            parsedStart = date
        }

        var parsedEnd: Date?
        if !trimmedEnd.isEmpty {
            guard let date = formatter.date(from: trimmedEnd), formatter.string(from: date) == trimmedEnd else {
                return .failure("结束日期格式无效，请使用 YYYY-MM-DD")
            }
            parsedEnd = date
        }

        if let start = parsedStart, let end = parsedEnd, start > end {
            return .failure("开始日期不能晚于结束日期")
        }

        return .success(())
    }
}

struct HistoryDetailView: View {
    @StateObject private var store: HistoryDetailStore
    @State private var showFeedback = false
    @State private var shareLinkItem: ShareLinkItem?
    @State private var copiedShareURL: String?
    @State private var showCopiedAlert = false
    @State private var expandAllShares = false

    let authStore: AuthStore
    let item: DivinationHistoryItem

    init(authStore: AuthStore, item: DivinationHistoryItem) {
        self.authStore = authStore
        self.item = item
        _store = StateObject(wrappedValue: HistoryDetailStore(authStore: authStore))
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
                            MarkdownText(result.summary, fallback: "暂无摘要")
                                .frame(maxWidth: .infinity, alignment: .leading)
                        }
                    }

                    if !result.detail.isEmpty {
                        GroupBox("详细解读") {
                            MarkdownText(result.detail, fallback: "暂无详情")
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
                                Text("综合：\(daily.overallScore)（\(scoreLevelText(daily.overallScore))）")
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

                DivinationActionBar(
                    onSave: {
                        Task { await store.saveResult(sessionId: item.id) }
                    },
                    onShare: {
                        Task {
                            await store.createShare(sessionId: item.id)
                            if let url = store.shareURL, let item = ShareLinkItem(urlString: url) {
                                shareLinkItem = item
                            }
                        }
                    },
                    isSaving: store.isSaving,
                    isSharing: store.isSharing
                )

                if let shareLinkItem {
                    ShareLink(item: shareLinkItem.url) {
                        Label("系统分享", systemImage: "square.and.arrow.up")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.bordered)
                }

                if let stats = store.shareStats {
                    GroupBox("分享统计") {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("分享次数：\(stats.totalShares)")
                            Text("总浏览量：\(stats.totalViews)")

                            if stats.shares.isEmpty {
                                Text("暂无分享记录")
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            } else {
                                Divider()
                                HStack {
                                    Text("分享列表")
                                        .font(.caption)
                                        .foregroundColor(.secondary)
                                    Spacer()
                                    Button(expandAllShares ? "收起" : "展开全部") {
                                        expandAllShares.toggle()
                                    }
                                    .font(.caption2)
                                    .buttonStyle(.bordered)
                                }

                                let displayShares = expandAllShares ? stats.shares : Array(stats.shares.prefix(3))

                                ForEach(displayShares) { share in
                                    VStack(alignment: .leading, spacing: 4) {
                                        if !share.url.isEmpty {
                                            Text(share.url)
                                                .font(.caption2)
                                                .foregroundColor(.secondary)
                                                .lineLimit(1)
                                        }
                                        HStack(spacing: 8) {
                                            Text("浏览：\(share.viewCount)")
                                                .font(.caption2)
                                                .foregroundColor(.secondary)
                                            Text(share.isExpired ? "已过期" : "有效")
                                                .font(.caption2)
                                                .padding(.horizontal, 6)
                                                .padding(.vertical, 2)
                                                .background((share.isExpired ? Color.gray : Color.green).opacity(0.15))
                                                .clipShape(Capsule())
                                            Spacer()
                                            if !share.url.isEmpty {
                                                Button("复制链接") {
                                                    UIPasteboard.general.string = share.url
                                                    copiedShareURL = share.url
                                                    showCopiedAlert = true
                                                }
                                                .font(.caption2)
                                                .buttonStyle(.bordered)
                                            }
                                        }
                                    }
                                    .padding(.vertical, 2)
                                }

                                if !expandAllShares, stats.shares.count > 3 {
                                    Text("仅展示前 3 条，点击“展开全部”查看全部记录")
                                        .font(.caption2)
                                        .foregroundColor(.secondary)
                                }
                            }
                        }
                        .font(.footnote)
                        .frame(maxWidth: .infinity, alignment: .leading)
                    }
                }

                Button("评价这次占卜") {
                    showFeedback = true
                }
                .buttonStyle(.bordered)

                if let error = store.errorMessage {
                    CommonErrorBanner(message: error)
                }

                Text("时间：\(DateTextFormatter.format(item.createdAt))")
                    .font(.footnote)
                    .foregroundColor(.secondary)
            }
            .padding(16)
        }
        .navigationTitle("记录详情")
        .sheet(isPresented: $showFeedback) {
            FeedbackSheet(authStore: authStore, sessionId: item.id)
        }
        .task {
            await store.load(sessionId: item.id)
            await store.loadShareStats(sessionId: item.id)
        }
        .alert("复制成功", isPresented: $showCopiedAlert) {
            Button("好的", role: .cancel) {}
        } message: {
            Text(copiedShareURL ?? "链接已复制到剪贴板")
        }
    }

    private func scoreLevelText(_ score: Int) -> String {
        switch score {
        case 85...100:
            return "大吉"
        case 70...84:
            return "吉"
        case 50...69:
            return "平"
        default:
            return "需谨慎"
        }
    }
}
