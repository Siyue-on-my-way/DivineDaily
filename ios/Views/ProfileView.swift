import SwiftUI

struct ProfileView: View {
    @StateObject private var store: ProfileStore

    init(authStore: AuthStore) {
        _store = StateObject(wrappedValue: ProfileStore(authStore: authStore))
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                if store.isLoading {
                    ProgressView("加载档案中...")
                }

                if let error = store.errorMessage {
                    CommonErrorBanner(message: error)
                }

                if let p = store.profile {
                    GroupBox("基础信息") {
                        VStack(alignment: .leading, spacing: 8) {
                            HStack {
                                Text("昵称").foregroundColor(.secondary)
                                Spacer()
                                Text(p.nickname ?? "-")
                            }
                            HStack {
                                Text("性别").foregroundColor(.secondary)
                                Spacer()
                                Text(p.gender ?? "-")
                            }
                            HStack {
                                Text("生日(公历)").foregroundColor(.secondary)
                                Spacer()
                                Text(p.birthDate ?? "-")
                            }
                            HStack {
                                Text("出生时辰").foregroundColor(.secondary)
                                Spacer()
                                Text(p.birthTime ?? "-")
                            }
                            HStack {
                                Text("出生地").foregroundColor(.secondary)
                                Spacer()
                                Text(p.birthPlace ?? "-")
                            }
                        }
                    }

                    GroupBox("命理摘要") {
                        VStack(alignment: .leading, spacing: 8) {
                            HStack {
                                Text("生肖").foregroundColor(.secondary)
                                Spacer()
                                Text(p.animal)
                            }
                            HStack {
                                Text("星座").foregroundColor(.secondary)
                                Spacer()
                                Text(p.zodiacSign)
                            }
                            HStack {
                                Text("八字").foregroundColor(.secondary)
                                Spacer()
                                Text(p.bazi)
                            }
                            if !p.lunarBirth.isEmpty {
                                HStack {
                                    Text("农历生日").foregroundColor(.secondary)
                                    Spacer()
                                    Text(p.lunarBirth)
                                }
                            }
                        }
                    }
                }

                Spacer(minLength: 0)
            }
            .padding(16)
        }
        .navigationTitle("用户档案")
        .task {
            await store.load()
        }
    }
}

