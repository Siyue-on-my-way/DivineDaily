# Divine Daily - Web Admin

管理后台项目，用于管理 Divine Daily 的配置和系统设置。

## 功能特性

- 🔐 管理员认证系统
- 🤖 LLM 配置管理
- 📝 Prompt 模板管理
- 📊 系统统计数据
- 👥 用户管理（即将推出）

## 技术栈

- React 19
- TypeScript
- React Router 7
- Axios
- Vite

## 开发

```bash
# 安装依赖
npm install

# 启动开发服务器（端口 5174）
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
VITE_APP_NAME=Divine Daily Admin
```

## 默认管理员账号

- 用户名: `admin`
- 密码: `594120`

## 项目结构

```
web-admin/
├── src/
│   ├── api/              # API 接口
│   │   ├── auth.ts       # 认证接口
│   │   └── config.ts     # 配置管理接口
│   ├── components/       # 组件
│   │   ├── admin/        # 管理后台布局组件
│   │   └── ui/           # 通用 UI 组件
│   ├── pages/            # 页面
│   │   ├── LoginPage.tsx # 登录页
│   │   └── admin/        # 管理页面
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
    server_name admin.divinedaily.com;
    
    root /var/www/divine-daily-admin;
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

1. 仅限管理员访问
2. 需要后端 API 支持
3. 建议使用 HTTPS
4. 定期更新管理员密码

## License

MIT
