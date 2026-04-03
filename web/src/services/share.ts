import type { DivinationResult } from '../types/divination';

interface ShareImageOptions {
  result: DivinationResult;
  userInfo?: {
    username: string;
    avatar?: string;
  };
}

export class ShareService {
  /**
   * 生成分享图片
   */
  static async generateShareImage(options: ShareImageOptions): Promise<Blob> {
    const { result } = options;

    // 创建 Canvas
    const canvas = document.createElement('canvas');
    canvas.width = 750;
    canvas.height = 1334;
    const ctx = canvas.getContext('2d');

    if (!ctx) {
      throw new Error('Failed to get canvas context');
    }

    // 绘制背景
    const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
    gradient.addColorStop(0, '#064E3B');
    gradient.addColorStop(0.5, '#047857');
    gradient.addColorStop(1, '#059669');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // 绘制装饰图案
    this.drawPattern(ctx, canvas.width, canvas.height);

    // 绘制内容卡片
    const cardX = 40;
    const cardY = 200;
    const cardWidth = canvas.width - 80;
    const cardHeight = 800;

    ctx.fillStyle = 'rgba(255, 255, 255, 0.95)';
    ctx.shadowColor = 'rgba(0, 0, 0, 0.2)';
    ctx.shadowBlur = 20;
    ctx.shadowOffsetY = 10;
    this.roundRect(ctx, cardX, cardY, cardWidth, cardHeight, 20);
    ctx.fill();
    ctx.shadowColor = 'transparent';

    // 绘制标题
    ctx.fillStyle = '#064E3B';
    ctx.font = 'bold 48px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(result.title || '占卜结果', canvas.width / 2, cardY + 80);

    // 绘制结果徽章
    if (result.outcome) {
      const badgeY = cardY + 150;
      const badgeWidth = 120;
      const badgeHeight = 50;
      const badgeX = (canvas.width - badgeWidth) / 2;

      ctx.fillStyle = this.getOutcomeColor(result.outcome);
      this.roundRect(ctx, badgeX, badgeY, badgeWidth, badgeHeight, 25);
      ctx.fill();

      ctx.fillStyle = 'white';
      ctx.font = 'bold 32px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(result.outcome, canvas.width / 2, badgeY + 38);
    }

    // 绘制摘要
    ctx.fillStyle = '#047857';
    ctx.font = '28px sans-serif';
    ctx.textAlign = 'center';
    const summaryLines = this.wrapText(ctx, result.summary, cardWidth - 80);
    let summaryY = cardY + 250;
    summaryLines.forEach(line => {
      ctx.fillText(line, canvas.width / 2, summaryY);
      summaryY += 40;
    });

    // 绘制评分（如果有）
    if (typeof result.daily_fortune?.overall_score === 'number') {
      const score = result.daily_fortune.overall_score;
      const scoreY = cardY + cardHeight - 200;

      ctx.fillStyle = '#10B981';
      ctx.font = 'bold 80px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(score.toString(), canvas.width / 2, scoreY);

      ctx.fillStyle = '#6B7280';
      ctx.font = '24px sans-serif';
      ctx.fillText('运势评分', canvas.width / 2, scoreY + 40);
    }

    // 绘制底部信息
    const footerY = cardY + cardHeight + 80;

    // Logo 和品牌名
    ctx.fillStyle = 'white';
    ctx.font = 'bold 36px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('🌿 DivineDaily', canvas.width / 2, footerY);

    ctx.font = '24px sans-serif';
    ctx.fillText('每日一卦，洞察人生', canvas.width / 2, footerY + 50);

    // 绘制二维码占位符（实际应用中可以集成 qrcode 库）
    const qrSize = 120;
    const qrX = (canvas.width - qrSize) / 2;
    const qrY = footerY + 100;
    ctx.fillStyle = 'white';
    this.roundRect(ctx, qrX, qrY, qrSize, qrSize, 10);
    ctx.fill();

    ctx.fillStyle = '#064E3B';
    ctx.font = '20px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('扫码查看', canvas.width / 2, qrY + qrSize / 2);

    // 转换为 Blob
    return new Promise((resolve, reject) => {
      canvas.toBlob(blob => {
        if (blob) {
          resolve(blob);
        } else {
          reject(new Error('Failed to generate image'));
        }
      }, 'image/png');
    });
  }

  /**
   * 分享到社交平台
   */
  static async share(result: DivinationResult, shareUrl: string): Promise<void> {
    // 尝试使用 Web Share API
    if (navigator.share) {
      try {
        await navigator.share({
          title: result.title || '我的占卜结果',
          text: result.summary,
          url: shareUrl
        });
        return;
      } catch (err: any) {
        // 用户取消分享
        if (err.name === 'AbortError') {
          throw err;
        }
        // 降级到复制链接
        console.warn('Web Share API failed, falling back to clipboard');
      }
    }

    // 降级方案：复制链接到剪贴板
    await navigator.clipboard.writeText(shareUrl);
  }

  /**
   * 下载分享图片
   */
  static async downloadImage(blob: Blob, filename: string = 'divination-result.png'): Promise<void> {
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  /**
   * 辅助方法：绘制圆角矩形
   */
  private static roundRect(
    ctx: CanvasRenderingContext2D,
    x: number,
    y: number,
    width: number,
    height: number,
    radius: number
  ): void {
    ctx.beginPath();
    ctx.moveTo(x + radius, y);
    ctx.lineTo(x + width - radius, y);
    ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
    ctx.lineTo(x + width, y + height - radius);
    ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
    ctx.lineTo(x + radius, y + height);
    ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
    ctx.lineTo(x, y + radius);
    ctx.quadraticCurveTo(x, y, x + radius, y);
    ctx.closePath();
  }

  /**
   * 辅助方法：文字换行
   */
  private static wrapText(ctx: CanvasRenderingContext2D, text: string, maxWidth: number): string[] {
    const words = text.split('');
    const lines: string[] = [];
    let currentLine = '';

    for (const word of words) {
      const testLine = currentLine + word;
      const metrics = ctx.measureText(testLine);

      if (metrics.width > maxWidth && currentLine !== '') {
        lines.push(currentLine);
        currentLine = word;
      } else {
        currentLine = testLine;
      }
    }

    if (currentLine) {
      lines.push(currentLine);
    }

    return lines;
  }

  /**
   * 辅助方法：绘制装饰图案
   */
  private static drawPattern(ctx: CanvasRenderingContext2D, width: number, height: number): void {
    ctx.fillStyle = 'rgba(255, 255, 255, 0.05)';
    
    // 绘制一些装饰圆圈
    for (let i = 0; i < 20; i++) {
      const x = Math.random() * width;
      const y = Math.random() * height;
      const radius = Math.random() * 50 + 20;
      
      ctx.beginPath();
      ctx.arc(x, y, radius, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  /**
   * 辅助方法：获取结果颜色
   */
  private static getOutcomeColor(outcome: string): string {
    if (outcome.includes('吉')) return '#10B981';
    if (outcome.includes('凶')) return '#EF4444';
    return '#3B82F6';
  }
}
