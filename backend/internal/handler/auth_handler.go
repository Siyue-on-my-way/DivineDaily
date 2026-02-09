package handler

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"divine-daily-backend/internal/model"
	"divine-daily-backend/internal/service"
)

// AuthHandler 认证处理器
type AuthHandler struct {
	authService service.AuthService
}

// NewAuthHandler 创建认证处理器
func NewAuthHandler(authService service.AuthService) *AuthHandler {
	return &AuthHandler{
		authService: authService,
	}
}


// Register 用户注册
func (h *AuthHandler) Register(c *gin.Context) {
	var req model.RegisterRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, Response{
			Code:    http.StatusBadRequest,
			Message: "请求参数错误: " + err.Error(),
		})
		return
	}

	resp, err := h.authService.Register(&req)
	if err != nil {
		statusCode := http.StatusInternalServerError
		message := "注册失败"

		switch err {
		case service.ErrUsernameTaken:
			statusCode = http.StatusBadRequest
			message = "用户名已被占用"
		case service.ErrEmailTaken:
			statusCode = http.StatusBadRequest
			message = "邮箱已被注册"
		case service.ErrPhoneTaken:
			statusCode = http.StatusBadRequest
			message = "手机号已被注册"
		case service.ErrInvalidInput:
			statusCode = http.StatusBadRequest
			message = err.Error()
		}

		c.JSON(statusCode, Response{
			Code:    statusCode,
			Message: message,
		})
		return
	}

	c.JSON(http.StatusOK, Response{
		Code:    http.StatusOK,
		Message: "注册成功",
		Data:    resp,
	})
}

// Login 用户登录
func (h *AuthHandler) Login(c *gin.Context) {
	var req model.LoginRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, Response{
			Code:    http.StatusBadRequest,
			Message: "请求参数错误: " + err.Error(),
		})
		return
	}

	resp, err := h.authService.Login(&req)
	if err != nil {
		statusCode := http.StatusInternalServerError
		message := "登录失败"

		switch err {
		case service.ErrInvalidCredentials:
			statusCode = http.StatusUnauthorized
			message = "用户名或密码错误"
		case service.ErrAccountDisabled:
			statusCode = http.StatusForbidden
			message = "账号已被禁用"
		}

		c.JSON(statusCode, Response{
			Code:    statusCode,
			Message: message,
		})
		return
	}

	c.JSON(http.StatusOK, Response{
		Code:    http.StatusOK,
		Message: "登录成功",
		Data:    resp,
	})
}

// Logout 用户登出
func (h *AuthHandler) Logout(c *gin.Context) {
	// 从上下文获取用户 ID（由中间件注入）
	userID, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusUnauthorized, Response{
			Code:    http.StatusUnauthorized,
			Message: "未授权",
		})
		return
	}

	// 获取 Token
	token := c.GetHeader("Authorization")
	if len(token) > 7 && token[:7] == "Bearer " {
		token = token[7:]
	}

	if err := h.authService.Logout(userID.(int64), token); err != nil {
		c.JSON(http.StatusInternalServerError, Response{
			Code:    http.StatusInternalServerError,
			Message: "登出失败",
		})
		return
	}

	c.JSON(http.StatusOK, Response{
		Code:    http.StatusOK,
		Message: "登出成功",
	})
}

// GetMe 获取当前用户信息
func (h *AuthHandler) GetMe(c *gin.Context) {
	// 从上下文获取用户 ID（由中间件注入）
	userID, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusUnauthorized, Response{
			Code:    http.StatusUnauthorized,
			Message: "未授权",
		})
		return
	}

	userInfo, err := h.authService.GetUserInfo(userID.(int64))
	if err != nil {
		c.JSON(http.StatusInternalServerError, Response{
			Code:    http.StatusInternalServerError,
			Message: "获取用户信息失败",
		})
		return
	}

	c.JSON(http.StatusOK, Response{
		Code:    http.StatusOK,
		Message: "success",
		Data: map[string]interface{}{
			"data": userInfo,
		},
	})
}

// RefreshToken 刷新 Token
func (h *AuthHandler) RefreshToken(c *gin.Context) {
	// 获取 Token
	token := c.GetHeader("Authorization")
	if len(token) > 7 && token[:7] == "Bearer " {
		token = token[7:]
	}

	if token == "" {
		c.JSON(http.StatusUnauthorized, Response{
			Code:    http.StatusUnauthorized,
			Message: "Token 不能为空",
		})
		return
	}

	newToken, err := h.authService.RefreshToken(token)
	if err != nil {
		c.JSON(http.StatusUnauthorized, Response{
			Code:    http.StatusUnauthorized,
			Message: "Token 刷新失败",
		})
		return
	}

	c.JSON(http.StatusOK, Response{
		Code:    http.StatusOK,
		Message: "Token 刷新成功",
		Data: map[string]string{
			"token": newToken,
		},
	})
}
