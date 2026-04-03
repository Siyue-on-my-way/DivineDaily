import SwiftUI

struct LoginView: View {
    let authStore: AuthStore

    @State private var username = ""
    @State private var password = ""
    @State private var isSubmitting = false
    @State private var errorMessage: String?

    var body: some View {
        NavigationStack {
            Form {
                Section("账号") {
                    TextField("用户名", text: $username)
                        .autocapitalization(.none)
                        .textInputAutocapitalization(.never)
                }

                Section("密码") {
                    SecureField("密码", text: $password)
                }

                if let error = errorMessage {
                    Section {
                        CommonErrorBanner(message: error)
                    }
                }

                Section {
                    Button {
                        Task {
                            await submit()
                        }
                    } label: {
                        if isSubmitting {
                            ProgressView()
                        } else {
                            Text("登录")
                                .frame(maxWidth: .infinity)
                        }
                    }
                    .disabled(isSubmitting || username.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty || password.isEmpty)
                }

                Section {
                    NavigationLink("没有账号？去注册") {
                        RegisterView(authStore: authStore)
                    }
                }
            }
            .navigationTitle("登录")
        }
    }

    private func submit() async {
        errorMessage = nil
        isSubmitting = true
        defer { isSubmitting = false }

        do {
            try await authStore.login(
                username: username.trimmingCharacters(in: .whitespacesAndNewlines),
                password: password
            )
        } catch {
            errorMessage = (error as? LocalizedError)?.errorDescription ?? "登录失败"
        }
    }
}

