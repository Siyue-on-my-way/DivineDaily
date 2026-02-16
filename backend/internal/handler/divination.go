package handler

import (
	"log"
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
	log.Println("========== [占卜流程] 开始 ==========")
	log.Printf("[占卜流程] 步骤1: 接收到占卜请求 - 客户端IP: %s", c.ClientIP())
	
	var req model.CreateDivinationRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		log.Printf("[占卜流程] 错误: 请求参数解析失败 - Error: %v", err)
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	log.Printf("[占卜流程] 步骤2: 请求参数解析成功 - 问题: %s, 事件类型: %s, 版本: %s, 用户ID: %s", 
		req.Question, req.EventType, req.Version, req.UserID)

	session, err := h.svc.StartDivination(req)
	if err != nil {
		log.Printf("[占卜流程] 错误: 占卜启动失败 - Error: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to start divination"})
		return
	}

	log.Printf("[占卜流程] 步骤完成: 占卜会话创建成功 - SessionID: %s", session.ID)
	log.Println("========== [占卜流程] Handler层完成 ==========")
	c.JSON(http.StatusCreated, session)
}

func (h *DivinationHandler) GetResult(c *gin.Context) {
	sessionID := c.Param("id")
	log.Printf("[占卜结果] 步骤1: 接收到结果查询请求 - SessionID: %s, 客户端IP: %s", sessionID, c.ClientIP())
	
	if sessionID == "" {
		log.Printf("[占卜结果] 错误: SessionID为空")
		c.JSON(http.StatusBadRequest, gin.H{"error": "Session ID is required"})
		return
	}

	result, err := h.svc.GetResult(sessionID)
	if err != nil {
		log.Printf("[占卜结果] 错误: 结果未找到 - SessionID: %s, Error: %v", sessionID, err)
		c.JSON(http.StatusNotFound, gin.H{"error": "Result not found"})
		return
	}

	log.Printf("[占卜结果] 步骤2: 结果查询成功 - SessionID: %s, 卦象: %s, 结果: %s", sessionID, result.Title, result.Outcome)
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
