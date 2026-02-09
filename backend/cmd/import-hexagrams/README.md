# 64卦数据导入脚本

## 功能

将Excel文件中的64卦数据导入到PostgreSQL数据库中。

## 前置条件

### 1. 启动PostgreSQL容器

```bash
cd ../../docker
docker-compose up -d
```

### 2. 安装依赖

依赖已包含在 `go.mod` 中，运行：

```bash
cd backend
go mod download
```

## 使用方法

### 方式1：使用环境变量（推荐）

```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_USER=divinedaily
export DB_PASSWORD=divinedaily123
export DB_NAME=divinedaily

cd cmd/import-hexagrams
go run main.go ../../a-report/周易64卦象解释.xlsx
```

### 方式2：直接指定连接字符串

```bash
cd cmd/import-hexagrams
go run main.go ../../a-report/周易64卦象解释.xlsx \
  "host=localhost port=5432 user=divinedaily password=divinedaily123 dbname=divinedaily sslmode=disable"
```

## Excel文件格式要求

Excel文件应包含以下列（列名支持多种变体）：

- **序号/编号/Number**: 卦的序号（1-64）
- **卦名/名称/Name**: 卦的名称
- **上卦/Upper**: 上卦名称
- **下卦/Lower**: 下卦名称
- **卦辞/摘要/Summary**: 卦辞摘要
- **详细/解释/Detail**: 详细解释
- **吉凶/结果/Outcome**: 吉凶判断（吉/凶/平）
- **五行/Wuxing**: 五行属性

## 数据库结构

```sql
CREATE TABLE hexagrams (
    id SERIAL PRIMARY KEY,
    number INTEGER UNIQUE NOT NULL,      -- 卦序号（1-64）
    name TEXT NOT NULL,                  -- 卦名
    upper_trigram TEXT,                 -- 上卦
    lower_trigram TEXT,                 -- 下卦
    summary TEXT,                        -- 卦辞摘要
    detail TEXT,                         -- 详细解释
    outcome TEXT,                        -- 吉凶（吉/凶/平）
    wuxing TEXT,                         -- 五行属性
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 输出

脚本会：
1. 读取Excel文件并解析数据
2. 创建SQLite数据库（如果不存在）
3. 创建hexagrams表（如果不存在）
4. 导入所有卦象数据
5. 显示导入进度和结果

## 注意事项

- 如果数据库中已存在相同序号的卦，会使用 `ON CONFLICT ... DO UPDATE` 更新数据
- 至少需要有序号和卦名两列才能导入
- 其他列为可选，如果缺失会留空
- 确保PostgreSQL容器正在运行
- 默认连接参数：host=localhost, port=5432, user=divinedaily, password=divinedaily123, dbname=divinedaily

