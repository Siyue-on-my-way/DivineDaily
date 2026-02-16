# Divine Daily - 移动端应用

Divine Daily 移动端占卜应用，提供周易六爻、塔罗牌占卜和每日运势服务。

## 功能特性

- 🔮 周易占卜 - 传统易经智慧
- 🎴 塔罗占卜 - 西方神秘学
- 🌟 每日运势 - 个性化运势预测
- 📜 历史记录 - 保存占卜历史
- 👤 个人中心 - 用户信息管理

## 技术栈

- React 19
- TypeScript
- React Router 7
- Axios
- Framer Motion
- Vite

## 开发

```bash
# 安装依赖
npm install

# 启动开发服务器（端口 5173）
npm run dev

# 构建生产版本
npm run build

# 预览生产版本
npm run preview
```

## 环境变量

创建 `.env` 文件：

```env
VITE_API_BASE_URL=http://localhost:8080/api/v1
VITE_API_PROXY_TARGET=http://localhost:8080
VITE_APP_NAME=Divine Daily
```

## 项目结构

```
web/
├── src/
│   ├── api/              # API 接口
│   │   ├── auth.ts       # 认证接口
│   │   ├── divination.ts # 占卜接口
│   │   └── fortune.ts    # 运势接口
│   ├── components/       # 组件
│   │   ├── mobile/       # 移动端组件
│   │   ├── divination/   # 占卜组件
│   │   ├── tarot/        # 塔罗组件
│   │   └── ui/           # 通用 UI 组件
│   ├── pages/            # 页面
│   │   ├── HomePage.tsx
│   │   ├── DivinationPage.tsx
│   │   ├── TarotPage.tsx
│   │   ├── ProfilePage.tsx
│   │   └── ...
│   ├── lib/              # 核心库
│   │   ├── AuthContext.tsx
│   │   └── axios.ts
│   ├── App.tsx           # 应用入口
│   └── main.tsx          # 主入口
├── package.json
└── vite.config.ts
```

## 部署

### 构建

```bash
npm run build
```

构建产物在 `dist/` 目录。

### Nginx 配置示例

```nginx
server {
    listen 80;
    server_name app.divinedaily.com;
    
    root /var/www/divine-daily-web;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 注意事项

1. 移动端优先设计
2. 需要后端 API 支持
3. 建议使用 HTTPS
4. 支持访客模式

## License

MIT
