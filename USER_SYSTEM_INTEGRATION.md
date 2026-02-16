# 用户系统接入完成报告

## 已完成的工作

### 1. 后端改动

#### 1.1 数据模型更新
- ✅ `internal/model/auth_user.go` - 添加 `role` 字段（admin/normal）
- ✅ `AuthUser` 模型包含角色信息
- ✅ `UserInfo` 响应包含角色信息

#### 1.2 JWT Token 更新
- ✅ `pkg/jwt/jwt.go` - JWT Claims 添加 `Role` 字段
- ✅ `GenerateToken()` 和 `GenerateRefreshToken()` 支持角色参数
- ✅ Token 中包含用户角色信息

#### 1.3 认证服务更新
- ✅ `internal/service/auth_service.go` - 注册时默认角色为 `normal`
- ✅ 登录时返回用户角色信息
- ✅ 支持邮箱或手机号注册（至少提供一个）

#### 1.4 验证器更新
- ✅ `pkg/validator/validator.go` - 验证邮箱和手机号格式
- ✅ 密码至少6位验证
- ✅ 两次密码一致性验证

#### 1.5 中间件
- ✅ `internal/middleware/auth_middleware.go` - 注入用户角色到上下文
- ✅ `internal/middleware/admin_middleware.go` - 管理员权限验证中间件

#### 1.6 初始化脚本
- ✅ `internal/database/init_admin.go` - 自动创建管理员用户
  - 用户名: `admin`
  - 邮箱: `admin@163.com`
  - 密码: `594120`
  - 角色: `admin`

#### 1.7 路由保护
- ✅ `cmd/server/main.go` - 配置管理接口添加管理员权限保护
- ✅ 启动时自动初始化管理员用户

### 2. 前端改动

#### 2.1 认证上下文更新
- ✅ `web/src/lib/AuthContext.tsx` - User 接口添加 `role` 字段
- ✅ 添加 `isAdmin()` 方法判断管理员权限

#### 2.2 API 更新
- ✅ `web/src/api/auth.ts` - 添加 `register()` 方法
- ✅ `RegisterRequest` 接口支持邮箱/手机号注册
- ✅ `LoginResponse` 包含角色信息

#### 2.3 路由保护组件
- ✅ `web/src/components/AdminRoute.tsx` - 管理员路由保护组件
- ✅ 未登录或非管理员自动跳转首页

#### 2.4 注册页面
- ✅ `web/src/pages/RegisterPage.tsx` - 用户注册页面
- ✅ `web/src/pages/RegisterPage.css` - 注册页面样式
- ✅ 支持用户名 + 邮箱/手机号 + 密码注册
- ✅ 前端表单验证

#### 2.5 路由更新
- ✅ `web/src/App.tsx` - 添加注册路由 `/register`
- ✅ 管理员路由使用 `AdminRoute` 保护

## 功能说明

### 用户角色
- **admin**: 管理员，可以访问 `/admin` 下的所有页面
- **normal**: 普通用户，只能访问占卜相关页面

### 注册规则
- 用户名：3-50个字符，只能包含字母、数字、下划线
- 邮箱或手机号：至少提供一个
  - 邮箱格式：标准邮箱格式
  - 手机号格式：中国大陆手机号（1开头11位）
- 密码：至少6位，最多32位
- 确认密码：必须与密码一致

### 默认管理员账号
- 用户名: `admin`
- 邮箱: `admin@163.com`
- 密码: `594120`
- 角色: `admin`

## 使用方式

### 后端启动
```bash
cd /mnt/DivineDaily/backend
go build -o server cmd/server/main.go
./server
```

首次启动会自动：
1. 迁移数据库表（users, user_sessions）
2. 创建默认管理员账号

### 前端启动
```bash
cd /mnt/DivineDaily/web
npm install
npm run dev
```

### 测试流程

#### 1. 普通用户注册
- 访问 `http://localhost:5173/register`
- 填写用户名、邮箱或手机号、密码
- 注册成功后自动登录

#### 2. 管理员登录
- 访问首页，点击登录
- 用户名: `admin`
- 密码: `594120`
- 登录成功后可访问 `/admin` 页面

#### 3. 权限测试
- 普通用户尝试访问 `/admin` 会被重定向到首页
- 管理员可以正常访问所有管理页面

## 注意事项

1. **编译问题**: 当前代码存在一些模型字段不匹配的问题，需要：
   - 检查 `LLMConfig` 是否包含 `Temperature`, `MaxTokens`, `TimeoutSeconds` 字段
   - 检查 `PromptConfig` 是否包含 `Scene`, `LLMConfigID` 等字段
   - 建议从 git 历史恢复完整的模型定义

2. **数据库迁移**: 首次运行会自动添加 `role` 字段到 users 表

3. **JWT Secret**: 生产环境请修改 `JWT_SECRET` 环境变量

4. **密码安全**: 使用 bcrypt 加密，默认 cost 为 10

## 下一步建议

1. 修复编译错误（模型字段不匹配）
2. 添加用户管理页面（管理员可查看/编辑用户）
3. 添加角色管理功能（支持更多角色）
4. 添加邮箱验证功能
5. 添加手机号验证码功能
6. 添加忘记密码功能
