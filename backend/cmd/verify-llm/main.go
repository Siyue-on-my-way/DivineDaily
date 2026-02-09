package main

import (
	"context"
	"database/sql"
	"divine-daily-backend/internal/model"

	"divine-daily-backend/internal/service"
	"fmt"
	"log"
	"os"

	_ "github.com/lib/pq"
)

func main() {
	// Initialize Database
	dbUser := os.Getenv("DB_USER")
	if dbUser == "" {
		dbUser = "divinedaily"
	}
	dbPassword := os.Getenv("DB_PASSWORD")
	if dbPassword == "" {
		dbPassword = "divinedaily_password"
	}
	dbName := os.Getenv("DB_NAME")
	if dbName == "" {
		dbName = "divinedaily"
	}
	dbHost := os.Getenv("DB_HOST")
	if dbHost == "" {
		dbHost = "localhost"
	}
	dbPort := os.Getenv("DB_PORT")
	if dbPort == "" {
		dbPort = "5432"
	}

	dsn := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=disable",
		dbHost, dbPort, dbUser, dbPassword, dbName)

	db, err := sql.Open("postgres", dsn)
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer db.Close()

	// Fetch Config ID 1
	var config model.LLMConfig
	query := `SELECT id, name, provider, url_type, api_key, endpoint, model_name, temperature, max_tokens, timeout_seconds FROM llm_configs WHERE id = 1`
	err = db.QueryRow(query).Scan(
		&config.ID, &config.Name, &config.Provider, &config.URLType, &config.APIKey,
		&config.Endpoint, &config.ModelName, &config.Temperature, &config.MaxTokens, &config.TimeoutSeconds,
	)
	if err != nil {
		log.Fatalf("Failed to fetch config: %v", err)
	}

	fmt.Printf("Config loaded: Endpoint=%s, URLType=%s, Model=%s\n", config.Endpoint, config.URLType, config.ModelName)

	// Test Connection
	llmSvc := service.NewOpenAIService(&config)
	fmt.Println("Testing connection...")

	resp, err := llmSvc.GenerateAnswer(context.Background(), "Hello! This is a verification test.")
	if err != nil {
		log.Fatalf("Test FAILED: %v", err)
	}

	fmt.Printf("Test SUCCESS! Response: %s\n", resp)
}
