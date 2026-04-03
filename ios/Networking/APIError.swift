import Foundation

/// 统一的 API 错误模型
struct APIErrorDTO: Decodable {
    let detail: String?
    let message: String?
}

enum APIError: Error, LocalizedError {
    case unauthorized
    case forbidden
    case serverError(statusCode: Int, detail: String?)
    case networkError(String)
    case decodingError(String)

    var errorDescription: String? {
        switch self {
        case .unauthorized:
            return "登录已过期，请重新登录"
        case .forbidden:
            return "您没有权限执行此操作"
        case .serverError(_, let detail):
            return detail ?? "服务器错误，请稍后重试"
        case .networkError(let msg):
            return msg
        case .decodingError(let msg):
            return msg
        }
    }
}

