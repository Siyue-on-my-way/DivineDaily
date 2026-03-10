import Foundation

enum APIError: LocalizedError {
    case invalidURL
    case invalidResponse
    case server(statusCode: Int, message: String)
    case decoding(Error)
    case network(Error)
    case unauthorized

    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "无效的请求地址"
        case .invalidResponse:
            return "服务器响应异常"
        case let .server(statusCode, message):
            if !message.isEmpty {
                return message
            }
            switch statusCode {
            case 400:
                return "请求参数有误，请检查后重试"
            case 403:
                return "当前账号暂无权限执行此操作"
            case 404:
                return "请求的资源不存在"
            case 408:
                return "请求超时，请稍后重试"
            case 429:
                return "请求过于频繁，请稍后再试"
            case 500...599:
                return "服务暂时不可用，请稍后重试"
            default:
                return "请求失败（\(statusCode)）"
            }
        case let .decoding(error):
            return "数据解析失败：\(error.localizedDescription)"
        case let .network(error):
            if let urlError = error as? URLError {
                switch urlError.code {
                case .timedOut:
                    return "请求超时，请检查网络后重试"
                case .notConnectedToInternet:
                    return "当前无网络连接"
                case .cannotFindHost, .cannotConnectToHost:
                    return "无法连接到服务器，请确认本地后端已启动"
                default:
                    return "网络异常：\(urlError.localizedDescription)"
                }
            }
            return "网络异常：\(error.localizedDescription)"
        case .unauthorized:
            return "登录状态已失效，请重新登录"
        }
    }
}
