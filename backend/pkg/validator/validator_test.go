package validator

import (
	"testing"
)

func TestValidatePhone(t *testing.T) {
	tests := []struct {
		phone    string
		expected bool
	}{
		{"13800138000", true},
		{"15912345678", true},
		{"12345678901", false}, // Invalid prefix
		{"1380013800", false},  // Too short
		{"138001380000", false}, // Too long
		{"", false},
		{"abcdefghijk", false},
	}
	
	for _, tt := range tests {
		result := ValidatePhone(tt.phone)
		if result != tt.expected {
			t.Errorf("ValidatePhone(%s) = %v, want %v", tt.phone, result, tt.expected)
		}
	}
}

func TestValidateEmail(t *testing.T) {
	tests := []struct {
		email    string
		expected bool
	}{
		{"test@example.com", true},
		{"user.name@domain.co.uk", true},
		{"invalid.email", false},
		{"@example.com", false},
		{"test@", false},
		{"", false},
	}
	
	for _, tt := range tests {
		result := ValidateEmail(tt.email)
		if result != tt.expected {
			t.Errorf("ValidateEmail(%s) = %v, want %v", tt.email, result, tt.expected)
		}
	}
}

func TestValidateUsername(t *testing.T) {
	tests := []struct {
		username string
		expected bool
	}{
		{"user123", true},
		{"test_user", true},
		{"ab", false},          // Too short
		{"a" + string(make([]byte, 50)), false}, // Too long
		{"user-name", false},   // Invalid character
		{"user name", false},   // Space not allowed
		{"", false},
	}
	
	for _, tt := range tests {
		result := ValidateUsername(tt.username)
		if result != tt.expected {
			t.Errorf("ValidateUsername(%s) = %v, want %v", tt.username, result, tt.expected)
		}
	}
}

func TestValidatePassword(t *testing.T) {
	tests := []struct {
		password string
		expected bool
	}{
		{"123456", true},
		{"12345", false},       // Too short
		{"a" + string(make([]byte, 33)), false}, // Too long
		{"validpass", true},
		{"", false},
	}
	
	for _, tt := range tests {
		result := ValidatePassword(tt.password)
		if result != tt.expected {
			t.Errorf("ValidatePassword(%s) = %v, want %v", tt.password, result, tt.expected)
		}
	}
}

func TestValidateRegisterRequest(t *testing.T) {
	tests := []struct {
		username        string
		email           string
		phone           string
		password        string
		confirmPassword string
		expectedValid   bool
		expectedMsg     string
	}{
		{
			"testuser", "test@example.com", "", "password123", "password123",
			true, "",
		},
		{
			"testuser", "", "13800138000", "password123", "password123",
			true, "",
		},
		{
			"ab", "test@example.com", "", "password123", "password123",
			false, "用户名格式不正确",
		},
		{
			"testuser", "invalid-email", "", "password123", "password123",
			false, "邮箱格式不正确",
		},
		{
			"testuser", "", "12345", "password123", "password123",
			false, "手机号格式不正确",
		},
		{
			"testuser", "test@example.com", "", "12345", "12345",
			false, "密码长度应为6-32个字符",
		},
		{
			"testuser", "test@example.com", "", "password123", "password456",
			false, "两次输入的密码不一致",
		},
		{
			"testuser", "", "", "password123", "password123",
			false, "请提供邮箱或手机号",
		},
	}
	
	for _, tt := range tests {
		valid, msg := ValidateRegisterRequest(
			tt.username, tt.email, tt.phone, tt.password, tt.confirmPassword,
		)
		if valid != tt.expectedValid {
			t.Errorf("ValidateRegisterRequest() valid = %v, want %v", valid, tt.expectedValid)
		}
		if !valid && msg != tt.expectedMsg {
			t.Errorf("ValidateRegisterRequest() msg = %s, want %s", msg, tt.expectedMsg)
		}
	}
}
