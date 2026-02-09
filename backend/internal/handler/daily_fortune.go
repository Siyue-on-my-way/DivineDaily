package handler

import (
	"divine-daily-backend/internal/model"
	"divine-daily-backend/internal/service"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
)

type DailyFortuneHandler struct {
	dailyFortuneSvc *service.DailyFortuneService
}

func NewDailyFortuneHandler(dailyFortuneSvc *service.DailyFortuneService) *DailyFortuneHandler {
	return &DailyFortuneHandler{
		dailyFortuneSvc: dailyFortuneSvc,
	}
}

// GenerateDailyFortune 生成每日运势
func (h *DailyFortuneHandler) GenerateDailyFortune(c *gin.Context) {
	var req model.DailyFortuneRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Parse date or use today
	targetDate := time.Now()
	if req.Date != "" {
		parsedDate, err := time.Parse("2006-01-02", req.Date)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid date format. Use YYYY-MM-DD"})
			return
		}
		targetDate = parsedDate
	}

	fortune, err := h.dailyFortuneSvc.GenerateDailyFortune(req.UserID, targetDate)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, fortune)
}
