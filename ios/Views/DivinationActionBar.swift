import SwiftUI

struct DivinationActionBar: View {
    let onSave: () -> Void
    let onShare: () -> Void
    let isSaving: Bool
    let isSharing: Bool

    var body: some View {
        HStack(spacing: 12) {
            Button(action: onSave) {
                Label(isSaving ? "保存中..." : "保存", systemImage: "tray.and.arrow.down")
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(.bordered)
            .disabled(isSaving)

            Button(action: onShare) {
                Label(isSharing ? "分享中..." : "分享", systemImage: "square.and.arrow.up")
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(.borderedProminent)
            .disabled(isSharing)
        }
    }
}
