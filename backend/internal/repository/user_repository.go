package repository

import (
	"errors"
	"time"

	"gorm.io/gorm"
	"divine-daily-backend/internal/model"
)

var (
	// ErrUserNotFound 用户不存在
	ErrUserNotFound = errors.New("user not found")
	// ErrUserExists 用户已存在
	ErrUserExists = errors.New("user already exists")
)

// UserRepository 用户仓储接口
type UserRepository interface {
	Create(user *model.AuthUser) error
	FindByID(id int64) (*model.AuthUser, error)
	FindByUsername(username string) (*model.AuthUser, error)
	FindByEmail(email string) (*model.AuthUser, error)
	FindByPhone(phone string) (*model.AuthUser, error)
	Update(user *model.AuthUser) error
	UpdateLastLogin(userID int64) error
	ExistsByUsername(username string) (bool, error)
	ExistsByEmail(email string) (bool, error)
	ExistsByPhone(phone string) (bool, error)
}

// userRepository 用户仓储实现
type userRepository struct {
	db *gorm.DB
}

// NewUserRepository 创建用户仓储
func NewUserRepository(db *gorm.DB) UserRepository {
	return &userRepository{db: db}
}

// Create 创建用户
func (r *userRepository) Create(user *model.AuthUser) error {
	if err := r.db.Create(user).Error; err != nil {
		return err
	}
	return nil
}

// FindByID 根据 ID 查找用户
func (r *userRepository) FindByID(id int64) (*model.AuthUser, error) {
	var user model.AuthUser
	if err := r.db.Where("id = ?", id).First(&user).Error; err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, ErrUserNotFound
		}
		return nil, err
	}
	return &user, nil
}

// FindByUsername 根据用户名查找用户
func (r *userRepository) FindByUsername(username string) (*model.AuthUser, error) {
	var user model.AuthUser
	if err := r.db.Where("username = ?", username).First(&user).Error; err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, ErrUserNotFound
		}
		return nil, err
	}
	return &user, nil
}

// FindByEmail 根据邮箱查找用户
func (r *userRepository) FindByEmail(email string) (*model.AuthUser, error) {
	var user model.AuthUser
	if err := r.db.Where("email = ?", email).First(&user).Error; err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, ErrUserNotFound
		}
		return nil, err
	}
	return &user, nil
}

// FindByPhone 根据手机号查找用户
func (r *userRepository) FindByPhone(phone string) (*model.AuthUser, error) {
	var user model.AuthUser
	if err := r.db.Where("phone = ?", phone).First(&user).Error; err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, ErrUserNotFound
		}
		return nil, err
	}
	return &user, nil
}

// Update 更新用户信息
func (r *userRepository) Update(user *model.AuthUser) error {
	return r.db.Save(user).Error
}

// UpdateLastLogin 更新最后登录时间
func (r *userRepository) UpdateLastLogin(userID int64) error {
	now := time.Now()
	return r.db.Model(&model.AuthUser{}).
		Where("id = ?", userID).
		Update("last_login_at", now).Error
}

// ExistsByUsername 检查用户名是否存在
func (r *userRepository) ExistsByUsername(username string) (bool, error) {
	var count int64
	if err := r.db.Model(&model.AuthUser{}).
		Where("username = ?", username).
		Count(&count).Error; err != nil {
		return false, err
	}
	return count > 0, nil
}

// ExistsByEmail 检查邮箱是否存在
func (r *userRepository) ExistsByEmail(email string) (bool, error) {
	if email == "" {
		return false, nil
	}
	var count int64
	if err := r.db.Model(&model.AuthUser{}).
		Where("email = ?", email).
		Count(&count).Error; err != nil {
		return false, err
	}
	return count > 0, nil
}

// ExistsByPhone 检查手机号是否存在
func (r *userRepository) ExistsByPhone(phone string) (bool, error) {
	if phone == "" {
		return false, nil
	}
	var count int64
	if err := r.db.Model(&model.AuthUser{}).
		Where("phone = ?", phone).
		Count(&count).Error; err != nil {
		return false, err
	}
	return count > 0, nil
}
