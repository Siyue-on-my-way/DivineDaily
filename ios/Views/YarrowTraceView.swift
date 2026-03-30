import SwiftUI

struct YarrowTraceView: View {
    let trace: YarrowProcessTrace

    var body: some View {
        GroupBox("起卦过程（大衍筮法）") {
            VStack(alignment: .leading, spacing: 12) {
                Text("方法：\(trace.method.isEmpty ? "dayan_yarrow" : trace.method)")
                    .font(.caption)
                    .foregroundColor(.secondary)

                ForEach(trace.lines.sorted(by: { $0.lineIndex < $1.lineIndex }), id: \.lineIndex) { line in
                    DisclosureGroup {
                        VStack(alignment: .leading, spacing: 8) {
                            HStack(spacing: 12) {
                                Text("初始：\(line.initialStalks)")
                                Text("最终：\(line.finalStalks)")
                                Text("爻值：\(line.lineValue)")
                            }
                            .font(.caption)
                            .foregroundColor(.secondary)

                            ForEach(line.changes, id: \.stepIndex) { step in
                                VStack(alignment: .leading, spacing: 6) {
                                    Text("第 \(step.stepIndex) 变：\(step.stalksBefore) → \(step.stalksAfter)")
                                        .font(.subheadline)
                                    Text("左手：\(step.leftPile)（余 \(step.leftRemainder)）")
                                        .font(.caption)
                                        .foregroundColor(.secondary)
                                    Text("右手：\(step.rightPileBeforeHang) 挂一 → \(step.rightPileAfterHang)（余 \(step.rightRemainder)）")
                                        .font(.caption)
                                        .foregroundColor(.secondary)
                                    Text("本次去除：\(step.removed)")
                                        .font(.caption)
                                        .foregroundColor(.secondary)
                                }
                                if step.stepIndex != line.changes.last?.stepIndex {
                                    Divider()
                                }
                            }
                        }
                        .frame(maxWidth: .infinity, alignment: .leading)
                    } label: {
                        HStack {
                            Text("第\(line.lineIndex)爻 · \(line.lineType)")
                                .font(.subheadline)
                            if line.isChanging {
                                Text("变爻")
                                    .font(.caption)
                                    .padding(.horizontal, 6)
                                    .padding(.vertical, 2)
                                    .background(Color.orange.opacity(0.2))
                                    .clipShape(Capsule())
                            }
                        }
                    }
                }
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        }
    }
}
