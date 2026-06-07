import Foundation

@MainActor
final class InsightsStore: ObservableObject {
    @Published var isLoading = false
    @Published var errorMessage: String?

    @Published var overview: InsightsOverview?
    @Published var typeDistribution: [InsightsTypeDistributionItem] = []
    @Published var recommendations: [InsightsRecommendationItem] = []

    private let service: InsightsService

    init(authStore: AuthStore) {
        self.service = AppEnvironment.shared.makeInsightsService { [weak authStore] in
            Task { @MainActor in authStore?.logout() }
        }
    }

    func loadAll() async {
        isLoading = true
        errorMessage = nil

        do {
            async let o = service.getOverview()
            async let t = service.getTypeDistribution()
            async let r = service.getRecommendations()

            overview = try await o
            typeDistribution = try await t
            recommendations = try await r
        } catch {
            errorMessage = (error as? LocalizedError)?.errorDescription ?? "加载洞察失败"
        }

        isLoading = false
    }
}
