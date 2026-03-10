import Foundation

enum AppConfig {
    // iOS 模拟器访问宿主机可使用 127.0.0.1；真机请改为局域网 IP
    static let baseURL = URL(string: "http://127.0.0.1:48080/api/v1")!
    static let requestTimeout: TimeInterval = 30
}
