import SwiftUI

struct LoginView: View {
    @EnvironmentObject private var authStore: AuthStore

    @State private var username = ""
    @State private var password = ""
    @State private var goRegister = false

    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                Text("DivineDaily")
                    .font(.largeTitle)
                    .bold()

                VStack(spacing: 12) {
                    TextField("用户名", text: $username)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()
                        .padding()
                        .background(Color(.secondarySystemBackground))
                        .cornerRadius(10)

                    SecureField("密码", text: $password)
                        .padding()
                        .background(Color(.secondarySystemBackground))
                        .cornerRadius(10)
                }

                if let error = authStore.errorMessage {
                    CommonErrorBanner(message: error)
                }

                Button {
                    Task {
                        await authStore.login(username: username, password: password)
                    }
                } label: {
                    if authStore.isLoading {
                        ProgressView()
                            .frame(maxWidth: .infinity)
                    } else {
                        Text("登录")
                            .bold()
                            .frame(maxWidth: .infinity)
                    }
                }
                .buttonStyle(.borderedProminent)
                .disabled(username.isEmpty || password.isEmpty || authStore.isLoading)

                Button("没有账号？去注册") {
                    goRegister = true
                }
                .font(.footnote)
                .padding(.top, 4)

                NavigationLink(destination: RegisterView(), isActive: $goRegister) {
                    EmptyView()
                }
            }
            .padding(24)
        }
        .navigationViewStyle(.stack)
    }
}
