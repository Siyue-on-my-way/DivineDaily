import SwiftUI

struct RegisterView: View {
    let authStore: AuthStore

    @State private var username = ""
    @State private var email = ""
    @State private var password = ""
    @State private var confirmPassword = ""

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

                Section("邮箱（可选）") {
                    TextField("邮箱", text: $email)
                        .keyboardType(.emailAddress)
                        .autocapitalization(.none)
                }

                Section("密码") {
                    SecureField("密码", text: $password)
                    SecureField("确认密码", text: $confirmPassword)
                }

                if let error = errorMessage {
                    Section {
                        CommonErrorBanner(message: error)
                    }
                }

                Section {
                    Button {
                        Task { await submit() }
                    } label: {
                        if isSubmitting {
                            ProgressView()
                        } else {
                            Text("注册")
                                .frame(maxWidth: .infinity)
                        }
                    }
                    .disabled(
                        isSubmitting ||
                        username.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty ||
                        password.isEmpty ||
                        confirmPassword.isEmpty
                    )
                }
            }
            .navigationTitle("注册")
        }
    }

    private func submit() async {
        errorMessage = nil
        isSubmitting = true
        defer { isSubmitting = false }

        guard password == confirmPassword else {
            errorMessage = "两次密码不一致"
            return
        }

        do {
            try await authStore.register(
                username: username.trimmingCharacters(in: .whitespacesAndNewlines),
                email: email.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty ? nil : email,
                password: password,
                confirmPassword: confirmPassword
            )
        } catch {
            errorMessage = (error as? LocalizedError)?.errorDescription ?? "注册失败"
        }
    }
}

