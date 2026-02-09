# SQLite to PostgreSQL 数据迁移脚本

## 功能

将SQLite数据库中的64卦数据迁移到PostgreSQL数据库中。

## 前置条件

### 1. 启动PostgreSQL容器

```bash
cd ../../docker
docker-compose up -d
```

### 2. 确保SQLite数据库文件存在

确保有SQLite数据库文件（如 `data/hexagrams.db`）

## 使用方法

### 方式1：使用环境变量（推荐）

```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_USER=divinedaily
export DB_PASSWORD=divinedaily123
export DB_NAME=divinedaily

cd backend/cmd/migrate-sqlite-to-postgres
go run main.go ../../data/hexagrams.db
```

### 方式2：直接指定PostgreSQL连接字符串

```bash
cd backend/cmd/migrate-sqlite-to-postgres
go run main.go ../../data/hexagrams.db \
  "host=localhost port=5432 user=divinedaily password=divinedaily123 dbname=divinedaily sslmode=disable"
```

## 参数说明

- **第一个参数**（必需）：SQLite数据库文件路径
- **第二个参数**（可选）：PostgreSQL连接字符串（DSN）。如果不提供，会从环境变量读取

## 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| DB_HOST | localhost | PostgreSQL主机地址 |
| DB_PORT | 5432 | PostgreSQL端口 |
| DB_USER | divinedaily | 数据库用户名 |
| DB_PASSWORD | divinedaily123 | 数据库密码 |
| DB_NAME | divinedaily | 数据库名 |
| DB_SSLMODE | disable | SSL模式 |

## 执行流程

脚本会按以下步骤执行：

1. **连接SQLite数据库** - 验证文件存在并连接
2. **读取数据** - 从SQLite读取所有hexagrams数据
3. **连接PostgreSQL** - 连接到PostgreSQL数据库
4. **创建表** - 确保PostgreSQL表存在（如果不存在则创建）
5. **迁移数据** - 批量将数据写入PostgreSQL
6. **验证数据** - 验证迁移后的数据数量

## 输出示例

```
=== SQLite to PostgreSQL Migration Tool ===
SQLite DB: ../../data/hexagrams.db
PostgreSQL DSN: host=localhost port=5432 user=divinedaily password=*** dbname=divinedaily sslmode=disable

Step 1: Connecting to SQLite database...
✓ SQLite connected successfully

Step 2: Reading data from SQLite...
✓ Read 64 hexagrams from SQLite

Step 3: Connecting to PostgreSQL database...
✓ PostgreSQL connected successfully

Step 4: Ensuring PostgreSQL table exists...
✓ Table ready

Step 5: Writing data to PostgreSQL...
  Progress: 10/64 migrated...
  Progress: 20/64 migrated...
  ...
  Progress: 60/64 migrated...
  Success: 64, Errors: 0
✓ Successfully migrated 64 hexagrams to PostgreSQL

Step 6: Verifying migration...
✓ Verified: 64 hexagrams in PostgreSQL database

=== Migration completed successfully! ===
```

## 特性

- ✅ **自动创建表**：如果PostgreSQL表不存在，会自动创建
- ✅ **冲突处理**：使用 `ON CONFLICT` 处理重复数据（基于number字段）
- ✅ **事务支持**：使用事务确保数据一致性
- ✅ **进度显示**：每10条记录显示一次进度
- ✅ **错误处理**：详细的错误信息和统计
- ✅ **数据验证**：迁移后自动验证数据数量

## 注意事项

1. **数据覆盖**：如果PostgreSQL中已存在相同number的记录，会被更新
2. **NULL值处理**：正确处理SQLite中的NULL值
3. **时间戳**：如果SQLite中没有时间戳，会使用当前时间
4. **事务回滚**：如果发生错误，事务会自动回滚

## 故障排查

### 问题1：SQLite文件不存在

```
Error: SQLite database file not found: ../../data/hexagrams.db
```

**解决**：检查SQLite文件路径是否正确

### 问题2：PostgreSQL连接失败

```
Error: Failed to connect to PostgreSQL: dial tcp: connect: connection refused
```

**解决**：确保PostgreSQL容器正在运行
```bash
docker-compose up -d
```

### 问题3：认证失败

```
Error: password authentication failed
```

**解决**：检查环境变量中的用户名和密码是否与docker-compose.yaml中的配置一致

### 问题4：表已存在但结构不同

脚本会自动创建表，但如果表已存在且结构不同，可能会报错。

**解决**：可以手动删除表后重新运行，或修改脚本使用 `DROP TABLE IF EXISTS`

## 相关文件

- `main.go` - 迁移脚本主文件
- `../../data/hexagrams.db` - SQLite数据库文件（如果存在）
- `../../docker/docker-compose.yaml` - PostgreSQL容器配置

