package middleware

import (
	"net/http"
	"strings"

	"github.com/gin-gonic/gin"
	"divine-daily-backend/pkg/jwt"
)

// AuthMiddleware JWT 认证中间件
func AuthMiddleware(jwtManager *jwt.JWTManager) gin.HandlerFunc {
	return func(c *gin.Context) {
		// 1. 从请求头获取 Token
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			c.JSON(http.StatusUnauthorized, gin.H{
				"code":    http.StatusUnauthorized,
				"message": "未提供认证令牌",
			})
			c.Abort()
			return
		}

		// 2. 检查 Token 格式（Bearer Token）
		parts := strings.SplitN(authHeader, " ", 2)
		if len(parts) != 2 || parts[0] != "Bearer" {
			c.JSON(http.StatusUnauthorized, gin.H{
				"code":    http.StatusUnauthorized,
				"message": "认证令牌格式错误",
			})
			c.Abort()
			return
		}

		token := parts[1]

		// 3. 验证 Token
		claims, err := jwtManager.ValidateToken(token)
		if err != nil {
			statusCode := http.StatusUnauthorized
			message := "认证令牌无效"

			if err == jwt.ErrExpiredToken {
				message = "认证令牌已过期"
			}

			c.JSON(statusCode, gin.H{
				"code":    statusCode,
				"message": message,
			})
			c.Abort()
			return
		}

		// 4. 将用户信息注入到上下文
		c.Set("user_id", claims.UserID)
		c.Set("username", claims.Username)
		c.Set("user_role", claims.Role)

		// 5. 继续处理请求
		c.Next()
	}
}

// OptionalAuthMiddleware 可选认证中间件（不强制要求登录）
func OptionalAuthMiddleware(jwtManager *jwt.JWTManager) gin.HandlerFunc {
	return func(c *gin.Context) {
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			c.Next()
			return
		}

		parts := strings.SplitN(authHeader, " ", 2)
		if len(parts) != 2 || parts[0] != "Bearer" {
			c.Next()
			return
		}

		token := parts[1]
		claims, err := jwtManager.ValidateToken(token)
		if err == nil {
			c.Set("user_id", claims.UserID)
			c.Set("username", claims.Username)
			c.Set("user_role", claims.Role)
		}

		c.Next()
	}
}
