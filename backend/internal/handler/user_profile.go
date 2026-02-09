package handler

import (
	"divine-daily-backend/internal/model"
	"divine-daily-backend/internal/service"
	"net/http"

	"github.com/gin-gonic/gin"
)

// UserProfileHandler 用户档案处理器
type UserProfileHandler struct {
	svc *service.UserProfileService
}

// NewUserProfileHandler 创建用户档案处理器
func NewUserProfileHandler(svc *service.UserProfileService) *UserProfileHandler {
	return &UserProfileHandler{svc: svc}
}

// Response 统一响应结构
type ProfileResponse struct {
	Code    int         `json:"code"`
	Message string      `json:"message"`
	Data    interface{} `json:"data,omitempty"`
}

// CreateOrUpdateProfile 创建或更新用户档案
// POST /api/v1/profile
func (h *UserProfileHandler) CreateOrUpdateProfile(c *gin.Context) {
	var req model.CreateUserProfileRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, ProfileResponse{
			Code:    400,
			Message: "参数错误: " + err.Error(),
		})
		return
	}

	profile, err := h.svc.CreateOrUpdateProfile(req.UserID, &req)
	if err != nil {
		c.JSON(http.StatusBadRequest, ProfileResponse{
			Code:    400,
			Message: err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, ProfileResponse{
		Code:    200,
		Message: "success",
		Data:    profile,
	})
}

// UpdateProfile 更新用户档案
// PUT /api/v1/profile/:user_id
func (h *UserProfileHandler) UpdateProfile(c *gin.Context) {
	userID := c.Param("user_id")
	if userID == "" {
		c.JSON(http.StatusBadRequest, ProfileResponse{
			Code:    400,
			Message: "user_id 不能为空",
		})
		return
	}

	var req model.UpdateUserProfileRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, ProfileResponse{
			Code:    400,
			Message: "参数错误: " + err.Error(),
		})
		return
	}

	profile, err := h.svc.UpdateProfile(userID, &req)
	if err != nil {
		c.JSON(http.StatusBadRequest, ProfileResponse{
			Code:    400,
			Message: err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, ProfileResponse{
		Code:    200,
		Message: "success",
		Data:    profile,
	})
}

// GetProfile 获取用户档案
// GET /api/v1/profile/:user_id
func (h *UserProfileHandler) GetProfile(c *gin.Context) {
	userID := c.Param("user_id")
	if userID == "" {
		c.JSON(http.StatusBadRequest, ProfileResponse{
			Code:    400,
			Message: "user_id 不能为空",
		})
		return
	}

	profile, err := h.svc.GetProfile(userID)
	if err != nil {
		if err.Error() == "profile not found" || err.Error() == "sql: no rows in result set" {
			c.JSON(http.StatusNotFound, ProfileResponse{
				Code:    404,
				Message: "用户档案不存在",
			})
			return
		}
		c.JSON(http.StatusInternalServerError, ProfileResponse{
			Code:    500,
			Message: err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, ProfileResponse{
		Code:    200,
		Message: "success",
		Data:    profile,
	})
}

