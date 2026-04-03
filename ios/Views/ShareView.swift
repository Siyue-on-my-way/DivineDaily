import SwiftUI

/// 通过分享 token 或完整 URL 展示 `GET /shares/{token}` 返回的内容（无需登录）
struct ShareView: View {
    let shareTokenOrURL: String
    var showDismissButton: Bool = false

    @StateObject private var store = ShareStore()
    @Environment(\.dismiss) private var dismiss

    private var resolvedToken: String {
        ShareURLParser.token(from: shareTokenOrURL)
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                if store.isLoading {
                    ProgressView("加载分享内容...")
                        .frame(maxWidth: .infinity)
                }

                if let error = store.errorMessage {
                    CommonErrorBanner(message: error)
                }

                if !store.question.isEmpty {
                    Text(store.question)
                        .font(.title3)
                        .bold()
                }

                if let meta = store.metadataCreatedAt, !meta.isEmpty {
                    Text("分享时间：\(DateTextFormatter.format(meta))")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }

                if let vc = store.metadataViewCount {
                    Text("浏览次数：\(vc)")
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }

                if let result = store.result {
                    shareResultContent(result)
                }
            }
            .padding(16)
        }
        .navigationTitle("分享")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            if showDismissButton {
                ToolbarItem(placement: .cancellationAction) {
                    Button("关闭") { dismiss() }
                }
            }
        }
        .task {
            await store.load(shareToken: resolvedToken)
        }
    }

    @ViewBuilder
    private func shareResultContent(_ result: DivinationResult) -> some View {
        if let outcome = result.outcome, !outcome.isEmpty {
            Text("结果：\(outcome)")
                .foregroundColor(.indigo)
        }

        if let title = result.title, !title.isEmpty {
            Text(title)
                .font(.headline)
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

            if !hexagram.lineValues.isEmpty {
                GroupBox("六爻图") {
                    HexagramLinesView(lineValues: hexagram.lineValues)
                }
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
    }
}

/// 首页入口：粘贴链接或 token 后进入落地页
struct ShareEntryView: View {
    @State private var input = ""

    private var canOpen: Bool {
        !ShareURLParser.token(from: input).isEmpty
    }

    var body: some View {
        Form {
            Section {
                TextField("粘贴分享链接或 token", text: $input, axis: .vertical)
                    .lineLimit(3...8)
            } footer: {
                Text("支持前端页路径 `/share/{token}`、API 路径中的 `shares/{token}`，或自定义 scheme：`divinedaily://share/{token}`。")
                    .font(.footnote)
            }

            Section {
                NavigationLink {
                    ShareView(shareTokenOrURL: input)
                } label: {
                    Text("打开")
                }
                .disabled(!canOpen)
            }
        }
        .navigationTitle("打开分享")
    }
}
