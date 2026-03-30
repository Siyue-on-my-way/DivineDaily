import SwiftUI
import UIKit

struct IChingDivinationView: View {
    @StateObject private var store: DivinationStore
    @State private var showFeedback = false
    @State private var shareLinkItem: ShareLinkItem?
    @State private var showCopyAlert = false

    let authStore: AuthStore

    init(authStore: AuthStore) {
        self.authStore = authStore
        _store = StateObject(wrappedValue: DivinationStore(authStore: authStore))
    }

    var body: some View {
        Group {
            if store.isLoading {
                VStack(spacing: 16) {
                    ProgressView()
                    Text("正在为你起卦解读...")
                        .foregroundColor(.secondary)
                    Text("通常需要 5-20 秒")
                        .font(.footnote)
                        .foregroundColor(.secondary)
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else if let result = store.result {
                ScrollView {
                    VStack(alignment: .leading, spacing: 14) {
                        Text(result.title ?? "占卜结果")
                            .font(.title2)
                            .bold()

                        if let outcome = result.outcome, !outcome.isEmpty {
                            Label(outcome, systemImage: "sparkles")
                                .font(.headline)
                                .foregroundColor(.indigo)
                        }

                        if let processingType = result.processingType, !processingType.isEmpty {
                            GroupBox("处理流程") {
                                Text(processingType)
                                    .font(.footnote)
                                    .foregroundColor(.secondary)
                            }
                        }

                        if let quality = result.quality, (!quality.level.isEmpty || !quality.reason.isEmpty || !quality.suggestions.isEmpty) {
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

                        if let hex = result.hexagramInfo {
                            GroupBox("卦象信息") {
                                VStack(alignment: .leading, spacing: 8) {
                                    Text("卦名：\(hex.name ?? "-")")
                                    Text("上卦：\(hex.upperTrigram ?? "-")")
                                    Text("下卦：\(hex.lowerTrigram ?? "-")")
                                    if let wuxing = hex.wuxing, !wuxing.isEmpty {
                                        Text("五行：\(wuxing)")
                                    }
                                }
                                .frame(maxWidth: .infinity, alignment: .leading)
                                .font(.subheadline)
                            }

                            if !hex.lineValues.isEmpty {
                                GroupBox("六爻图") {
                                    HexagramLinesView(lineValues: hex.lineValues)
                                }
                            }
                        }

                        if let trace = result.yarrowTrace, !trace.lines.isEmpty {
                            YarrowTraceView(trace: trace)
                        }

                        GroupBox("核心解读") {
                            MarkdownText(
                                result.summary,
                                fallback: "暂未生成摘要，请稍后再查看或重新占卜。"
                            )
                            .frame(maxWidth: .infinity, alignment: .leading)
                        }

                        GroupBox("详细分析") {
                            MarkdownText(
                                result.detail,
                                fallback: "暂未生成详细分析，可稍后再尝试查看。"
                            )
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .font(.footnote)
                            .foregroundColor(.secondary)
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
                        }
                        .buttonStyle(.borderedProminent)
                        .padding(.top, 8)
                    }
                    .padding(16)
                }
                .sheet(isPresented: $showFeedback) {
                    if let sessionId = store.result?.sessionId {
                        FeedbackSheet(authStore: authStore, sessionId: sessionId)
                    }
                }
            } else {
                VStack(spacing: 14) {
                    Text("周易占卜")
                        .font(.title2)
                        .bold()

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

                    Button {
                        Task { await store.submitIChingQuestion() }
                    } label: {
                        Text("开始占卜")
                            .bold()
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.borderedProminent)
                    .disabled(store.question.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
                }
                .padding(16)
            }
        }
        .navigationTitle("周易占卜")
        .alert("链接已复制", isPresented: $showCopyAlert) {
            Button("好") {}
        }
    }
}
