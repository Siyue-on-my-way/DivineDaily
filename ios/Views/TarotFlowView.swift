import SwiftUI
import UIKit

private enum TarotStage {
    case spread
    case question
    case shuffle
    case loading
    case result
}

struct TarotFlowView: View {
    @StateObject private var store: TarotStore
    @State private var stage: TarotStage = .spread
    @State private var showFeedback = false
    @State private var shareLinkItem: ShareLinkItem?
    @State private var showCopyAlert = false

    private let spreadOptions: [(id: String, name: String, desc: String, icon: String)] = [
        ("single", "单张牌", "快速获得清晰答案", "🃏"),
        ("three", "三张牌阵", "过去 / 现在 / 未来", "🎴"),
        ("cross", "十字牌阵", "更深入的问题分析", "✨")
    ]

    let authStore: AuthStore

    init(authStore: AuthStore) {
        self.authStore = authStore
        _store = StateObject(wrappedValue: TarotStore(authStore: authStore))
    }

    var body: some View {
        Group {
            switch stage {
            case .spread:
                spreadSelectView
            case .question:
                questionView
            case .shuffle:
                shuffleView
            case .loading:
                loadingView
            case .result:
                resultView
            }
        }
        .navigationTitle("塔罗占卜")
        .sheet(isPresented: $showFeedback) {
            if let sessionId = store.result?.sessionId {
                FeedbackSheet(authStore: authStore, sessionId: sessionId)
            }
        }
        .alert("链接已复制", isPresented: $showCopyAlert) {
            Button("好") {}
        }
    }

    private var spreadSelectView: some View {
        ScrollView {
            VStack(spacing: 12) {
                ForEach(spreadOptions, id: \.id) { option in
                    Button {
                        store.selectedSpread = option.id
                        stage = .question
                    } label: {
                        HStack(spacing: 12) {
                            Text(option.icon)
                                .font(.title)
                            VStack(alignment: .leading, spacing: 4) {
                                Text(option.name)
                                    .font(.headline)
                                    .foregroundColor(.primary)
                                Text(option.desc)
                                    .font(.footnote)
                                    .foregroundColor(.secondary)
                            }
                            Spacer()
                            Image(systemName: "chevron.right")
                                .foregroundColor(.secondary)
                        }
                        .padding(14)
                        .background(Color(.secondarySystemBackground))
                        .clipShape(RoundedRectangle(cornerRadius: 12))
                    }
                }
            }
            .padding(16)
        }
    }

    private var questionView: some View {
        VStack(spacing: 14) {
            Text("请写下你的问题")
                .font(.headline)

            TextEditor(text: $store.question)
                .frame(height: 160)
                .padding(8)
                .overlay(
                    RoundedRectangle(cornerRadius: 10)
                        .stroke(Color.gray.opacity(0.3), lineWidth: 1)
                )

            if let error = store.errorMessage {
                CommonErrorBanner(message: error)
                    .frame(maxWidth: .infinity, alignment: .leading)
            }

            HStack {
                Button("返回") {
                    stage = .spread
                }
                .buttonStyle(.bordered)

                Button("开始洗牌") {
                    stage = .shuffle
                }
                .buttonStyle(.borderedProminent)
                .disabled(store.question.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
            }

            Spacer()
        }
        .padding(16)
    }

    private var shuffleView: some View {
        VStack(spacing: 20) {
            Text("洗牌与切牌")
                .font(.headline)

            Text("滑动下方滑块，选择你直觉中的切牌位置")
                .font(.footnote)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)

            VStack(spacing: 8) {
                Text("切牌位置：\(store.cutPosition)%")
                    .font(.subheadline)
                Slider(
                    value: Binding(
                        get: { Double(store.cutPosition) },
                        set: { store.updateCutPosition(Int($0)) }
                    ),
                    in: 0...100,
                    step: 1
                )
            }
            .padding(14)
            .background(Color(.secondarySystemBackground))
            .clipShape(RoundedRectangle(cornerRadius: 12))

            HStack {
                Button("返回") {
                    stage = .question
                }
                .buttonStyle(.bordered)

                Button("抽牌并解读") {
                    stage = .loading
                    Task {
                        await store.submitTarot()
                        stage = store.result == nil ? .question : .result
                    }
                }
                .buttonStyle(.borderedProminent)
            }

            Spacer()
        }
        .padding(16)
    }

    private var loadingView: some View {
        VStack(spacing: 14) {
            ProgressView()
            Text("AI 正在解读牌面...")
                .foregroundColor(.secondary)
            Text("通常需要 5-20 秒")
                .font(.footnote)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }

    private var resultView: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                Text(store.result?.title ?? "塔罗结果")
                    .font(.title2)
                    .bold()

                if let processingType = store.result?.processingType, !processingType.isEmpty {
                    GroupBox("处理流程") {
                        Text(processingType)
                            .font(.footnote)
                            .foregroundColor(.secondary)
                    }
                }

                if let quality = store.result?.quality, (!quality.level.isEmpty || !quality.reason.isEmpty || !quality.suggestions.isEmpty) {
                    GroupBox("问题质量提示") {
                        VStack(alignment: .leading, spacing: 6) {
                            if !quality.level.isEmpty {
                                Text("等级：\(quality.level)")
                            }
                            if !quality.reason.isEmpty {
                                Text("原因：\(quality.reason)")
                                    .font(.footnote)
                                    .foregroundColor(.secondary)
                            }
                            if !quality.suggestions.isEmpty {
                                Text("建议：\(quality.suggestions.joined(separator: "、"))")
                                    .font(.footnote)
                                    .foregroundColor(.secondary)
                            }
                        }
                        .frame(maxWidth: .infinity, alignment: .leading)
                    }
                }

                if let cards = store.result?.cards, !cards.isEmpty {
                    GroupBox("抽到的牌") {
                        VStack(alignment: .leading, spacing: 8) {
                            ForEach(Array(cards.enumerated()), id: \.offset) { index, card in
                                VStack(alignment: .leading, spacing: 4) {
                                    HStack {
                                        Text(card.name)
                                            .font(.headline)
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
                                        .font(.caption)
                                        .foregroundColor(.secondary)
                                    if !card.englishName.isEmpty {
                                        Text(card.englishName)
                                            .font(.caption2)
                                            .foregroundColor(.secondary)
                                    }
                                    Text(card.meaning)
                                        .font(.footnote)
                                        .foregroundColor(.secondary)
                                }
                                if index < cards.count - 1 {
                                    Divider()
                                }
                            }
                        }
                        .frame(maxWidth: .infinity, alignment: .leading)
                    }
                }

                GroupBox("解读摘要") {
                    MarkdownText(
                        store.result?.summary ?? "",
                        fallback: "暂未生成摘要，请稍后再查看或重新占卜。"
                    )
                    .frame(maxWidth: .infinity, alignment: .leading)
                }

                GroupBox("详细解读") {
                    MarkdownText(
                        store.result?.detail ?? "",
                        fallback: "暂未生成详细解读，可稍后再尝试查看。"
                    )
                    .font(.footnote)
                    .foregroundColor(.secondary)
                    .frame(maxWidth: .infinity, alignment: .leading)
                }

                DivinationActionBar(
                    onSave: {
                        Task { await store.saveResult() }
                    },
                    onShare: {
                        Task {
                            await store.createShare()
                            if let url = store.shareURL, let item = ShareLinkItem(urlString: url) {
                                shareLinkItem = item
                            }
                        }
                    },
                    isSaving: store.isSaving,
                    isSharing: store.isSharing
                )

                if let shareLinkItem {
                    VStack(spacing: 8) {
                        ShareLink(item: shareLinkItem.url) {
                            Label("系统分享", systemImage: "square.and.arrow.up")
                                .frame(maxWidth: .infinity)
                        }
                        .buttonStyle(.bordered)

                        Button {
                            UIPasteboard.general.string = shareLinkItem.url.absoluteString
                            showCopyAlert = true
                        } label: {
                            Label("复制分享链接", systemImage: "doc.on.doc")
                                .frame(maxWidth: .infinity)
                        }
                        .buttonStyle(.bordered)
                    }
                }

                Button("评价这次占卜") {
                    showFeedback = true
                }
                .buttonStyle(.bordered)

                Button("再占一次") {
                    store.reset()
                    stage = .spread
                }
                .buttonStyle(.borderedProminent)
            }
            .padding(16)
        }
    }
}
