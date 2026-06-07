import SwiftUI

struct InsightsView: View {
    @StateObject private var store: InsightsStore

    init(authStore: AuthStore) {
        _store = StateObject(wrappedValue: InsightsStore(authStore: authStore))
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                if store.isLoading {
                    ProgressView("加载洞察中...")
                }

                if let error = store.errorMessage {
                    CommonErrorBanner(message: error)
                }

                if let overview = store.overview {
                    GroupBox("概览") {
                        VStack(alignment: .leading, spacing: 8) {
                            row("总占卜次数", "\(overview.totalDivinations)")
                            row("本周占卜", "\(overview.thisWeekDivinations)")
                            row("平均问题质量", String(format: "%.1f", overview.avgQualityScore))
                            row("成功率", String(format: "%.1f%%", overview.successRate * 100))
                            row("常见类型", localizedType(overview.mostCommonType))
                        }
                        .frame(maxWidth: .infinity, alignment: .leading)
                    }
                }

                GroupBox("类型分布") {
                    if store.typeDistribution.isEmpty {
                        Text("暂无数据")
                            .foregroundColor(.secondary)
                    } else {
                        VStack(alignment: .leading, spacing: 8) {
                            ForEach(store.typeDistribution) { item in
                                VStack(alignment: .leading, spacing: 4) {
                                    HStack {
                                        Text(localizedType(item.type))
                                            .font(.subheadline)
                                        Spacer()
                                        Text("\(item.count) 次")
                                            .font(.caption)
                                            .foregroundColor(.secondary)
                                    }

                                    ProgressView(value: min(max(item.percentage, 0), 100), total: 100)
                                        .tint(.indigo)

                                    Text(String(format: "%.1f%%", item.percentage))
                                        .font(.caption2)
                                        .foregroundColor(.secondary)
                                }
                            }
                        }
                        .frame(maxWidth: .infinity, alignment: .leading)
                    }
                }

                GroupBox("个性化建议") {
                    if store.recommendations.isEmpty {
                        Text("暂无建议")
                            .foregroundColor(.secondary)
                    } else {
                        VStack(alignment: .leading, spacing: 10) {
                            ForEach(store.recommendations) { rec in
                                VStack(alignment: .leading, spacing: 4) {
                                    Text(rec.title)
                                        .font(.subheadline)
                                        .bold()
                                    if !rec.content.isEmpty {
                                        Text(rec.content)
                                            .font(.footnote)
                                            .foregroundColor(.secondary)
                                    }
                                }
                                .frame(maxWidth: .infinity, alignment: .leading)
                            }
                        }
                    }
                }
            }
            .padding(16)
        }
        .navigationTitle("我的洞察")
        .task {
            await store.loadAll()
        }
        .refreshable {
            await store.loadAll()
        }
    }

    @ViewBuilder
    private func row(_ title: String, _ value: String) -> some View {
        HStack {
            Text(title)
            Spacer()
            Text(value)
                .foregroundColor(.secondary)
        }
    }

    private func localizedType(_ raw: String) -> String {
        switch raw {
        case "career": return "事业"
        case "relationship": return "感情"
        case "decision": return "决策"
        case "fortune": return "运势"
        case "knowledge": return "知识"
        case "health": return "健康"
        case "wealth": return "财运"
        case "general": return "综合"
        default: return raw.isEmpty ? "-" : raw
        }
    }
}
