package handler

import (
	"divine-daily-backend/internal/model"
	"divine-daily-backend/internal/service"
	"net/http"

	"github.com/gin-gonic/gin"
)

type IntelligentPreprocessingHandler struct {
	svc *service.IntelligentPreprocessingService
}

func NewIntelligentPreprocessingHandler(svc *service.IntelligentPreprocessingService) *IntelligentPreprocessingHandler {
	return &IntelligentPreprocessingHandler{svc: svc}
}

func (h *IntelligentPreprocessingHandler) PreprocessQuestion(c *gin.Context) {
	var req model.PreprocessRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	response, err := h.svc.ProcessQuestion(req.UserID, req.RawQuestion, req.Context)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Preprocessing failed"})
		return
	}

	c.JSON(http.StatusOK, response)
}
