import { MobilePage } from '../components/mobile';
import { Card, CardContent } from '../components/mobile/Card';
import './AboutPage.css';

export default function AboutPage() {
  return (
    <MobilePage>
      <div className="about-container">
        <div className="about-header">
          <div className="about-logo">🔮</div>
          <h1 className="about-title">Divine Daily</h1>
          <p className="about-version">v1.0.0</p>
        </div>

      <Card>
        <CardContent>
            <div className="about-section">
              <h3>关于我们</h3>
              <p>
                Divine Daily 是一款结合传统占卜智慧与现代 AI 技术的应用，
                为您提供周易、塔罗等多种占卜方式，帮助您探索内心、指引方向。
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <div className="about-section">
              <h3>功能特色</h3>
              <ul className="about-features">
                <li>🔮 周易占卜 - 传统易经智慧</li>
                <li>🎴 塔罗占卜 - 西方神秘学</li>
                <li>🤖 AI 解读 - 智能分析指导</li>
                <li>📊 运势分析 - 每日运势预测</li>
              </ul>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <div className="about-section">
              <h3>联系我们</h3>
              <p>如有问题或建议，欢迎联系我们：</p>
              <p className="about-contact">📧 support@divinedaily.com</p>
          </div>
        </CardContent>
      </Card>

        <div className="about-footer">
          <p>© 2024 Divine Daily. All rights reserved.</p>
        </div>
      </div>
    </MobilePage>
  );
}
