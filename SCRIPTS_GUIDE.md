# Divine Daily 管理脚本说明

## 📋 脚本列表

Divine Daily 提供了一套完整的管理脚本，方便快速操作：

| 脚本 | 功能 | 用法 |
|------|------|------|
| `restart.sh` | 重启所有服务 | `./restart.sh` |
| `stop.sh` | 停止服务 | `./stop.sh` 或 `./stop.sh --all` |
| `logs.sh` | 查看日志 | `./logs.sh` 或 `./logs.sh backend` |
| `check.sh` | 检查配置 | `./check.sh` |
| `start.sh` | 快速启动 | `./start.sh` |

---

## 🚀 restart.sh - 重启服务

**功能**：停止并重新启动所有 Docker 服务

**用法**：
```bash
./restart.sh
```

**执行流程**：
1. 检查 Docker 环境
2. 停止现有服务
3. 清理旧容器
4. 启动所有服务
5. 显示服务状态和访问地址

**特点**：
- ✅ 自动检查 Docker 环境
- ✅ 彩色输出，清晰易读
- ✅ 显示服务信息和访问地址
- ✅ 提供常用命令提示

---

## 🛑 stop.sh - 停止服务

**功能**：停止 Docker 服务（支持多种模式）

**交互式用法**：
```bash
./stop.sh
```

然后选择：
1. 停止所有服务（保留数据）
2. 停止所有服务并删除数据卷
3. 仅停止前端服务
4. 仅停止后端服务

**命令行用法**：
```bash
# 停止所有服务
./stop.sh --all
./stop.sh -a

# 停止并清除数据
./stop.sh --clean
./stop.sh -c

# 仅停止前端
./stop.sh --frontend
./stop.sh -f

# 仅停止后端
./stop.sh --backend
./stop.sh -b

# 显示帮助
./stop.sh --help
```

**特点**：
- ✅ 支持交互式和命令行模式
- ✅ 可选择性停止服务
- ✅ 安全确认（删除数据时）
- ✅ 显示服务状态

---

## 📝 logs.sh - 查看日志

**功能**：查看各服务的日志输出

**交互式用法**：
```bash
./logs.sh
```

然后选择要查看的服务。

**命令行用法**：
```bash
# 查看所有服务日志
./logs.sh all
./logs.sh -a

# 查看数据库日志
./logs.sh postgres
./logs.sh -p

# 查看后端日志
./logs.sh backend
./logs.sh -b

# 查看移动端日志
./logs.sh web
./logs.sh -w

# 查看管理后台日志
./logs.sh admin
./logs.sh -m

# 显示帮助
./logs.sh --help
```

**特点**：
- ✅ 实时日志流（Ctrl+C 退出）
- ✅ 支持多种服务选择
- ✅ 交互式菜单
- ✅ 快捷命令支持

---

## ✅ check.sh - 配置检查

**功能**：检查项目配置是否正确

**用法**：
```bash
./check.sh
```

**检查项目**：
1. Docker 环境
2. 项目文件
3. 配置文件
4. 端口占用
5. Docker Compose 配置

**输出示例**：
```
✓ Docker 已安装
✓ Docker Compose 已安装
✓ docker-compose.yaml 存在
✓ 端口 40080 未被占用
...
检查结果: 15/15 通过
```

---

## 🎯 start.sh - 快速启动

**功能**：快速启动所有服务（简化版）

**用法**：
```bash
./start.sh
```

**特点**：
- ✅ 一键启动
- ✅ 显示访问地址
- ✅ 显示默认账号

---

## 📖 使用场景

### 场景 1：首次启动
```bash
# 1. 检查配置
./check.sh

# 2. 启动服务
./restart.sh

# 3. 查看日志（可选）
./logs.sh backend
```

### 场景 2：日常开发
```bash
# 启动服务
./restart.sh

# 修改代码后，查看日志
./logs.sh web

# 停止服务
./stop.sh --all
```

### 场景 3：调试问题
```bash
# 查看所有日志
./logs.sh all

# 或查看特定服务
./logs.sh backend
./logs.sh web
```

### 场景 4：清理重置
```bash
# 停止并清除所有数据
./stop.sh --clean

# 重新启动
./restart.sh
```

---

## 🔧 高级用法

### 组合使用

```bash
# 停止 → 检查 → 启动
./stop.sh -a && ./check.sh && ./restart.sh

# 重启并查看日志
./restart.sh && ./logs.sh backend
```

### 后台运行

```bash
# 启动服务后台运行
./restart.sh &

# 查看日志（不阻塞）
./logs.sh backend > backend.log 2>&1 &
```

---

## 📊 脚本对比

| 功能 | restart.sh | stop.sh | logs.sh | check.sh |
|------|-----------|---------|---------|----------|
| 启动服务 | ✅ | ❌ | ❌ | ❌ |
| 停止服务 | ✅ | ✅ | ❌ | ❌ |
| 查看日志 | ❌ | ❌ | ✅ | ❌ |
| 检查配置 | ✅ | ❌ | ❌ | ✅ |
| 交互式 | ❌ | ✅ | ✅ | ❌ |
| 命令行参数 | ❌ | ✅ | ✅ | ❌ |

---

## 💡 提示

1. **首次使用**：先运行 `./check.sh` 检查配置
2. **日常使用**：使用 `./restart.sh` 快速重启
3. **调试问题**：使用 `./logs.sh` 查看日志
4. **停止服务**：使用 `./stop.sh` 安全停止

---

## 🎨 彩色输出说明

脚本使用彩色输出提高可读性：

- 🔵 蓝色 (ℹ) - 信息提示
- 🟢 绿色 (✓) - 成功操作
- 🟡 黄色 (⚠) - 警告信息
- 🔴 红色 (✗) - 错误信息
- 🔷 青色 - 标题和重要信息

---

## 📞 获取帮助

所有脚本都支持 `--help` 参数：

```bash
./stop.sh --help
./logs.sh --help
```

---

**快速参考**：
- 启动: `./restart.sh`
- 停止: `./stop.sh -a`
- 日志: `./logs.sh backend`
- 检查: `./check.sh`
