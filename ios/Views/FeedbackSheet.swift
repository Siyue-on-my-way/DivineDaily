import SwiftUI

struct FeedbackSheet: View {
    @Environment(\.dismiss) private var dismiss

    @State private var rating: Int = 5
    @State private var isHelpful: Bool = true
    @State private var comment: String = ""

    @StateObject private var store: FeedbackStore

    let sessionId: String

    init(authStore: AuthStore, sessionId: String) {
        self.sessionId = sessionId
        _store = StateObject(wrappedValue: FeedbackStore(authStore: authStore))
    }

    var body: some View {
        NavigationView {
            Form {
                Section("评分") {
                    Picker("评分", selection: $rating) {
                        ForEach(1...5, id: \.self) { value in
                            Text("\(value) 星").tag(value)
                        }
                    }
                    .pickerStyle(.segmented)
                }

                Section("是否有帮助") {
                    Toggle("本次占卜是否有帮助", isOn: $isHelpful)
                }

                Section("补充说明") {
                    TextEditor(text: $comment)
                        .frame(height: 120)
                }

                if let error = store.errorMessage {
                    Section {
                        Text(error)
                            .foregroundColor(.red)
                    }
                }
            }
            .navigationTitle("评价占卜")
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("关闭") { dismiss() }
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button(store.isSubmitting ? "提交中" : "提交") {
                        Task {
                            await store.submitDivinationFeedback(
                                sessionId: sessionId,
                                rating: rating,
                                comment: comment.isEmpty ? nil : comment,
                                tags: nil,
                                isHelpful: isHelpful
                            )
                            if store.submitted {
                                dismiss()
                            }
                        }
                    }
                    .disabled(store.isSubmitting)
                }
            }
        }
    }
}
