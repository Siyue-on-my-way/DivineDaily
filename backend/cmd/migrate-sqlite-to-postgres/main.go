package main

import (
	"database/sql"
	"fmt"
	"log"
	"os"
	"time"

	_ "github.com/lib/pq"
	_ "github.com/mattn/go-sqlite3"
)

// Hexagram 卦象数据结构
type Hexagram struct {
	ID           int
	Number       int
	Name         string
	UpperTrigram sql.NullString
	LowerTrigram sql.NullString
	Summary      sql.NullString
	Detail       sql.NullString
	Outcome      sql.NullString
	Wuxing       sql.NullString
	CreatedAt    sql.NullTime
	UpdatedAt    sql.NullTime
}

func main() {
	// 获取命令行参数
	if len(os.Args) < 2 {
		log.Fatal("Usage: go run main.go <sqlite_db_path> [postgres_dsn]")
	}

	sqlitePath := os.Args[1]
	postgresDSN := getPostgresDSN()

	if len(os.Args) >= 3 {
		postgresDSN = os.Args[2]
	}

	fmt.Println("=== SQLite to PostgreSQL Migration Tool ===")
	fmt.Printf("SQLite DB: %s\n", sqlitePath)
	fmt.Printf("PostgreSQL DSN: %s\n", maskPassword(postgresDSN))
	fmt.Println()

	// 1. 连接SQLite数据库
	fmt.Println("Step 1: Connecting to SQLite database...")
	sqliteDB, err := connectSQLite(sqlitePath)
	if err != nil {
		log.Fatalf("Failed to connect to SQLite: %v", err)
	}
	defer sqliteDB.Close()
	fmt.Println("✓ SQLite connected successfully")

	// 2. 读取SQLite数据
	fmt.Println("\nStep 2: Reading data from SQLite...")
	hexagrams, err := readFromSQLite(sqliteDB)
	if err != nil {
		log.Fatalf("Failed to read from SQLite: %v", err)
	}
	fmt.Printf("✓ Read %d hexagrams from SQLite\n", len(hexagrams))

	if len(hexagrams) == 0 {
		log.Fatal("No data found in SQLite database. Nothing to migrate.")
	}

	// 3. 连接PostgreSQL数据库
	fmt.Println("\nStep 3: Connecting to PostgreSQL database...")
	postgresDB, err := connectPostgres(postgresDSN)
	if err != nil {
		log.Fatalf("Failed to connect to PostgreSQL: %v", err)
	}
	defer postgresDB.Close()
	fmt.Println("✓ PostgreSQL connected successfully")

	// 4. 确保PostgreSQL表存在
	fmt.Println("\nStep 4: Ensuring PostgreSQL table exists...")
	if err := createPostgresTable(postgresDB); err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}
	fmt.Println("✓ Table ready")

	// 5. 写入PostgreSQL
	fmt.Println("\nStep 5: Writing data to PostgreSQL...")
	if err := writeToPostgres(postgresDB, hexagrams); err != nil {
		log.Fatalf("Failed to write to PostgreSQL: %v", err)
	}
	fmt.Printf("✓ Successfully migrated %d hexagrams to PostgreSQL\n", len(hexagrams))

	// 6. 验证数据
	fmt.Println("\nStep 6: Verifying migration...")
	count, err := verifyPostgresData(postgresDB)
	if err != nil {
		log.Printf("Warning: Failed to verify data: %v", err)
	} else {
		fmt.Printf("✓ Verified: %d hexagrams in PostgreSQL database\n", count)
	}

	fmt.Println("\n=== Migration completed successfully! ===")
}

// connectSQLite 连接SQLite数据库
func connectSQLite(path string) (*sql.DB, error) {
	// 检查文件是否存在
	if _, err := os.Stat(path); os.IsNotExist(err) {
		return nil, fmt.Errorf("SQLite database file not found: %s", path)
	}

	db, err := sql.Open("sqlite3", path)
	if err != nil {
		return nil, fmt.Errorf("open SQLite: %w", err)
	}

	if err := db.Ping(); err != nil {
		return nil, fmt.Errorf("ping SQLite: %w", err)
	}

	return db, nil
}

// connectPostgres 连接PostgreSQL数据库
func connectPostgres(dsn string) (*sql.DB, error) {
	db, err := sql.Open("postgres", dsn)
	if err != nil {
		return nil, fmt.Errorf("open PostgreSQL: %w", err)
	}

	if err := db.Ping(); err != nil {
		return nil, fmt.Errorf("ping PostgreSQL: %w", err)
	}

	// 设置连接池
	db.SetMaxOpenConns(25)
	db.SetMaxIdleConns(5)

	return db, nil
}

// readFromSQLite 从SQLite读取所有数据
func readFromSQLite(db *sql.DB) ([]Hexagram, error) {
	query := `
		SELECT id, number, name, upper_trigram, lower_trigram, 
		       summary, detail, outcome, wuxing, 
		       created_at, updated_at
		FROM hexagrams
		ORDER BY number
	`

	rows, err := db.Query(query)
	if err != nil {
		return nil, fmt.Errorf("query SQLite: %w", err)
	}
	defer rows.Close()

	var hexagrams []Hexagram
	for rows.Next() {
		var h Hexagram
		err := rows.Scan(
			&h.ID,
			&h.Number,
			&h.Name,
			&h.UpperTrigram,
			&h.LowerTrigram,
			&h.Summary,
			&h.Detail,
			&h.Outcome,
			&h.Wuxing,
			&h.CreatedAt,
			&h.UpdatedAt,
		)
		if err != nil {
			return nil, fmt.Errorf("scan row: %w", err)
		}
		hexagrams = append(hexagrams, h)
	}

	if err := rows.Err(); err != nil {
		return nil, fmt.Errorf("rows error: %w", err)
	}

	return hexagrams, nil
}

// createPostgresTable 创建PostgreSQL表（如果不存在）
func createPostgresTable(db *sql.DB) error {
	createTableSQL := `
	CREATE TABLE IF NOT EXISTS hexagrams (
		id SERIAL PRIMARY KEY,
		number INTEGER UNIQUE NOT NULL,
		name TEXT NOT NULL,
		upper_trigram TEXT,
		lower_trigram TEXT,
		summary TEXT,
		detail TEXT,
		outcome TEXT,
		wuxing TEXT,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	);

	CREATE INDEX IF NOT EXISTS idx_hexagram_number ON hexagrams(number);
	CREATE INDEX IF NOT EXISTS idx_hexagram_name ON hexagrams(name);
	`

	if _, err := db.Exec(createTableSQL); err != nil {
		return fmt.Errorf("create table: %w", err)
	}

	return nil
}

// writeToPostgres 将数据写入PostgreSQL
func writeToPostgres(db *sql.DB, hexagrams []Hexagram) error {
	// 开始事务
	tx, err := db.Begin()
	if err != nil {
		return fmt.Errorf("begin transaction: %w", err)
	}
	defer tx.Rollback()

	// 准备插入语句（使用ON CONFLICT处理重复）
	stmt, err := tx.Prepare(`
		INSERT INTO hexagrams 
		(number, name, upper_trigram, lower_trigram, summary, detail, outcome, wuxing, created_at, updated_at)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
		ON CONFLICT (number) 
		DO UPDATE SET 
			name = EXCLUDED.name,
			upper_trigram = EXCLUDED.upper_trigram,
			lower_trigram = EXCLUDED.lower_trigram,
			summary = EXCLUDED.summary,
			detail = EXCLUDED.detail,
			outcome = EXCLUDED.outcome,
			wuxing = EXCLUDED.wuxing,
			updated_at = CURRENT_TIMESTAMP
	`)
	if err != nil {
		return fmt.Errorf("prepare statement: %w", err)
	}
	defer stmt.Close()

	// 批量插入
	successCount := 0
	errorCount := 0

	for i, h := range hexagrams {
		// 处理NULL值
		var upperTrigram, lowerTrigram, summary, detail, outcome, wuxing interface{}
		var createdAt, updatedAt interface{}

		if h.UpperTrigram.Valid {
			upperTrigram = h.UpperTrigram.String
		}
		if h.LowerTrigram.Valid {
			lowerTrigram = h.LowerTrigram.String
		}
		if h.Summary.Valid {
			summary = h.Summary.String
		}
		if h.Detail.Valid {
			detail = h.Detail.String
		}
		if h.Outcome.Valid {
			outcome = h.Outcome.String
		}
		if h.Wuxing.Valid {
			wuxing = h.Wuxing.String
		}
		if h.CreatedAt.Valid {
			createdAt = h.CreatedAt.Time
		} else {
			createdAt = time.Now()
		}
		if h.UpdatedAt.Valid {
			updatedAt = h.UpdatedAt.Time
		} else {
			updatedAt = time.Now()
		}

		_, err := stmt.Exec(
			h.Number,
			h.Name,
			upperTrigram,
			lowerTrigram,
			summary,
			detail,
			outcome,
			wuxing,
			createdAt,
			updatedAt,
		)

		if err != nil {
			errorCount++
			log.Printf("Error inserting hexagram %d (%s): %v", h.Number, h.Name, err)
		} else {
			successCount++
			if (i+1)%10 == 0 {
				fmt.Printf("  Progress: %d/%d migrated...\n", i+1, len(hexagrams))
			}
		}
	}

	// 提交事务
	if err := tx.Commit(); err != nil {
		return fmt.Errorf("commit transaction: %w", err)
	}

	fmt.Printf("  Success: %d, Errors: %d\n", successCount, errorCount)

	if errorCount > 0 {
		return fmt.Errorf("migration completed with %d errors", errorCount)
	}

	return nil
}

// verifyPostgresData 验证PostgreSQL中的数据
func verifyPostgresData(db *sql.DB) (int, error) {
	var count int
	err := db.QueryRow("SELECT COUNT(*) FROM hexagrams").Scan(&count)
	if err != nil {
		return 0, err
	}
	return count, nil
}

// getPostgresDSN 从环境变量获取PostgreSQL连接字符串
func getPostgresDSN() string {
	host := getEnv("DB_HOST", "localhost")
	port := getEnv("DB_PORT", "5432")
	user := getEnv("DB_USER", "divinedaily")
	password := getEnv("DB_PASSWORD", "divinedaily123")
	dbname := getEnv("DB_NAME", "divinedaily")
	sslmode := getEnv("DB_SSLMODE", "disable")

	return fmt.Sprintf(
		"host=%s port=%s user=%s password=%s dbname=%s sslmode=%s",
		host, port, user, password, dbname, sslmode,
	)
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

// maskPassword 隐藏密码用于显示
func maskPassword(dsn string) string {
	// 简单处理：将password=xxx替换为password=***
	// 实际应用中可以使用更复杂的字符串处理
	result := dsn
	start := 0
	for {
		idx := findSubstring(result, "password=", start)
		if idx == -1 {
			break
		}
		startIdx := idx + 9 // "password="的长度
		endIdx := startIdx
		for endIdx < len(result) && result[endIdx] != ' ' {
			endIdx++
		}
		if endIdx > startIdx {
			result = result[:startIdx] + "***" + result[endIdx:]
		}
		start = startIdx + 3
	}
	return result
}

func findSubstring(s, substr string, start int) int {
	if start >= len(s) {
		return -1
	}
	idx := start
	for idx < len(s) {
		if idx+len(substr) <= len(s) && s[idx:idx+len(substr)] == substr {
			return idx
		}
		idx++
	}
	return -1
}
