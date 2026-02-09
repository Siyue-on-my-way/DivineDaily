package crypto

import (
	"testing"
)

func TestHashPassword(t *testing.T) {
	password := "testpassword123"
	
	hash, err := HashPassword(password)
	if err != nil {
		t.Fatalf("HashPassword failed: %v", err)
	}
	
	if hash == "" {
		t.Error("Hash should not be empty")
	}
	
	if hash == password {
		t.Error("Hash should not equal plain password")
	}
}

func TestCheckPassword(t *testing.T) {
	password := "testpassword123"
	
	hash, err := HashPassword(password)
	if err != nil {
		t.Fatalf("HashPassword failed: %v", err)
	}
	
	// Test correct password
	if !CheckPassword(password, hash) {
		t.Error("CheckPassword should return true for correct password")
	}
	
	// Test incorrect password
	if CheckPassword("wrongpassword", hash) {
		t.Error("CheckPassword should return false for incorrect password")
	}
}

func TestCheckPasswordStrength(t *testing.T) {
	tests := []struct {
		password string
		expected bool
	}{
		{"12345", false},        // Too short
		{"123456", true},        // Valid
		{"abcdefghijklmnopqrstuvwxyz123456", false}, // Too long
		{"validpass", true},     // Valid
	}
	
	for _, tt := range tests {
		result := CheckPasswordStrength(tt.password)
		if result != tt.expected {
			t.Errorf("CheckPasswordStrength(%s) = %v, want %v", tt.password, result, tt.expected)
		}
	}
}
