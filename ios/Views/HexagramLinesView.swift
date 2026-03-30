import SwiftUI

struct HexagramLinesView: View {
    let lineValues: [Int]

    var body: some View {
        VStack(spacing: 8) {
            ForEach(displayLines, id: \.index) { item in
                HStack(spacing: 12) {
                    Text("第\(item.label)爻")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    lineView(value: item.value)
                }
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }

    private var displayLines: [(index: Int, label: Int, value: Int)] {
        let reversed = Array(lineValues.reversed())
        return reversed.enumerated().map { index, value in
            (index: index, label: 6 - index, value: value)
        }
    }

    private func lineView(value: Int) -> some View {
        let isYang = value == 7 || value == 9
        let isChanging = value == 6 || value == 9

        return HStack(spacing: 6) {
            if isYang {
                Rectangle()
                    .fill(isChanging ? Color.orange.opacity(0.7) : Color.primary)
                    .frame(height: 6)
                    .cornerRadius(3)
            } else {
                Rectangle()
                    .fill(isChanging ? Color.orange.opacity(0.7) : Color.primary)
                    .frame(width: 30, height: 6)
                    .cornerRadius(3)
                Spacer(minLength: 16)
                Rectangle()
                    .fill(isChanging ? Color.orange.opacity(0.7) : Color.primary)
                    .frame(width: 30, height: 6)
                    .cornerRadius(3)
            }

            if isChanging {
                Text("变")
                    .font(.caption2)
                    .foregroundColor(.orange)
            }
        }
    }
}
