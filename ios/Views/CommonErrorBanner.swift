import SwiftUI

/// 简单的错误提示条，用于统一展示 API 或业务错误
struct CommonErrorBanner: View {
    let message: String

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text("错误")
                .font(.caption)
                .foregroundColor(.secondary)
            Text(message)
                .foregroundColor(.red)
                .font(.body)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.red.opacity(0.08))
        .cornerRadius(12)
    }
}

