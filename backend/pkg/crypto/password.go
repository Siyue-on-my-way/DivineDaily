package crypto

import (
	"golang.org/x/crypto/bcrypt"
)

// HashPassword 使用 bcrypt 加密密码
func HashPassword(password string) (string, error) {
	bytes, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	if err != nil {
		return "", err
	}
	return string(bytes), nil
}

// CheckPassword 验证密码是否匹配
func CheckPassword(password, hash string) bool {
	err := bcrypt.CompareHashAndPassword([]byte(hash), []byte(password))
	return err == nil
}

// CheckPasswordStrength 检查密码强度
func CheckPasswordStrength(password string) bool {
	// 基本长度检查
	if len(password) < 6 || len(password) > 32 {
		return false
	}

	// 可以添加更多复杂度检查
	// 例如：必须包含数字、字母、特殊字符等

	return true
}
