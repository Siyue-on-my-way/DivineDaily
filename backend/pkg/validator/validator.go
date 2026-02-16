package validator

import (
	"regexp"
	"strings"
)

var (
	// 中国大陆手机号正则
	phoneRegex = regexp.MustCompile(`^1[3-9]\d{9}$`)
	// 邮箱正则
	emailRegex = regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
	// 用户名正则：3-50个字符，字母、数字、下划线
	usernameRegex = regexp.MustCompile(`^[a-zA-Z0-9_]{3,50}$`)
)

// ValidatePhone 验证手机号格式
func ValidatePhone(phone string) bool {
	if phone == "" {
		return false
	}
	return phoneRegex.MatchString(phone)
}

// ValidateEmail 验证邮箱格式
func ValidateEmail(email string) bool {
	if email == "" {
		return false
	}
	return emailRegex.MatchString(email)
}

// ValidateUsername 验证用户名格式
func ValidateUsername(username string) bool {
	if username == "" {
		return false
	}
	return usernameRegex.MatchString(username)
}

// ValidatePassword 验证密码强度
func ValidatePassword(password string) bool {
	// 长度检查：至少6位
	if len(password) < 6 || len(password) > 32 {
		return false
	}
	
	return true
}

// ValidateRegisterRequest 验证注册请求
func ValidateRegisterRequest(username, email, phone, password, confirmPassword string) (bool, string) {
	// 验证用户名
	if !ValidateUsername(username) {
		return false, "用户名格式不正确，应为3-50个字符，只能包含字母、数字、下划线"
	}

	// 验证邮箱或手机号（至少提供一个）
	hasEmail := email != ""
	hasPhone := phone != ""

	if !hasEmail && !hasPhone {
		return false, "请提供邮箱或手机号"
	}

	if hasEmail && !ValidateEmail(email) {
		return false, "邮箱格式不正确"
	}

	if hasPhone && !ValidatePhone(phone) {
		return false, "手机号格式不正确"
	}

	// 验证密码（至少6位）
	if len(password) < 6 {
		return false, "密码长度至少为6位"
	}

	if len(password) > 32 {
		return false, "密码长度不能超过32位"
	}

	// 验证两次密码是否一致
	if password != confirmPassword {
		return false, "两次输入的密码不一致"
	}

	return true, ""
}

// SanitizeInput 清理输入（防止 XSS）
func SanitizeInput(input string) string {
	// 移除前后空格
	input = strings.TrimSpace(input)
	
	return input
}

// IsValidLoginIdentifier 验证登录标识符（用户名/邮箱/手机号）
func IsValidLoginIdentifier(identifier string) bool {
	if identifier == "" {
		return false
	}
	
	// 可以是用户名、邮箱或手机号
	return ValidateUsername(identifier) || 
	       ValidateEmail(identifier) || 
	       ValidatePhone(identifier)
}
