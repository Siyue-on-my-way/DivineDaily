import SwiftUI

struct FortuneView: View {
    @StateObject private var store: FortuneStore

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
                    GroupBox("综合运势") {
                        HStack {
                            Text("总分")
                            Spacer()
                            Text("\(f.overallScore)")
                                .bold()
                                .foregroundColor(.indigo)
                        }
                    }

                    GroupBox("分项评分") {
                        VStack(spacing: 8) {
                            scoreRow("财运", f.wealthScore)
                            scoreRow("事业", f.careerScore)
                            scoreRow("感情", f.loveScore)
                            scoreRow("健康", f.healthScore)
                        }
                    }

                    GroupBox("幸运信息") {
                        VStack(alignment: .leading, spacing: 6) {
                            Text("幸运色：\(f.luckyColor)")
                            Text("幸运数字：\(f.luckyNumber)")
                            Text("幸运方位：\(f.luckyDirection)")
                            Text("幸运时辰：\(f.luckyTime)")
                        }
                        .frame(maxWidth: .infinity, alignment: .leading)
                    }

                    GroupBox("宜忌") {
                        VStack(alignment: .leading, spacing: 6) {
                            Text("宜：\(f.yi)")
                            Text("忌：\(f.ji)")
                        }
                        .frame(maxWidth: .infinity, alignment: .leading)
                    }

                    GroupBox("解读") {
                        Text(f.content)
                            .frame(maxWidth: .infinity, alignment: .leading)
                    }
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
