package handler

import (
	"divine-daily-backend/internal/service"
	"net/http"

	"github.com/gin-gonic/gin"
)

// TimeConvertHandler 时间转换处理器
type TimeConvertHandler struct {
	svc *service.TimeConvertService
}

// NewTimeConvertHandler 创建时间转换处理器
func NewTimeConvertHandler(svc *service.TimeConvertService) *TimeConvertHandler {
	return &TimeConvertHandler{svc: svc}
}

// Solar2LunarRequest 公历转农历请求
type Solar2LunarRequest struct {
	Year  int `json:"year" binding:"required,min=1900,max=3000"`
	Month int `json:"month" binding:"required,min=1,max=12"`
	Day   int `json:"day" binding:"required,min=1,max=31"`
}

// Lunar2SolarRequest 农历转公历请求
type Lunar2SolarRequest struct {
	Year       int  `json:"year" binding:"required,min=1900,max=3000"`
	Month      int  `json:"month" binding:"required,min=1,max=12"`
	Day        int  `json:"day" binding:"required,min=1,max=30"`
	IsLeapMonth bool `json:"is_leap_month"`
}

// Response 统一响应结构
type Response struct {
	Code    int         `json:"code"`
	Message string      `json:"message"`
	Data    interface{} `json:"data,omitempty"`
}

// Solar2Lunar 公历转农历
// POST /api/v1/time/solar2lunar
func (h *TimeConvertHandler) Solar2Lunar(c *gin.Context) {
	var req Solar2LunarRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, Response{
			Code:    400,
			Message: "参数错误: " + err.Error(),
		})
		return
	}

	result, err := h.svc.Solar2Lunar(req.Year, req.Month, req.Day)
	if err != nil {
		c.JSON(http.StatusBadRequest, Response{
			Code:    400,
			Message: err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, Response{
		Code:    200,
		Message: "success",
		Data:    result,
	})
}

// Lunar2Solar 农历转公历
// POST /api/v1/time/lunar2solar
func (h *TimeConvertHandler) Lunar2Solar(c *gin.Context) {
	var req Lunar2SolarRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, Response{
			Code:    400,
			Message: "参数错误: " + err.Error(),
		})
		return
	}

	result, err := h.svc.Lunar2Solar(req.Year, req.Month, req.Day, req.IsLeapMonth)
	if err != nil {
		c.JSON(http.StatusBadRequest, Response{
			Code:    400,
			Message: err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, Response{
		Code:    200,
		Message: "success",
		Data:    result,
	})
}

