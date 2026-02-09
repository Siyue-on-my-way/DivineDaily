package service

import (
	"divine-daily-backend/internal/database"
	"divine-daily-backend/internal/model"
	"testing"
)

func TestUserProfileService_CreateOrUpdateProfile(t *testing.T) {
	// 初始化数据库（如果未初始化）
	if database.GetDB() == nil {
		if err := database.InitDB(); err != nil {
			t.Skipf("跳过测试：数据库未初始化: %v", err)
			return
		}
	}

	svc := NewUserProfileService()

	// 测试创建用户档案
	req := &model.CreateUserProfileRequest{
		UserID:     "test_user_001",
		Nickname:   "测试用户",
		Gender:     "male",
		BirthDate:  "1987-11-01",
		BirthTime:  "14:30",
		ZodiacSign: "天蝎座",
	}

	profile, err := svc.CreateOrUpdateProfile("test_user_001", req)
	if err != nil {
		t.Fatalf("创建用户档案失败: %v", err)
	}

	// 验证公历信息
	if profile.BirthDate != "1987-11-01" {
		t.Errorf("公历日期错误: 期望 1987-11-01, 实际 %s", profile.BirthDate)
	}

	// 验证农历信息
	if profile.LunarYear != 1987 {
		t.Errorf("农历年错误: 期望 1987, 实际 %d", profile.LunarYear)
	}
	if profile.LunarMonth != 9 {
		t.Errorf("农历月错误: 期望 9, 实际 %d", profile.LunarMonth)
	}
	if profile.LunarDay != 10 {
		t.Errorf("农历日错误: 期望 10, 实际 %d", profile.LunarDay)
	}
	if profile.Animal != "兔" {
		t.Errorf("生肖错误: 期望 '兔', 实际 '%s'", profile.Animal)
	}
	if profile.GanZhiYear != "丁卯" {
		t.Errorf("天干地支年错误: 期望 '丁卯', 实际 '%s'", profile.GanZhiYear)
	}

	// 清理测试数据
	_ = svc // 可以添加清理逻辑
}

func TestUserProfileService_UpdateProfile(t *testing.T) {
	// 初始化数据库（如果未初始化）
	if database.GetDB() == nil {
		if err := database.InitDB(); err != nil {
			t.Skipf("跳过测试：数据库未初始化: %v", err)
			return
		}
	}

	svc := NewUserProfileService()

	// 先创建用户档案
	createReq := &model.CreateUserProfileRequest{
		UserID:    "test_user_002",
		Nickname:  "测试用户2",
		Gender:    "female",
		BirthDate: "1987-11-01",
	}

	_, err := svc.CreateOrUpdateProfile("test_user_002", createReq)
	if err != nil {
		t.Fatalf("创建用户档案失败: %v", err)
	}

	// 测试更新生日（应该触发农历信息重新计算）
	newBirthDate := "2000-01-01"
	updateReq := &model.UpdateUserProfileRequest{
		BirthDate: &newBirthDate,
	}

	profile, err := svc.UpdateProfile("test_user_002", updateReq)
	if err != nil {
		t.Fatalf("更新用户档案失败: %v", err)
	}

	// 验证公历日期已更新
	if profile.BirthDate != "2000-01-01" {
		t.Errorf("公历日期错误: 期望 2000-01-01, 实际 %s", profile.BirthDate)
	}

	// 验证农历信息已重新计算
	if profile.LunarYear != 1999 {
		t.Errorf("农历年错误: 期望 1999, 实际 %d", profile.LunarYear)
	}

	// 测试只更新昵称（不应该触发农历信息重新计算）
	newNickname := "新昵称"
	updateReq2 := &model.UpdateUserProfileRequest{
		Nickname: &newNickname,
	}

	profile2, err := svc.UpdateProfile("test_user_002", updateReq2)
	if err != nil {
		t.Fatalf("更新用户档案失败: %v", err)
	}

	// 验证昵称已更新
	if profile2.Nickname != "新昵称" {
		t.Errorf("昵称错误: 期望 '新昵称', 实际 '%s'", profile2.Nickname)
	}

	// 验证农历信息未变化（应该还是2000-01-01对应的农历）
	if profile2.LunarYear != 1999 {
		t.Errorf("农历年应该未变化: 期望 1999, 实际 %d", profile2.LunarYear)
	}
}

func TestUserProfileService_GetProfile(t *testing.T) {
	// 初始化数据库（如果未初始化）
	if database.GetDB() == nil {
		if err := database.InitDB(); err != nil {
			t.Skipf("跳过测试：数据库未初始化: %v", err)
			return
		}
	}

	svc := NewUserProfileService()

	// 先创建用户档案
	req := &model.CreateUserProfileRequest{
		UserID:    "test_user_003",
		Nickname:  "测试用户3",
		BirthDate: "1987-11-01",
	}

	_, err := svc.CreateOrUpdateProfile("test_user_003", req)
	if err != nil {
		t.Fatalf("创建用户档案失败: %v", err)
	}

	// 测试获取用户档案
	profile, err := svc.GetProfile("test_user_003")
	if err != nil {
		t.Fatalf("获取用户档案失败: %v", err)
	}

	// 验证信息
	if profile.UserID != "test_user_003" {
		t.Errorf("用户ID错误: 期望 'test_user_003', 实际 '%s'", profile.UserID)
	}
	if profile.Nickname != "测试用户3" {
		t.Errorf("昵称错误: 期望 '测试用户3', 实际 '%s'", profile.Nickname)
	}
	if profile.LunarYear == 0 {
		t.Error("农历年应该已设置")
	}
}

