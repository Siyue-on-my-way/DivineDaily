import Foundation

@MainActor
final class HistoryStore: ObservableObject {
    @Published var isLoading = false
    @Published var isLoadingMore = false
    @Published var errorMessage: String?
    @Published var items: [DivinationHistoryItem] = []

    @Published var selectedEventType: String = ""
    @Published var selectedVersion: String = ""
    @Published var selectedStatus: String = ""

    private(set) var hasMore = true
    private(set) var total = 0
    private(set) var offset = 0
    private let limit = 20

    private let service: DivinationService

    init(authStore: AuthStore) {
        self.service = AppEnvironment.shared.makeDivinationService { [weak authStore] in
            Task { @MainActor in authStore?.logout() }
        }
    }

    func load() async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }

        do {
            offset = 0
            let response = try await service.getHistory(
                limit: limit,
                offset: offset,
                eventType: selectedEventType,
                version: selectedVersion,
                status: selectedStatus,
                orderBy: "created_at",
                orderDirection: "desc"
            )

            items = response.sessions.map(DivinationHistoryItem.init)
            total = response.total
            hasMore = response.has_more
            offset = items.count
        } catch {
            errorMessage = (error as? LocalizedError)?.errorDescription ?? "加载历史失败"
        }
    }

    func loadMoreIfNeeded(currentItem item: DivinationHistoryItem) async {
        guard let last = items.last, last.id == item.id else { return }
        guard hasMore, !isLoading, !isLoadingMore else { return }

        isLoadingMore = true
        defer { isLoadingMore = false }

        do {
            let response = try await service.getHistory(
                limit: limit,
                offset: offset,
                eventType: selectedEventType,
                version: selectedVersion,
                status: selectedStatus,
                orderBy: "created_at",
                orderDirection: "desc"
            )

            let newItems = response.sessions.map(DivinationHistoryItem.init)
            items.append(contentsOf: newItems)
            total = response.total
            hasMore = response.has_more
            offset = items.count
        } catch {
            errorMessage = (error as? LocalizedError)?.errorDescription ?? "加载更多失败"
        }
    }

    func applyFilters(eventType: String, version: String, status: String) async {
        selectedEventType = eventType
        selectedVersion = version
        selectedStatus = status
        await load()
    }
}
