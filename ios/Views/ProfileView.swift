import SwiftUI

struct ProfileView: View {
    @StateObject private var store: ProfileStore

    init(authStore: AuthStore) {
        _store = StateObject(wrappedValue: ProfileStore(authStore: authStore))
    }

    var body: some View {
        Form {
            Section("生日信息") {
                TextField("公历生日 YYYY-MM-DD", text: $store.birthDateInput)
                    .textInputAutocapitalization(.never)
                    .autocorrectionDisabled()
                TextField("出生时辰 HH:MM（可选）", text: $store.birthTimeInput)
                    .textInputAutocapitalization(.never)
                    .autocorrectionDisabled()

                Button("保存") {
                    Task { await store.saveBirthInfo() }
                }
                .buttonStyle(.borderedProminent)
            }

            if let p = store.profile {
                Section("命理信息") {
                    row("生肖", p.animal)
                    row("星座", p.zodiacSign)
                    row("农历", p.lunarBirth)
                    row("八字", p.bazi)
                }
            }

            if let error = store.errorMessage {
                Section {
                    Text(error)
                        .foregroundColor(.red)
                        .font(.footnote)
                }
            }
        }
        .navigationTitle("个人资料")
        .overlay {
            if store.isLoading {
                ProgressView("加载中...")
            }
        }
        .task {
            await store.load()
        }
    }

    @ViewBuilder
    private func row(_ title: String, _ value: String) -> some View {
        HStack {
            Text(title)
            Spacer()
            Text(value.isEmpty ? "-" : value)
                .foregroundColor(.secondary)
        }
    }
}
