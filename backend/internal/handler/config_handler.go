package handler

import (
	"divine-daily-backend/internal/model"
	"divine-daily-backend/internal/service"
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
)

// ConfigHandler 配置管理Handler
type ConfigHandler struct {
	configSvc *service.ConfigService
}

// NewConfigHandler 创建配置Handler
func NewConfigHandler(configSvc *service.ConfigService) *ConfigHandler {
	return &ConfigHandler{
		configSvc: configSvc,
	}
}

// ========== LLM配置API ==========

// ListLLMConfigs 获取所有LLM配置
// GET /api/v1/configs/llm
func (h *ConfigHandler) ListLLMConfigs(c *gin.Context) {
	configs, err := h.configSvc.ListLLMConfigs()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":  "获取配置列表失败",
			"detail": err.Error(),
		})
		return
	}

	// 转换为响应格式（脱敏）
	responses := make([]*model.LLMConfigResponse, len(configs))
	for i, config := range configs {
		responses[i] = h.configSvc.ToLLMConfigResponse(config)
	}

	c.JSON(http.StatusOK, gin.H{
		"data": responses,
	})
}

// GetLLMConfig 获取单个LLM配置
// GET /api/v1/configs/llm/:id
func (h *ConfigHandler) GetLLMConfig(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "无效的配置ID",
		})
		return
	}

	config, err := h.configSvc.GetLLMConfigByID(id)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{
			"error":  "配置不存在",
			"detail": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"data": h.configSvc.ToLLMConfigResponse(config),
	})
}

// CreateLLMConfig 创建LLM配置
// POST /api/v1/configs/llm
func (h *ConfigHandler) CreateLLMConfig(c *gin.Context) {
	var req model.LLMConfigCreateRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error":  "请求参数错误",
			"detail": err.Error(),
		})
		return
	}

	config, err := h.configSvc.CreateLLMConfig(&req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":  "创建配置失败",
			"detail": err.Error(),
		})
		return
	}

	c.JSON(http.StatusCreated, gin.H{
		"data": h.configSvc.ToLLMConfigResponse(config),
	})
}

// UpdateLLMConfig 更新LLM配置
// PUT /api/v1/configs/llm/:id
func (h *ConfigHandler) UpdateLLMConfig(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "无效的配置ID",
		})
		return
	}

	var req model.LLMConfigUpdateRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error":  "请求参数错误",
			"detail": err.Error(),
		})
		return
	}

	config, err := h.configSvc.UpdateLLMConfig(id, &req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":  "更新配置失败",
			"detail": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"data": h.configSvc.ToLLMConfigResponse(config),
	})
}

// DeleteLLMConfig 删除LLM配置
// DELETE /api/v1/configs/llm/:id
func (h *ConfigHandler) DeleteLLMConfig(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "无效的配置ID",
		})
		return
	}

	if err := h.configSvc.DeleteLLMConfig(id); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":  "删除配置失败",
			"detail": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"message": "删除成功",
	})
}

// SetDefaultLLMConfig 设置默认LLM配置
// POST /api/v1/configs/llm/:id/set-default
func (h *ConfigHandler) SetDefaultLLMConfig(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "无效的配置ID",
		})
		return
	}

	if err := h.configSvc.SetDefaultLLMConfig(id); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":  "设置默认配置失败",
			"detail": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"message": "设置成功",
	})
}

// TestLLMConfig 测试LLM配置
// POST /api/v1/configs/llm/:id/test
func (h *ConfigHandler) TestLLMConfig(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "无效的配置ID",
		})
		return
	}

	// 获取测试模式：stream（流式）或 block（阻塞式）
	var req struct {
		Mode string `json:"mode"` // "stream" or "block"
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		req.Mode = "block" // 默认阻塞式
	}

	if req.Mode == "stream" {
		// 流式输出测试
		h.testLLMConfigStream(c, id)
	} else {
		// 阻塞式输出测试
		h.testLLMConfigBlock(c, id)
	}
}

// testLLMConfigBlock 阻塞式测试
func (h *ConfigHandler) testLLMConfigBlock(c *gin.Context, id int) {
	response, tokenCount, duration, err := h.configSvc.TestLLMConfigBlock(id)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":  "测试失败",
			"detail": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"message": "测试成功",
		"data": gin.H{
			"response":    response,
			"token_count": tokenCount,
			"duration_ms": duration,
			"mode":        "block",
		},
	})
}

// testLLMConfigStream 流式测试
func (h *ConfigHandler) testLLMConfigStream(c *gin.Context, id int) {
	// 设置SSE响应头
	c.Header("Content-Type", "text/event-stream")
	c.Header("Cache-Control", "no-cache")
	c.Header("Connection", "keep-alive")
	c.Header("X-Accel-Buffering", "no")

	// 创建流式通道
	streamChan := make(chan string, 100)
	errChan := make(chan error, 1)

	// 启动流式测试
	go func() {
		err := h.configSvc.TestLLMConfigStream(id, streamChan)
		if err != nil {
			errChan <- err
		}
		close(streamChan)
		close(errChan)
	}()

	// 发送流式数据
	flusher, ok := c.Writer.(http.Flusher)
	if !ok {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "不支持流式输出",
		})
		return
	}

	tokenCount := 0
	for {
		select {
		case chunk, ok := <-streamChan:
			if !ok {
				// 流结束
				c.SSEvent("done", gin.H{
					"token_count": tokenCount,
					"mode":        "stream",
				})
				flusher.Flush()
				return
			}
			// 发送数据块
			c.SSEvent("message", chunk)
			flusher.Flush()
			tokenCount++
		case err := <-errChan:
			if err != nil {
				c.SSEvent("error", gin.H{
					"error": err.Error(),
				})
				flusher.Flush()
				return
			}
		}
	}
}

// ========== Prompt配置API ==========

// ListPromptConfigs 获取所有Prompt配置
// GET /api/v1/configs/prompt
func (h *ConfigHandler) ListPromptConfigs(c *gin.Context) {
	configs, err := h.configSvc.ListPromptConfigs()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":  "获取配置列表失败",
			"detail": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"data": configs,
	})
}

// GetPromptConfig 获取单个Prompt配置
// GET /api/v1/configs/prompt/:id
func (h *ConfigHandler) GetPromptConfig(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "无效的配置ID",
		})
		return
	}

	config, err := h.configSvc.GetPromptConfigByID(id)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{
			"error":  "配置不存在",
			"detail": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"data": config,
	})
}

// CreatePromptConfig 创建Prompt配置
// POST /api/v1/configs/prompt
func (h *ConfigHandler) CreatePromptConfig(c *gin.Context) {
	var req model.PromptConfigCreateRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error":  "请求参数错误",
			"detail": err.Error(),
		})
		return
	}

	config, err := h.configSvc.CreatePromptConfig(&req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":  "创建配置失败",
			"detail": err.Error(),
		})
		return
	}

	c.JSON(http.StatusCreated, gin.H{
		"data": config,
	})
}

// UpdatePromptConfig 更新Prompt配置
// PUT /api/v1/configs/prompt/:id
func (h *ConfigHandler) UpdatePromptConfig(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "无效的配置ID",
		})
		return
	}

	var req model.PromptConfigUpdateRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error":  "请求参数错误",
			"detail": err.Error(),
		})
		return
	}

	config, err := h.configSvc.UpdatePromptConfig(id, &req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":  "更新配置失败",
			"detail": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"data": config,
	})
}

// DeletePromptConfig 删除Prompt配置
// DELETE /api/v1/configs/prompt/:id
func (h *ConfigHandler) DeletePromptConfig(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "无效的配置ID",
		})
		return
	}

	if err := h.configSvc.DeletePromptConfig(id); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":  "删除配置失败",
			"detail": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"message": "删除成功",
	})
}

// SetDefaultPromptConfig 设置默认Prompt配置
// POST /api/v1/configs/prompt/:id/set-default
func (h *ConfigHandler) SetDefaultPromptConfig(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "无效的配置ID",
		})
		return
	}

	if err := h.configSvc.SetDefaultPromptConfig(id); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":  "设置默认配置失败",
			"detail": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"message": "设置成功",
	})
}

// RenderPrompt 预览Prompt渲染结果
// POST /api/v1/configs/prompt/render
func (h *ConfigHandler) RenderPrompt(c *gin.Context) {
	var req model.PromptRenderRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error":  "请求参数错误",
			"detail": err.Error(),
		})
		return
	}

	rendered, err := h.configSvc.RenderPrompt(req.Template, req.Variables)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":  "渲染失败",
			"detail": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"data": model.PromptRenderResponse{
			Rendered: rendered,
		},
	})
}
