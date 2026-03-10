import SwiftUI

struct IChingDivinationView: View {
    @StateObject private var store: DivinationStore

    init(authStore: AuthStore) {
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
                        }

                        GroupBox("核心解读") {
                            Text(result.summary.isEmpty ? "暂无摘要" : result.summary)
                                .frame(maxWidth: .infinity, alignment: .leading)
                        }

                        GroupBox("详细分析") {
                            Text(result.detail.isEmpty ? "暂无详情" : result.detail)
                                .frame(maxWidth: .infinity, alignment: .leading)
                                .font(.footnote)
                                .foregroundColor(.secondary)
                        }

                        Button("再占一次") {
                            store.reset()
                        }
                        .buttonStyle(.borderedProminent)
                        .padding(.top, 8)
                    }
                    .padding(16)
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
    }
}
