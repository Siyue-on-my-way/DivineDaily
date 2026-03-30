import SwiftUI

struct FortuneView: View {
    @StateObject private var store: FortuneStore
    @State private var showDetail = false

    init(authStore: AuthStore) {
        _store = StateObject(wrappedValue: FortuneStore(authStore: authStore))
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                if store.isLoading {
                    ProgressView("生成今日运势...")
                }

                if let error = store.errorMessage {
                    CommonErrorBanner(message: error)
                }

                if let f = store.today {
                    FortuneScoreCard(overallScore: f.overallScore)

                    FortuneScoreGrid(
                        wealthScore: f.wealthScore,
                        careerScore: f.careerScore,
                        loveScore: f.loveScore,
                        healthScore: f.healthScore
                    )

                    FortuneLuckyCard(
                        luckyColor: f.luckyColor,
                        luckyNumber: f.luckyNumber,
                        luckyDirection: f.luckyDirection,
                        luckyTime: f.luckyTime
                    )

                    FortuneYiJiCard(yi: f.yi, ji: f.ji)

                    FortuneDetailCard(
                        content: f.content,
                        isExpanded: showDetail,
                        onToggle: { showDetail.toggle() }
                    )
                }

                GroupBox("最近运势历史") {
                    if store.history.isEmpty {
                        Text("暂无历史数据")
                            .foregroundColor(.secondary)
                            .frame(maxWidth: .infinity, alignment: .leading)
                    } else {
                        VStack(alignment: .leading, spacing: 10) {
                            ForEach(Array(store.history.enumerated()), id: \.offset) { index, item in
                                VStack(alignment: .leading, spacing: 6) {
                                    HStack {
                                        Text("第 \(index + 1) 条")
                                            .font(.caption)
                                            .foregroundColor(.secondary)
                                        Spacer()
                                        Text("总分 \(item.overallScore)")
                                            .font(.subheadline)
                                            .foregroundColor(.indigo)
                                    }

                                    Text(item.content)
                                        .font(.footnote)
                                        .foregroundColor(.secondary)
                                        .lineLimit(3)

                                    HStack(spacing: 8) {
                                        Text("财 \(item.wealthScore)")
                                        Text("事 \(item.careerScore)")
                                        Text("感 \(item.loveScore)")
                                        Text("健 \(item.healthScore)")
                                    }
                                    .font(.caption2)
                                    .foregroundColor(.secondary)
                                }
                                if index < store.history.count - 1 {
                                    Divider()
                                }
                            }
                        }
                        .frame(maxWidth: .infinity, alignment: .leading)
                    }
                }
            }
            .padding(16)
        }
        .navigationTitle("每日运势")
        .task {
            await store.loadToday()
            await store.loadHistory(limit: 10, skip: 0)
        }
        .refreshable {
            await store.loadToday()
            await store.loadHistory(limit: 10, skip: 0)
        }
    }

    @ViewBuilder
    private func scoreRow(_ title: String, _ score: Int) -> some View {
        HStack {
            Text(title)
            Spacer()
            Text("\(score)")
                .foregroundColor(.secondary)
        }
    }
}

private struct FortuneScoreCard: View {
    let overallScore: Int

    var body: some View {
        GroupBox {
            VStack(alignment: .leading, spacing: 6) {
                Text("综合运势")
                    .font(.headline)
                HStack {
                    Text("总分")
                        .foregroundColor(.secondary)
                    Spacer()
                    Text("\(overallScore)")
                        .font(.title2)
                        .bold()
                        .foregroundColor(.indigo)
                }
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        }
    }
}

private struct FortuneScoreGrid: View {
    let wealthScore: Int
    let careerScore: Int
    let loveScore: Int
    let healthScore: Int

    var body: some View {
        GroupBox {
            VStack(alignment: .leading, spacing: 10) {
                Text("分项评分")
                    .font(.headline)
                HStack(spacing: 12) {
                    scoreTile(title: "财运", score: wealthScore, color: .orange)
                    scoreTile(title: "事业", score: careerScore, color: .blue)
                }
                HStack(spacing: 12) {
                    scoreTile(title: "感情", score: loveScore, color: .pink)
                    scoreTile(title: "健康", score: healthScore, color: .green)
                }
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        }
    }

    private func scoreTile(title: String, score: Int, color: Color) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
            Text("\(score)")
                .font(.headline)
                .foregroundColor(color)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(10)
        .background(color.opacity(0.12))
        .clipShape(RoundedRectangle(cornerRadius: 12))
    }
}

private struct FortuneLuckyCard: View {
    let luckyColor: String
    let luckyNumber: Int
    let luckyDirection: String
    let luckyTime: String

    var body: some View {
        GroupBox {
            VStack(alignment: .leading, spacing: 10) {
                Text("幸运信息")
                    .font(.headline)
                HStack(spacing: 12) {
                    luckyItem(title: "幸运色", value: luckyColor)
                    luckyItem(title: "幸运数字", value: "\(luckyNumber)")
                }
                HStack(spacing: 12) {
                    luckyItem(title: "幸运方位", value: luckyDirection)
                    luckyItem(title: "幸运时辰", value: luckyTime)
                }
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        }
    }

    private func luckyItem(title: String, value: String) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
            Text(value)
                .font(.subheadline)
                .bold()
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(10)
        .background(Color(.secondarySystemBackground))
        .clipShape(RoundedRectangle(cornerRadius: 12))
    }
}

private struct FortuneYiJiCard: View {
    let yi: String
    let ji: String

    var body: some View {
        GroupBox {
            VStack(alignment: .leading, spacing: 10) {
                Text("宜忌")
                    .font(.headline)
                HStack(spacing: 12) {
                    VStack(alignment: .leading, spacing: 6) {
                        Text("宜")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        Text(yi.isEmpty ? "无" : yi)
                            .font(.subheadline)
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(10)
                    .background(Color.green.opacity(0.12))
                    .clipShape(RoundedRectangle(cornerRadius: 12))

                    VStack(alignment: .leading, spacing: 6) {
                        Text("忌")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        Text(ji.isEmpty ? "无" : ji)
                            .font(.subheadline)
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(10)
                    .background(Color.red.opacity(0.12))
                    .clipShape(RoundedRectangle(cornerRadius: 12))
                }
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        }
    }
}

private struct FortuneDetailCard: View {
    let content: String
    let isExpanded: Bool
    let onToggle: () -> Void

    var body: some View {
        GroupBox {
            VStack(alignment: .leading, spacing: 10) {
                HStack {
                    Text("解读")
                        .font(.headline)
                    Spacer()
                    Button(isExpanded ? "收起" : "展开") {
                        onToggle()
                    }
                    .font(.caption)
                }

                if isExpanded {
                    MarkdownText(content, fallback: "暂无内容")
                        .frame(maxWidth: .infinity, alignment: .leading)
                } else {
                    Text(content.isEmpty ? "暂无内容" : content)
                        .font(.footnote)
                        .foregroundColor(.secondary)
                        .lineLimit(3)
                }
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        }
    }
}
