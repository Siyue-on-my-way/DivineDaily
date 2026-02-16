# Admin 管理界面响应式设计需求文档

## 1. 需求背景

### 1.1 当前问题
- `/admin/config` 等管理界面只能通过直接输入 URL 访问
- 管理界面使用了移动端布局（MobileLayout），不适合桌面端操作
- 在正常的 APP 中没有入口可以跳转到管理界面
- 管理界面需要在桌面端和移动端都能良好显示

### 1.2 目标用户
- **桌面端用户**：管理员在电脑上进行配置管理，需要更大的操作空间和更丰富的交互
- **移动端用户**：管理员在手机上进行紧急配置调整，需要简洁的界面和便捷的操作

## 2. 功能需求

### 2.1 响应式布局
- **桌面端（≥768px）**
  - 使用独立的 AdminLayout，不使用 MobileLayout
  - 侧边栏导航 + 主内容区域的经典布局
  - 表格展示配置列表，支持更多列和操作按钮
  - 表单使用多列布局，提高空间利用率

- **移动端（<768px）**
  - 使用卡片式布局展示配置列表
  - 表单使用单列布局，适配小屏幕
  - 底部导航栏或汉堡菜单

### 2.2 访问入口

#### 2.2.1 桌面端入口
- 在顶部导航栏添加"管理"菜单（仅管理员可见）
- 下拉菜单包含：
  - LLM 配置管理
  - Prompt 配置管理
  - 用户管理（未来）
  - 系统设置（未来）

#### 2.2.2 移动端入口
- 在"我的"页面（ProfilePage）添加"管理中心"入口
- 需要管理员权限才能看到
- 点击后跳转到管理首页

### 2.3 权限控制
- 添加管理员角色判断
- 非管理员访问管理页面时重定向到首页
- 在导航中根据权限显示/隐藏管理入口

## 3. 技术设计

### 3.1 组件结构

```
src/
├── components/
│   ├── admin/                    # 管理界面专用组件
│   │   ├── AdminLayout.tsx       # 桌面端管理布局
│   │   ├── AdminSidebar.tsx      # 侧边栏导航
│   │   ├── AdminHeader.tsx       # 顶部导航栏
│   │   └── AdminMobileNav.tsx    # 移动端导航
│   ├── config/                   # 配置管理组件
│   │   ├── LLMConfigList.tsx     # LLM配置列表（响应式）
│   │   ├── LLMConfigForm.tsx     # LLM配置表单（响应式）
│   │   ├── PromptConfigList.tsx  # Prompt配置列表（响应式）
│   │   └── PromptConfigForm.tsx  # Prompt配置表单（响应式）
│   └── mobile/
│       └── MobileLayout.tsx      # 移动端布局（不用于管理页面）
├── pages/
│   ├── admin/                    # 管理页面
│   │   ├── AdminDashboard.tsx    # 管理首页
│   │   ├── LLMConfigPage.tsx     # LLM配置页面
│   │   └── PromptConfigPage.tsx  # Prompt配置页面
│   └── ConfigManagement.tsx      # 旧的配置管理页面（待重构）
└── hooks/
    ├── useResponsive.ts          # 响应式断点 Hook
    └── useAuth.ts                # 权限判断 Hook
```

### 3.2 路由设计

```typescript
// App.tsx
<Routes>
  {/* 普通用户路由 */}
  <Route path="/" element={<HomePage />} />
  <Route path="/divination" element={<DivinationPage />} />
  <Route path="/profile" element={<ProfilePage />} />
  
  {/* 管理员路由 - 使用 AdminLayout */}
  <Route path="/admin" element={<AdminLayout />}>
    <Route index element={<AdminDashboard />} />
    <Route path="llm-config" element={<LLMConfigPage />} />
    <Route path="prompt-config" element={<PromptConfigPage />} />
  </Route>
</Routes>
```

### 3.3 响应式断点

```typescript
// hooks/useResponsive.ts
export const breakpoints = {
  mobile: 0,
  tablet: 768,
  desktop: 1024,
  wide: 1440,
};

export function useResponsive() {
  const [screenSize, setScreenSize] = useState('mobile');
  
  useEffect(() => {
    const handleResize = () => {
      const width = window.innerWidth;
      if (width >= breakpoints.wide) setScreenSize('wide');
      else if (width >= breakpoints.desktop) setScreenSize('desktop');
      else if (width >= breakpoints.tablet) setScreenSize('tablet');
      else setScreenSize('mobile');
    };
    
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);
  
  return {
    isMobile: screenSize === 'mobile',
    isTablet: screenSize === 'tablet',
    isDesktop: screenSize === 'desktop' || screenSize === 'wide',
    screenSize,
  };
}
```

### 3.4 样式设计

#### 3.4.1 桌面端样式
```css
/* AdminLayout.css */
.admin-layout {
  display: flex;
  min-height: 100vh;
}

.admin-sidebar {
  width: 240px;
  background: #1a1a1a;
  color: white;
  position: fixed;
  height: 100vh;
  overflow-y: auto;
}

.admin-main {
  margin-left: 240px;
  flex: 1;
  background: #f5f5f5;
}

.admin-header {
  height: 60px;
  background: white;
  border-bottom: 1px solid #e0e0e0;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.admin-content {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}
```

#### 3.4.2 移动端样式
```css
/* 移动端适配 */
@media (max-width: 768px) {
  .admin-sidebar {
    transform: translateX(-100%);
    transition: transform 0.3s;
    z-index: 1000;
  }
  
  .admin-sidebar.open {
    transform: translateX(0);
  }
  
  .admin-main {
    margin-left: 0;
  }
  
  .admin-content {
    padding: 16px;
  }
}
```

## 4. 实施计划

### Phase 1: 基础架构（优先级：高）
- [ ] 创建 `useResponsive` Hook
- [ ] 创建 `AdminLayout` 组件（桌面端）
- [ ] 创建 `AdminSidebar` 组件
- [ ] 创建 `AdminHeader` 组件
- [ ] 更新路由配置

### Phase 2: 配置管理页面重构（优先级：高）
- [ ] 重构 `LLMConfigList` 为响应式组件
- [ ] 重构 `PromptConfigList` 为响应式组件
- [ ] 创建 `LLMConfigPage` 和 `PromptConfigPage`
- [ ] 添加表单验证和错误处理

### Phase 3: 访问入口（优先级：中）
- [ ] 在桌面端顶部导航添加"管理"菜单
- [ ] 在移动端"我的"页面添加"管理中心"入口
- [ ] 添加权限判断逻辑

### Phase 4: 权限系统（优先级：中）
- [ ] 实现管理员角色判断
- [ ] 添加路由守卫
- [ ] 添加权限提示页面

### Phase 5: 优化和测试（优先级：低）
- [ ] 添加加载状态和骨架屏
- [ ] 添加操作确认对话框
- [ ] 响应式测试（各种屏幕尺寸）
- [ ] 性能优化

## 5. UI/UX 设计要点

### 5.1 桌面端设计
- **配色方案**：深色侧边栏 + 浅色主内容区
- **导航**：固定侧边栏，支持折叠
- **表格**：支持排序、筛选、分页
- **表单**：多列布局，实时验证
- **操作反馈**：Toast 提示 + 确认对话框

### 5.2 移动端设计
- **配色方案**：与主 APP 保持一致
- **导航**：汉堡菜单或底部导航
- **列表**：卡片式布局，支持下拉刷新
- **表单**：单列布局，大按钮，易点击
- **操作反馈**：Toast 提示 + 底部弹出确认

### 5.3 交互设计
- **快捷操作**：常用操作放在列表项右侧
- **批量操作**：支持多选和批量删除/启用
- **搜索过滤**：实时搜索，支持多条件筛选
- **拖拽排序**：支持配置项的拖拽排序

## 6. 技术栈

- **React 18** - UI 框架
- **TypeScript** - 类型安全
- **React Router v6** - 路由管理
- **CSS Modules** - 样式方案
- **现有组件库** - 保持一致性

## 7. 兼容性要求

- **浏览器**：Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **移动端**：iOS 13+, Android 8+
- **屏幕尺寸**：320px - 2560px

## 8. 性能指标

- **首屏加载**：< 2s
- **页面切换**：< 300ms
- **表单提交**：< 1s
- **列表渲染**：支持虚拟滚动（100+ 项）

## 9. 安全考虑

- **权限验证**：前后端双重验证
- **敏感信息**：API Key 脱敏显示
- **操作日志**：记录所有配置变更
- **CSRF 防护**：使用 Token 验证

## 10. 未来扩展

- 用户管理
- 角色权限管理
- 系统日志查看
- 数据统计和报表
- 配置导入/导出
- 配置版本管理
