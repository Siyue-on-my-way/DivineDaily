import SwiftUI

struct RegisterView: View {
    @EnvironmentObject private var authStore: AuthStore
    @Environment(\.dismiss) private var dismiss

    @State private var username = ""
    @State private var email = ""
    @State private var password = ""

    var body: some View {
        VStack(spacing: 16) {
            Text("创建账号")
                .font(.title2)
                .bold()

            TextField("用户名", text: $username)
                .textInputAutocapitalization(.never)
                .autocorrectionDisabled()
                .padding()
                .background(Color(.secondarySystemBackground))
                .cornerRadius(10)

            TextField("邮箱", text: $email)
                .textInputAutocapitalization(.never)
                .autocorrectionDisabled()
                .keyboardType(.emailAddress)
                .padding()
                .background(Color(.secondarySystemBackground))
                .cornerRadius(10)

            SecureField("密码", text: $password)
                .padding()
                .background(Color(.secondarySystemBackground))
                .cornerRadius(10)

            if let error = authStore.errorMessage {
                Text(error)
                    .foregroundColor(.red)
                    .font(.footnote)
            }

            Button {
                Task {
                    await authStore.register(username: username, email: email, password: password)
                    if authStore.isAuthenticated {
                        dismiss()
                    }
                }
            } label: {
                if authStore.isLoading {
                    ProgressView()
                        .frame(maxWidth: .infinity)
                } else {
                    Text("注册并登录")
                        .bold()
                        .frame(maxWidth: .infinity)
                }
            }
            .buttonStyle(.borderedProminent)
            .disabled(username.isEmpty || email.isEmpty || password.count < 6 || authStore.isLoading)

            Spacer()
        }
        .padding(20)
    }
}
