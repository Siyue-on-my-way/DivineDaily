import SwiftUI

struct SessionSelectorSection: View {
    let items: [DivinationHistoryItem]
    @Binding var selectedSessionId: String
    @Binding var keyword: String

    private var filteredItems: [DivinationHistoryItem] {
        let completed = items.filter { $0.isCompleted }
        let sorted = completed.sorted { $0.createdAtRaw > $1.createdAtRaw }
        guard !keyword.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
            return sorted
        }
        let key = keyword.lowercased()
        return sorted.filter {
            $0.question.lowercased().contains(key) || $0.id.lowercased().contains(key)
        }
    }

    var body: some View {
        Section("选择占卜记录") {
            TextField("搜索问题或会话ID", text: $keyword)
                .textInputAutocapitalization(.never)
                .autocorrectionDisabled()

            if filteredItems.isEmpty {
                Text("暂无可分享记录（仅展示已完成占卜）")
                    .foregroundColor(.secondary)
            } else {
                Picker("会话", selection: $selectedSessionId) {
                    Text("请选择").tag("")
                    ForEach(filteredItems) { item in
                        Text((item.question.isEmpty ? "未命名问题" : item.question).prefix(24))
                            .tag(item.id)
                    }
                }
            }
        }
    }
}
