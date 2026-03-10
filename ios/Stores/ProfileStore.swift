import Foundation

@MainActor
final class ProfileStore: ObservableObject {
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var profile: UserProfile?

    @Published var birthDateInput: String = ""
    @Published var birthTimeInput: String = ""

    private let service: ProfileService

    init(authStore: AuthStore) {
        self.service = AppEnvironment.shared.makeProfileService { [weak authStore] in
            Task { @MainActor in authStore?.logout() }
        }
    }

    func load() async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }

        do {
            let p = try await service.getMyProfile()
            profile = p
            birthDateInput = p.birthDate
            birthTimeInput = p.birthTime
        } catch {
            errorMessage = (error as? LocalizedError)?.errorDescription ?? "加载资料失败"
        }
    }

    func saveBirthInfo() async {
        guard !birthDateInput.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
            errorMessage = "请输入生日（YYYY-MM-DD）"
            return
        }

        isLoading = true
        errorMessage = nil
        defer { isLoading = false }

        do {
            let updated = try await service.updateMyProfile(
                birthDate: birthDateInput,
                birthTime: birthTimeInput.isEmpty ? nil : birthTimeInput
            )
            profile = updated
        } catch {
            errorMessage = (error as? LocalizedError)?.errorDescription ?? "保存失败"
        }
    }
}
