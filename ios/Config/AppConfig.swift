import Foundation

/// iOS 端后端 API 配置
///
/// 开发阶段默认指向 docker-compose 映射后的端口；你也可以在调试/测试时通过 UserDefaults 覆盖。
struct AppConfig {
    private static let apiBaseURLKey = "API_BASE_URL"

    /// 形如：`http://localhost:48080/api/v1`
    static var apiBaseURLString: String {
        UserDefaults.standard.string(forKey: apiBaseURLKey) ?? "http://localhost:48080/api/v1"
    }

    static var apiBaseURL: URL {
        // 强制兜底，避免 URL 构建失败导致崩溃
        URL(string: apiBaseURLString) ?? URL(string: "http://localhost:48080/api/v1")!
    }
}

