package middleware

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

// AdminMiddleware 管理员权限中间件
func AdminMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		// 从上下文获取用户角色（由 AuthMiddleware 注入）
		role, exists := c.Get("user_role")
		if !exists {
			c.JSON(http.StatusUnauthorized, gin.H{
				"code":    http.StatusUnauthorized,
				"message": "未授权访问",
			})
			c.Abort()
			return
		}

		// 检查是否为管理员
		if role != "admin" {
			c.JSON(http.StatusForbidden, gin.H{
				"code":    http.StatusForbidden,
				"message": "需要管理员权限",
			})
			c.Abort()
			return
		}

		c.Next()
	}
}
