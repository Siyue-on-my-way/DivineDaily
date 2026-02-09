package main

import (
	"database/sql"
	"fmt"
	"log"
	"os"
	"strconv"
	"strings"

	_ "github.com/lib/pq"
	"github.com/xuri/excelize/v2"
)

// HexagramData 存储从Excel读取的卦象数据
type HexagramData struct {
	Number       int    // 卦序号
	Name         string // 卦名
	UpperTrigram string // 上卦
	LowerTrigram string // 下卦
	Summary      string // 卦辞摘要
	Detail       string // 详细解释
	Outcome      string // 吉凶
	Wuxing       string // 五行
}

func main() {
	if len(os.Args) < 2 {
		log.Fatal("Usage: go run main.go <excel_file_path> [connection_string]")
	}

	excelPath := os.Args[1]

	// 从环境变量或参数获取数据库连接字符串
	dsn := getDSN()
	if len(os.Args) >= 3 {
		dsn = os.Args[2]
	}

	// 读取Excel文件
	hexagrams, err := readExcelFile(excelPath)
	if err != nil {
		log.Fatalf("Failed to read Excel file: %v", err)
	}

	fmt.Printf("Read %d hexagrams from Excel\n", len(hexagrams))

	// 初始化数据库
	db, err := initDatabase(dsn)
	if err != nil {
		log.Fatalf("Failed to initialize database: %v", err)
	}
	defer db.Close()

	// 导入数据
	if err := importHexagrams(db, hexagrams); err != nil {
		log.Fatalf("Failed to import hexagrams: %v", err)
	}

	fmt.Printf("Successfully imported %d hexagrams to database\n", len(hexagrams))
}

// getDSN 从环境变量构建PostgreSQL连接字符串
func getDSN() string {
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

// readExcelFile 读取Excel文件并解析卦象数据
func readExcelFile(path string) ([]HexagramData, error) {
	f, err := excelize.OpenFile(path)
	if err != nil {
		return nil, fmt.Errorf("open file: %w", err)
	}
	defer f.Close()

	// 获取第一个工作表
	sheetName := f.GetSheetName(0)
	rows, err := f.GetRows(sheetName)
	if err != nil {
		return nil, fmt.Errorf("get rows: %w", err)
	}

	if len(rows) < 2 {
		return nil, fmt.Errorf("Excel file must have at least a header row and one data row")
	}

	// 解析表头，确定列索引
	header := rows[0]
	colMap := make(map[string]int)
	for i, h := range header {
		if h != "" {
			colMap[strings.TrimSpace(h)] = i
		}
	}

	fmt.Printf("Found columns: %v\n", colMap)

	var hexagrams []HexagramData

	// 解析数据行
	for rowIdx, row := range rows[1:] {
		if len(row) == 0 {
			continue
		}

		hexagram := HexagramData{}

		// 尝试从不同可能的列名读取数据
		// 序号
		if idx, ok := findColumn(colMap, "序号", "编号", "number", "Number"); ok {
			if idx < len(row) && row[idx] != "" {
				if num, err := strconv.Atoi(strings.TrimSpace(row[idx])); err == nil {
					hexagram.Number = num
				}
			}
		}

		// 卦名 - 支持从"标题"列解析
		if idx, ok := findColumn(colMap, "卦名", "名称", "name", "Name", "卦", "标题"); ok {
			if idx < len(row) && row[idx] != "" {
				title := strings.TrimSpace(row[idx])
				// 如果标题列包含序号和卦名（如"1. 乾为天"），尝试解析
				if hexagram.Number == 0 {
					// 尝试从标题中提取序号
					parts := strings.SplitN(title, ".", 2)
					if len(parts) == 2 {
						if num, err := strconv.Atoi(strings.TrimSpace(parts[0])); err == nil {
							hexagram.Number = num
							hexagram.Name = strings.TrimSpace(parts[1])
						} else {
							hexagram.Name = title
						}
					} else {
						hexagram.Name = title
					}
				} else {
					hexagram.Name = title
				}
			}
		}

		// 上卦
		if idx, ok := findColumn(colMap, "上卦", "上", "upper", "Upper", "上卦名"); ok {
			if idx < len(row) && row[idx] != "" {
				hexagram.UpperTrigram = strings.TrimSpace(row[idx])
			}
		}

		// 下卦
		if idx, ok := findColumn(colMap, "下卦", "下", "lower", "Lower", "下卦名"); ok {
			if idx < len(row) && row[idx] != "" {
				hexagram.LowerTrigram = strings.TrimSpace(row[idx])
			}
		}

		// 卦辞/摘要
		if idx, ok := findColumn(colMap, "卦辞", "摘要", "summary", "Summary", "简要", "说明"); ok {
			if idx < len(row) && row[idx] != "" {
				hexagram.Summary = strings.TrimSpace(row[idx])
			}
		}

		// 详细解释 - 支持"解释"列
		if idx, ok := findColumn(colMap, "详细", "解释", "detail", "Detail", "详解", "内容"); ok {
			if idx < len(row) && row[idx] != "" {
				hexagram.Detail = strings.TrimSpace(row[idx])
			}
		}

		// 吉凶
		if idx, ok := findColumn(colMap, "吉凶", "结果", "outcome", "Outcome", "判断"); ok {
			if idx < len(row) && row[idx] != "" {
				hexagram.Outcome = strings.TrimSpace(row[idx])
			}
		}

		// 五行
		if idx, ok := findColumn(colMap, "五行", "wuxing", "Wuxing", "属性"); ok {
			if idx < len(row) && row[idx] != "" {
				hexagram.Wuxing = strings.TrimSpace(row[idx])
			}
		}

		// 如果至少有序号和卦名，就添加
		// 如果没有序号，尝试从行号推断（第一行数据是第1卦）
		if hexagram.Number == 0 && hexagram.Name != "" {
			hexagram.Number = rowIdx + 1
		}

		if hexagram.Number > 0 && hexagram.Name != "" {
			hexagrams = append(hexagrams, hexagram)
		} else {
			fmt.Printf("Warning: Skipping row %d (missing number or name)\n", rowIdx+2)
		}
	}

	return hexagrams, nil
}

// findColumn 查找列名（支持多个可能的名称）
func findColumn(colMap map[string]int, names ...string) (int, bool) {
	for _, name := range names {
		if idx, ok := colMap[name]; ok {
			return idx, true
		}
		// 尝试不区分大小写
		for k, v := range colMap {
			if strings.EqualFold(k, name) {
				return v, true
			}
		}
	}
	return -1, false
}

// initDatabase 初始化PostgreSQL数据库
func initDatabase(dsn string) (*sql.DB, error) {
	db, err := sql.Open("postgres", dsn)
	if err != nil {
		return nil, fmt.Errorf("open database: %w", err)
	}

	// 测试连接
	if err := db.Ping(); err != nil {
		return nil, fmt.Errorf("ping database: %w", err)
	}

	// 创建表
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
		return nil, fmt.Errorf("create table: %w", err)
	}

	return db, nil
}

// importHexagrams 导入卦象数据到数据库
func importHexagrams(db *sql.DB, hexagrams []HexagramData) error {
	tx, err := db.Begin()
	if err != nil {
		return fmt.Errorf("begin transaction: %w", err)
	}
	defer tx.Rollback()

	// PostgreSQL使用ON CONFLICT处理重复
	stmt, err := tx.Prepare(`
		INSERT INTO hexagrams 
		(number, name, upper_trigram, lower_trigram, summary, detail, outcome, wuxing)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
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

	for _, h := range hexagrams {
		_, err := stmt.Exec(
			h.Number,
			h.Name,
			h.UpperTrigram,
			h.LowerTrigram,
			h.Summary,
			h.Detail,
			h.Outcome,
			h.Wuxing,
		)
		if err != nil {
			return fmt.Errorf("insert hexagram %d: %w", h.Number, err)
		}
		fmt.Printf("Imported: %d - %s\n", h.Number, h.Name)
	}

	if err := tx.Commit(); err != nil {
		return fmt.Errorf("commit transaction: %w", err)
	}

	return nil
}
