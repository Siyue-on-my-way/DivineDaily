package model

import (
	"time"
)

// AuthUser 认证用户模型（用于登录注册）
type AuthUser struct {
	ID           int64      `json:"id" gorm:"primaryKey;autoIncrement"`
	Username     string     `json:"username" gorm:"uniqueIndex;size:50;not null"`
	Email        *string    `json:"email,omitempty" gorm:"uniqueIndex;size:100"`
	Phone        *string    `json:"phone,omitempty" gorm:"uniqueIndex;size:20"`
	PasswordHash string     `json:"-" gorm:"column:password_hash;size:255;not null"`
	Avatar       *string    `json:"avatar,omitempty" gorm:"size:255"`
	Nickname     *string    `json:"nickname,omitempty" gorm:"size:50"`
	Role         string     `json:"role" gorm:"size:20;default:'normal';index;not null"` // admin, normal
	Status       int8       `json:"status" gorm:"default:1;index"`
	LastLoginAt  *time.Time `json:"last_login_at,omitempty"`
	CreatedAt    time.Time  `json:"created_at" gorm:"autoCreateTime"`
	UpdatedAt    time.Time  `json:"updated_at" gorm:"autoUpdateTime"`
}

// TableName 指定表名
func (AuthUser) TableName() string {
	return "users"
}

// RegisterRequest 注册请求
type RegisterRequest struct {
	Username        string `json:"username" binding:"required,min=3,max=50"`
	Email           string `json:"email" binding:"omitempty,email"`
	Phone           string `json:"phone" binding:"omitempty"`
	Password        string `json:"password" binding:"required,min=6,max=32"`
	ConfirmPassword string `json:"confirm_password" binding:"required,eqfield=Password"`
}

// LoginRequest 登录请求
type LoginRequest struct {
	Username string `json:"username" binding:"required"`
	Password string `json:"password" binding:"required"`
}

// AuthResponse 认证响应
type AuthResponse struct {
	Token        string    `json:"token"`
	RefreshToken string    `json:"refresh_token,omitempty"`
	User         *UserInfo `json:"user"`
}

// UserInfo 用户信息（脱敏）
type UserInfo struct {
	ID       int64   `json:"id"`
	Username string  `json:"username"`
	Email    *string `json:"email,omitempty"`
	Phone    *string `json:"phone,omitempty"`
	Avatar   *string `json:"avatar,omitempty"`
	Nickname *string `json:"nickname,omitempty"`
	Role     string  `json:"role"` // admin, normal
}

// ToUserInfo 转换为用户信息
func (u *AuthUser) ToUserInfo() *UserInfo {
	return &UserInfo{
		ID:       u.ID,
		Username: u.Username,
		Email:    u.Email,
		Phone:    u.Phone,
		Avatar:   u.Avatar,
		Nickname: u.Nickname,
		Role:     u.Role,
	}
}

// IsAdmin 判断是否为管理员
func (u *AuthUser) IsAdmin() bool {
	return u.Role == "admin"
}

// UserSession 用户会话
type UserSession struct {
	ID           int64     `json:"id" gorm:"primaryKey;autoIncrement"`
	UserID       int64     `json:"user_id" gorm:"not null;index"`
	Token        string    `json:"token" gorm:"size:500;not null;index:idx_token,length:255"`
	RefreshToken string    `json:"refresh_token,omitempty" gorm:"size:500"`
	ExpiresAt    time.Time `json:"expires_at" gorm:"not null;index"`
	IPAddress    string    `json:"ip_address,omitempty" gorm:"size:50"`
	UserAgent    string    `json:"user_agent,omitempty" gorm:"size:255"`
	CreatedAt    time.Time `json:"created_at" gorm:"autoCreateTime"`
}

// TableName 指定表名
func (UserSession) TableName() string {
	return "user_sessions"
}
