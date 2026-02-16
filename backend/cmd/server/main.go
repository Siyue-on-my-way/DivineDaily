package main

import (
	"divine-daily-backend/internal/database"
	"divine-daily-backend/internal/handler"
	"divine-daily-backend/internal/middleware"
	"divine-daily-backend/internal/model"
	"divine-daily-backend/internal/repository"
	"divine-daily-backend/internal/service"
	"divine-daily-backend/pkg/jwt"
	"log"
	"os"

	"github.com/gin-gonic/gin"
)

func main() {
	// Initialize Database (PostgreSQL)
	if err := database.InitDB(); err != nil {
		log.Printf("Warning: Failed to initialize database: %v (will use default hexagrams)", err)
	} else {
		log.Println("Database initialized successfully")
	}
	defer database.CloseDB()

	// Initialize GORM Database (for auth system)
	if err := database.InitGormDB(); err != nil {
		log.Printf("Warning: Failed to initialize GORM database: %v", err)
	} else {
		log.Println("GORM database initialized successfully")
	}
	defer database.CloseGormDB()

	// 自动迁移用户表
	gormDB := database.GetGormDB()
	if gormDB != nil {
		if err := gormDB.AutoMigrate(&model.AuthUser{}, &model.UserSession{}); err != nil {
			log.Printf("Warning: Failed to migrate user tables: %v", err)
		} else {
			log.Println("User tables migrated successfully")
		
		// 初始化管理员用户
		if err := database.InitAdminUser(); err != nil {
			log.Printf("Warning: Failed to initialize admin user: %v", err)
		}
		}
	}

	// Initialize JWT Manager
	jwtSecret := getEnv("JWT_SECRET", "your-secret-key-change-in-production")
	jwtExpireHours := 24
	jwtRefreshExpireHours := 168 // 7 days
	jwtManager := jwt.NewJWTManager(jwtSecret, jwtExpireHours, jwtRefreshExpireHours)

	// Initialize Repository
	llmConfigRepo := repository.NewLLMConfigRepository(database.GetDB())
	promptConfigRepo := repository.NewPromptConfigRepository(database.GetDB())
	divinationRepo := repository.NewDivinationRepository(database.GetDB())
	userPatternRepo := repository.NewUserPatternRepository(database.GetDB())
	questionQualityRepo := repository.NewQuestionQualityRepository(database.GetDB())
	
	// 用户仓储（使用 GORM）
	var userRepo repository.UserRepository
	if gormDB != nil {
		userRepo = repository.NewUserRepository(gormDB)
	}

	// Initialize Service
	configSvc := service.NewConfigService(llmConfigRepo, promptConfigRepo)
	divinationSvc := service.NewDivinationService()
	divinationSvc.SetRepository(divinationRepo) // 注入数据库仓库
	divinationSvc.SetConfigService(configSvc)   // 注入配置服务
	timeConvertSvc := service.NewTimeConvertService()
	userProfileSvc := service.NewUserProfileService()
	
	// 认证服务（仅在 GORM 可用时初始化）
	var authService service.AuthService
	if userRepo != nil {
		authService = service.NewAuthService(userRepo, jwtManager)
	}

	preprocessingLLM := service.NewDatabaseLLMService(configSvc, "preprocessing")
	preprocessingSvc := service.NewIntelligentPreprocessingService(
		userPatternRepo,
		questionQualityRepo,
		userProfileSvc,
		preprocessingLLM,
	)

	// Daily Fortune Service
	dailyFortuneLLM := service.NewDatabaseLLMService(configSvc, "daily_fortune")
	dailyFortuneSvc := service.NewDailyFortuneService(timeConvertSvc, userProfileSvc, dailyFortuneLLM, configSvc)

	// Inject DailyFortuneService into DivinationService
	divinationSvc.SetDailyFortuneService(dailyFortuneSvc)

	// Initialize Handler
	divinationHandler := handler.NewDivinationHandler(divinationSvc)
	timeConvertHandler := handler.NewTimeConvertHandler(timeConvertSvc)
	userProfileHandler := handler.NewUserProfileHandler(userProfileSvc)
	dailyFortuneHandler := handler.NewDailyFortuneHandler(dailyFortuneSvc)
	configHandler := handler.NewConfigHandler(configSvc)
	preprocessingHandler := handler.NewIntelligentPreprocessingHandler(preprocessingSvc)
	
	// 认证处理器（仅在认证服务可用时初始化）
	var authHandler *handler.AuthHandler
	if authService != nil {
		authHandler = handler.NewAuthHandler(authService)
	}

	// Setup Router
	r := gin.Default()

	// CORS Middleware
	r.Use(corsMiddleware())

	// Health Check
	r.GET("/ping", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"message": "pong",
		})
	})

	// API V1 Routes
	v1 := r.Group("/api/v1")
	{
		// 认证路由（仅在认证系统可用时注册）
		if authHandler != nil {
			auth := v1.Group("/auth")
			{
				auth.POST("/register", authHandler.Register)
				auth.POST("/login", authHandler.Login)
				auth.POST("/refresh", authHandler.RefreshToken)
			}

			// 需要认证的认证路由
			authProtected := v1.Group("/auth")
			authProtected.Use(middleware.AuthMiddleware(jwtManager))
			{
				authProtected.GET("/me", authHandler.GetMe)
				authProtected.POST("/logout", authHandler.Logout)
			}
		}

		// 占卜路由（可选认证）
		divinations := v1.Group("/divinations")
		if jwtManager != nil {
			divinations.Use(middleware.OptionalAuthMiddleware(jwtManager))
		}
		{
			divinations.POST("/start", divinationHandler.StartDivination)
			divinations.GET("/:id/result", divinationHandler.GetResult)
			divinations.POST("/follow-up", divinationHandler.SubmitFollowUp)
			divinations.GET("/history", divinationHandler.ListHistory)
			divinations.GET("/history/count", divinationHandler.GetHistoryCount)
		}

		orientation := v1.Group("/orientation")
		if jwtManager != nil {
			orientation.Use(middleware.OptionalAuthMiddleware(jwtManager))
		}
		{
			orientation.POST("/recommend", divinationHandler.RecommendOrientation)
		}

		// 时间转换接口
		time := v1.Group("/time")
		{
			time.POST("/solar2lunar", timeConvertHandler.Solar2Lunar)
			time.POST("/lunar2solar", timeConvertHandler.Lunar2Solar)
		}

		// 用户档案接口
		profile := v1.Group("/profile")
		if jwtManager != nil {
			profile.Use(middleware.OptionalAuthMiddleware(jwtManager))
		}
		{
			profile.POST("", userProfileHandler.CreateOrUpdateProfile)
			profile.PUT("/:user_id", userProfileHandler.UpdateProfile)
			profile.GET("/:user_id", userProfileHandler.GetProfile)
		}

		// 每日运势接口
		v1.POST("/daily_fortune", dailyFortuneHandler.GenerateDailyFortune)

		// 智能预处理接口
		preprocess := v1.Group("/preprocess")
		{
			preprocess.POST("/question", preprocessingHandler.PreprocessQuestion)
		}

		// 配置管理接口（需要管理员权限）
		configs := v1.Group("/configs")
		if jwtManager != nil {
			configs.Use(middleware.AuthMiddleware(jwtManager))
			configs.Use(middleware.AdminMiddleware())
		}
		{
			// LLM配置
			llm := configs.Group("/llm")
			{
				llm.GET("", configHandler.ListLLMConfigs)
				llm.GET("/:id", configHandler.GetLLMConfig)
				llm.POST("", configHandler.CreateLLMConfig)
				llm.PUT("/:id", configHandler.UpdateLLMConfig)
				llm.DELETE("/:id", configHandler.DeleteLLMConfig)
				llm.POST("/:id/set-default", configHandler.SetDefaultLLMConfig)
				llm.POST("/:id/test", configHandler.TestLLMConfig)
			}

			// Prompt配置
			prompt := configs.Group("/prompt")
			{
				prompt.GET("", configHandler.ListPromptConfigs)
				prompt.GET("/:id", configHandler.GetPromptConfig)
				prompt.POST("", configHandler.CreatePromptConfig)
				prompt.PUT("/:id", configHandler.UpdatePromptConfig)
				prompt.DELETE("/:id", configHandler.DeletePromptConfig)
				prompt.POST("/:id/set-default", configHandler.SetDefaultPromptConfig)
				prompt.POST("/render", configHandler.RenderPrompt)
			}
		}
	}

	// Run Server
	port := getEnv("SERVER_PORT", "8080")
	log.Printf("Server starting on :%s", port)
	log.Printf("Authentication system: %v", authHandler != nil)
	if err := r.Run(":" + port); err != nil {
		log.Fatalf("Failed to run server: %v", err)
	}
}

// corsMiddleware CORS 中间件
func corsMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Writer.Header().Set("Access-Control-Allow-Origin", "*")
		c.Writer.Header().Set("Access-Control-Allow-Credentials", "true")
		c.Writer.Header().Set("Access-Control-Allow-Headers", "Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization, accept, origin, Cache-Control, X-Requested-With")
		c.Writer.Header().Set("Access-Control-Allow-Methods", "POST, OPTIONS, GET, PUT, DELETE")

		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}

		c.Next()
	}
}

// getEnv 获取环境变量，如果不存在则返回默认值
func getEnv(key, defaultValue string) string {
	value := os.Getenv(key)
	if value == "" {
		return defaultValue
	}
	return value
}
