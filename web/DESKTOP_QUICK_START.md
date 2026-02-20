# DivineDaily Web 桌面版 - 快速启动指南

## 🚀 快速开始

### 1. 安装依赖
```bash
cd /mnt/DivineDaily/web
npm install
```

### 2. 启动开发服务器
```bash
npm run dev
```

### 3. 访问应用
- **开发环境**: http://localhost:5173
- **移动端预览**: 调整浏览器窗口宽度 < 1024px
- **桌面端预览**: 调整浏览器窗口宽度 ≥ 1024px

## 📱 响应式断点

| 断点 | 宽度范围 | 布局模式 | 导航方式 |
|------|---------|---------|---------|
| Mobile | 0 - 767px | 移动端 | 底部Tab Bar |
| Tablet | 768px - 1023px | 移动端 | 底部Tab Bar |
| Desktop | 1024px - 1439px | 桌面端 | 左侧边栏 |
| Wide | 1440px+ | 桌面端 | 左侧边栏 |

## 🎨 新增功能

### 桌面端特性
- ✅ 左侧导航栏（可折叠）
- ✅ 顶部工具栏（用户菜单、通知）
- ✅ Hero Section（首页大标题区域）
- ✅ 三列网格布局
- ✅ 数据表格组件
- ✅ 增强的卡片组件
- ✅ 键盘快捷键支持
- ✅ 拖拽排序功能
- ✅ 流畅的页面动画

### 保留的移动端功能
- ✅ 底部导航栏
- ✅ 触摸优化
- ✅ 安全区域适配
- ✅ 所有原有功能

## 🔧 开发指南

### 创建响应式页面
```tsx
import { useResponsive } from '../hooks/useResponsive';
import MobileVersion from './MobileVersion';
import DesktopVersion from './DesktopVersion';

export default function ResponsivePage() {
  const { isDesktopLayout } = useResponsive();
  return isDesktopLayout ? <DesktopVersion /> : <MobileVersion />;
}
```

### 使用桌面组件
```tsx
import { DesktopCard, DataTable } from '../components/desktop';

// 桌面卡片
<DesktopCard 
  title="标题"
  subtitle="副标题"
  variant="primary"
  size="default"
>
  内容
</DesktopCard>

// 数据表格
<DataTable
  columns={columns}
  data={data}
  rowKey="id"
  onRowClick={handleRowClick}
/>
```

### 使用响应式样式
```tsx
// 显示/隐藏
<div className="show-mobile">仅移动端显示</div>
<div className="show-desktop">仅桌面端显示</div>

// 响应式容器
<div className="responsive-container">
  <div className="responsive-grid">
    {/* 自动响应式网格 */}
  </div>
</div>
```

## 📂 项目结构

```
web/src/
├── components/
│   ├── desktop/          # 桌面端组件
│   │   ├── DesktopLayout.tsx
│   │   ├── Sidebar.tsx
│   │   ├── TopBar.tsx
│   │   ├── ResponsiveLayout.tsx
│   │   ├── DesktopCard.tsx
│   │   └── DataTable.tsx
│   └── mobile/           # 移动端组件（保留）
├── pages/
│   ├── HomePage.tsx      # 移动端首页
│   ├── HomePageDesktop.tsx  # 桌面端首页
│   └── HomePageResponsive.tsx  # 响应式包装器
├── hooks/
│   ├── useResponsive.ts  # 响应式Hook（增强版）
│   └── useDesktopInteractions.ts  # 桌面交互Hook
└── styles/
    ├── desktop.css       # 桌面端样式
    └── responsive.css    # 响应式工具类
```

## 🎯 测试清单

### 功能测试
- [ ] 在不同断点下测试布局切换
- [ ] 测试移动端所有功能正常
- [ ] 测试桌面端导航和交互
- [ ] 测试用户登录/登出流程

### 浏览器测试
- [ ] Chrome/Edge（最新版）
- [ ] Firefox（最新版）
- [ ] Safari（最新版）
- [ ] 移动端浏览器

### 性能测试
- [ ] 使用 Lighthouse 检查性能评分
- [ ] 测试首屏加载时间
- [ ] 测试页面切换流畅度

## 🐛 常见问题

### Q: 桌面端布局没有显示？
A: 确保浏览器窗口宽度 ≥ 1024px，可以按 F12 打开开发者工具查看当前宽度。

### Q: 样式没有生效？
A: 检查是否正确导入了 `desktop.css` 和 `responsive.css`，确认 `index.css` 中的导入顺序。

### Q: 移动端功能异常？
A: 桌面版改造完全保留了移动端功能，如有问题请检查 `ResponsiveLayout` 的条件判断。

### Q: 如何调试响应式布局？
A: 使用浏览器开发者工具的响应式设计模式（Ctrl+Shift+M），可以快速切换不同设备尺寸。

## 📚 相关文档

- [完整改造报告](./DESKTOP_VERSION_COMPLETE.md)
- [技术参考文档](../a-docs/TECHNICAL_REFERENCE.md)
- [架构设计文档](../a-docs/design/ARCH_AND_DESIGN.md)

## 🎉 下一步

1. 启动开发服务器测试功能
2. 根据需要完善其他页面的桌面版
3. 添加更多交互增强功能
4. 优化性能和用户体验
5. 准备生产环境部署

---

**祝你使用愉快！** 🌿✨

