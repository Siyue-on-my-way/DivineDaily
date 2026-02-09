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

	response, err := h.configSvc.TestLLMConfig(id)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":  "测试失败",
			"detail": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"message": "测试成功",
		"data":    response,
	})
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
