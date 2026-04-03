import Foundation

@MainActor
final class HistoryStore: ObservableObject {
    @Published var items: [DivinationHistoryItem] = []
    @Published var total: Int = 0

    @Published var isLoading = false
    @Published var isLoadingMore = false
    @Published var errorMessage: String?

    private let authStore: AuthStore
    private let service: DivinationService

    private var hasMore = true
    private var limit = 20

    private var eventTypeFilter: String?
    private var versionFilter: String?
    private var statusFilter: String?
    private var startDateFilter: String?
    private var endDateFilter: String?
    private var orderByFilter: String? = "created_at"
    private var orderDirectionFilter: String? = "desc"

    init(authStore: AuthStore) {
        self.authStore = authStore
        self.service = AppEnvironment.shared.makeDivinationService { [weak authStore] in
            Task { @MainActor in authStore?.logout() }
        }
    }

    func load() async {
        guard authStore.isAuthenticated else {
            errorMessage = "请先登录"
            return
        }

        isLoading = true
        isLoadingMore = false
        errorMessage = nil

        items = []
        total = 0
        hasMore = true

        do {
            let dto = try await service.listHistory(
                limit: limit,
                offset: 0,
                eventType: eventTypeFilter,
                version: versionFilter,
                status: statusFilter,
                startDate: startDateFilter,
                endDate: endDateFilter,
                orderBy: orderByFilter,
                orderDirection: orderDirectionFilter
            )
            items = dto.sessions.map(DivinationHistoryItem.init)
            total = dto.total
            hasMore = dto.has_more
        } catch {
            errorMessage = mapError(error, fallback: "加载历史失败")
        }

        isLoading = false
    }

    func applyFilters(
        eventType: String,
        version: String,
        status: String,
        startDate: String,
        endDate: String,
        orderBy: String,
        orderDirection: String
    ) async {
        eventTypeFilter = eventType.isEmpty ? nil : eventType
        versionFilter = version.isEmpty ? nil : version
        statusFilter = status.isEmpty ? nil : status
        startDateFilter = startDate.isEmpty ? nil : startDate
        endDateFilter = endDate.isEmpty ? nil : endDate
        orderByFilter = orderBy.isEmpty ? nil : orderBy
        orderDirectionFilter = orderDirection.isEmpty ? nil : orderDirection
        await load()
    }

    func loadMoreIfNeeded(currentItem: DivinationHistoryItem) async {
        guard !isLoadingMore, !isLoading else { return }
        guard hasMore else { return }

        // 只在最后一条触发分页
        guard let last = items.last, last.id == currentItem.id else { return }

        isLoadingMore = true
        errorMessage = nil

        do {
            let dto = try await service.listHistory(
                limit: limit,
                offset: items.count,
                eventType: eventTypeFilter,
                version: versionFilter,
                status: statusFilter,
                startDate: startDateFilter,
                endDate: endDateFilter,
                orderBy: orderByFilter,
                orderDirection: orderDirectionFilter
            )
            let newItems = dto.sessions.map(DivinationHistoryItem.init)
            items.append(contentsOf: newItems)
            total = dto.total
            hasMore = dto.has_more
        } catch {
            errorMessage = mapError(error, fallback: "加载更多失败")
        }

        isLoadingMore = false
    }

    private func mapError(_ error: Error, fallback: String) -> String {
        if let apiError = error as? APIError {
            return apiError.errorDescription ?? fallback
        }
        return (error as? LocalizedError)?.errorDescription ?? fallback
    }
}

