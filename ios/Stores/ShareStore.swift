import Foundation

@MainActor
final class ShareStore: ObservableObject {
    @Published var isLoading = false
    @Published var errorMessage: String?

    @Published var question: String = ""
    @Published var result: DivinationResult?
    @Published var metadataCreatedAt: String?
    @Published var metadataViewCount: Int?

    private let service: ShareService

    init() {
        self.service = AppEnvironment.shared.makeShareService(onUnauthorized: nil)
    }

    func load(shareToken raw: String) async {
        let token = raw.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !token.isEmpty else {
            errorMessage = "无效的分享链接"
            return
        }

        isLoading = true
        errorMessage = nil
        result = nil
        question = ""
        metadataCreatedAt = nil
        metadataViewCount = nil
        defer { isLoading = false }

        do {
            let dto = try await service.fetchShareContent(shareToken: token)
            question = dto.question
            result = DivinationResult(shareToken: dto.share_token, payload: dto.result)
            metadataCreatedAt = dto.metadata?.created_at
            metadataViewCount = dto.metadata?.view_count
        } catch let api as APIError {
            switch api {
            case .forbidden:
                errorMessage = "分享已设为私密"
            case .serverError(let code, let detail):
                if code == 410 {
                    errorMessage = detail ?? "分享已过期"
                } else if code == 404 {
                    errorMessage = detail ?? "分享不存在"
                } else {
                    errorMessage = detail ?? "加载分享失败"
                }
            default:
                errorMessage = api.localizedDescription
            }
        } catch {
            errorMessage = (error as? LocalizedError)?.errorDescription ?? "加载分享失败"
        }
    }
}
