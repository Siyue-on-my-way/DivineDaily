package service

import (
	"errors"
	"fmt"

	"divine-daily-backend/internal/model"
	"divine-daily-backend/internal/repository"
	"divine-daily-backend/pkg/crypto"
	"divine-daily-backend/pkg/jwt"
	"divine-daily-backend/pkg/validator"
)

var (
	// ErrInvalidCredentials 凭证无效
	ErrInvalidCredentials = errors.New("invalid credentials")
	// ErrUsernameTaken 用户名已被占用
	ErrUsernameTaken = errors.New("username already taken")
	// ErrEmailTaken 邮箱已被注册
	ErrEmailTaken = errors.New("email already registered")
	// ErrPhoneTaken 手机号已被注册
	ErrPhoneTaken = errors.New("phone already registered")
	// ErrInvalidInput 输入无效
	ErrInvalidInput = errors.New("invalid input")
	// ErrAccountDisabled 账号已被禁用
	ErrAccountDisabled = errors.New("account disabled")
)

// AuthService 认证服务接口
type AuthService interface {
	Register(req *model.RegisterRequest) (*model.AuthResponse, error)
	Login(req *model.LoginRequest) (*model.AuthResponse, error)
	GetUserInfo(userID int64) (*model.UserInfo, error)
	RefreshToken(token string) (string, error)
	Logout(userID int64, token string) error
}

// authService 认证服务实现
type authService struct {
	userRepo   repository.UserRepository
	jwtManager *jwt.JWTManager
}

// NewAuthService 创建认证服务
func NewAuthService(userRepo repository.UserRepository, jwtManager *jwt.JWTManager) AuthService {
	return &authService{
		userRepo:   userRepo,
		jwtManager: jwtManager,
	}
}

// Register 用户注册
func (s *authService) Register(req *model.RegisterRequest) (*model.AuthResponse, error) {
	// 1. 验证输入
	valid, errMsg := validator.ValidateRegisterRequest(
		req.Username,
		req.Email,
		req.Phone,
		req.Password,
		req.ConfirmPassword,
	)
	if !valid {
		return nil, fmt.Errorf("%w: %s", ErrInvalidInput, errMsg)
	}

	// 2. 检查用户名是否已存在
	exists, err := s.userRepo.ExistsByUsername(req.Username)
	if err != nil {
		return nil, fmt.Errorf("failed to check username: %w", err)
	}
	if exists {
		return nil, ErrUsernameTaken
	}

	// 3. 检查邮箱是否已注册
	if req.Email != "" {
		exists, err := s.userRepo.ExistsByEmail(req.Email)
		if err != nil {
			return nil, fmt.Errorf("failed to check email: %w", err)
		}
		if exists {
			return nil, ErrEmailTaken
		}
	}

	// 4. 检查手机号是否已注册
	if req.Phone != "" {
		exists, err := s.userRepo.ExistsByPhone(req.Phone)
		if err != nil {
			return nil, fmt.Errorf("failed to check phone: %w", err)
		}
		if exists {
			return nil, ErrPhoneTaken
		}
	}

	// 5. 密码加密
	passwordHash, err := crypto.HashPassword(req.Password)
	if err != nil {
		return nil, fmt.Errorf("failed to hash password: %w", err)
	}

	// 6. 创建用户
	user := &model.AuthUser{
		Username:     req.Username,
		PasswordHash: passwordHash,
		Role:         "normal", // 默认为普通用户
	}

	if req.Email != "" {
		user.Email = &req.Email
	}
	if req.Phone != "" {
		user.Phone = &req.Phone
	}

	if err := s.userRepo.Create(user); err != nil {
		return nil, fmt.Errorf("failed to create user: %w", err)
	}

	// 7. 生成 JWT Token
	token, err := s.jwtManager.GenerateToken(user.ID, user.Username, user.Role)
	if err != nil {
		return nil, fmt.Errorf("failed to generate token: %w", err)
	}

	refreshToken, err := s.jwtManager.GenerateRefreshToken(user.ID, user.Username, user.Role)
	if err != nil {
		return nil, fmt.Errorf("failed to generate refresh token: %w", err)
	}

	// 8. 返回响应
	return &model.AuthResponse{
		Token:        token,
		RefreshToken: refreshToken,
		User:         user.ToUserInfo(),
	}, nil
}

// Login 用户登录
func (s *authService) Login(req *model.LoginRequest) (*model.AuthResponse, error) {
	// 1. 查找用户（支持用户名/邮箱/手机号登录）
	var user *model.AuthUser
	var err error

	// 尝试按用户名查找
	user, err = s.userRepo.FindByUsername(req.Username)
	if err != nil && !errors.Is(err, repository.ErrUserNotFound) {
		return nil, fmt.Errorf("failed to find user: %w", err)
	}

	// 如果用户名未找到，尝试邮箱
	if user == nil && validator.ValidateEmail(req.Username) {
		user, err = s.userRepo.FindByEmail(req.Username)
		if err != nil && !errors.Is(err, repository.ErrUserNotFound) {
			return nil, fmt.Errorf("failed to find user by email: %w", err)
		}
	}

	// 如果邮箱未找到，尝试手机号
	if user == nil && validator.ValidatePhone(req.Username) {
		user, err = s.userRepo.FindByPhone(req.Username)
		if err != nil && !errors.Is(err, repository.ErrUserNotFound) {
			return nil, fmt.Errorf("failed to find user by phone: %w", err)
		}
	}

	// 用户不存在
	if user == nil {
		return nil, ErrInvalidCredentials
	}

	// 2. 验证密码
	if !crypto.CheckPassword(req.Password, user.PasswordHash) {
		return nil, ErrInvalidCredentials
	}

	// 3. 检查用户状态
	if user.Status != 1 {
		return nil, ErrAccountDisabled
	}

	// 4. 更新最后登录时间
	if err := s.userRepo.UpdateLastLogin(user.ID); err != nil {
		// 记录错误但不影响登录
		fmt.Printf("failed to update last login: %v\n", err)
	}

	// 5. 生成 JWT Token
	token, err := s.jwtManager.GenerateToken(user.ID, user.Username, user.Role)
	if err != nil {
		return nil, fmt.Errorf("failed to generate token: %w", err)
	}

	refreshToken, err := s.jwtManager.GenerateRefreshToken(user.ID, user.Username, user.Role)
	if err != nil {
		return nil, fmt.Errorf("failed to generate refresh token: %w", err)
	}

	// 6. 返回响应
	return &model.AuthResponse{
		Token:        token,
		RefreshToken: refreshToken,
		User:         user.ToUserInfo(),
	}, nil
}

// GetUserInfo 获取用户信息
func (s *authService) GetUserInfo(userID int64) (*model.UserInfo, error) {
	user, err := s.userRepo.FindByID(userID)
	if err != nil {
		return nil, err
	}
	return user.ToUserInfo(), nil
}

// RefreshToken 刷新 Token
func (s *authService) RefreshToken(token string) (string, error) {
	return s.jwtManager.RefreshToken(token)
}

// Logout 用户登出
func (s *authService) Logout(userID int64, token string) error {
	// TODO: 实现 Token 黑名单机制
	// 可以将 Token 加入 Redis 黑名单，直到过期
	return nil
}
