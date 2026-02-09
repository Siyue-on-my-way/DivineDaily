package handler

import (
	"divine-daily-backend/internal/model"
	"divine-daily-backend/internal/service"
	"net/http"

	"github.com/gin-gonic/gin"
)

type DivinationHandler struct {
	svc *service.DivinationService
}

func NewDivinationHandler(svc *service.DivinationService) *DivinationHandler {
	return &DivinationHandler{svc: svc}
}

func (h *DivinationHandler) StartDivination(c *gin.Context) {
	var req model.CreateDivinationRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	session, err := h.svc.StartDivination(req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to start divination"})
		return
	}

	c.JSON(http.StatusCreated, session)
}

func (h *DivinationHandler) GetResult(c *gin.Context) {
	sessionID := c.Param("id")
	if sessionID == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Session ID is required"})
		return
	}

	result, err := h.svc.GetResult(sessionID)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Result not found"})
		return
	}

	c.JSON(http.StatusOK, result)
}

func (h *DivinationHandler) SubmitFollowUp(c *gin.Context) {
	var req model.FollowUpAnswer
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	err := h.svc.SubmitAnswer(req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to submit answer"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"status": "success"})
}

func (h *DivinationHandler) RecommendOrientation(c *gin.Context) {
	var req model.OrientationRecommendRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	resp, err := h.svc.RecommendOrientation(req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to recommend orientation"})
		return
	}

	c.JSON(http.StatusOK, resp)
}
