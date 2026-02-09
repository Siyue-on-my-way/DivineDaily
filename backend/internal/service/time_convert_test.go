package service

import (
	"testing"
)

// 测试公历转农历
func TestSolar2Lunar(t *testing.T) {
	// 测试 1987-11-01
	result, err := Solar2Lunar(1987, 11, 1)
	if err != nil {
		t.Fatalf("Solar2Lunar 失败: %v", err)
	}

	// 验证结果
	if result.LunarYear != 1987 {
		t.Errorf("农历年错误: 期望 1987, 实际 %d", result.LunarYear)
	}
	if result.LunarMonth != 9 {
		t.Errorf("农历月错误: 期望 9, 实际 %d", result.LunarMonth)
	}
	if result.LunarDay != 10 {
		t.Errorf("农历日错误: 期望 10, 实际 %d", result.LunarDay)
	}
	if result.Animal != "兔" {
		t.Errorf("生肖错误: 期望 '兔', 实际 '%s'", result.Animal)
	}
	if result.GanZhiYear != "丁卯" {
		t.Errorf("天干地支年错误: 期望 '丁卯', 实际 '%s'", result.GanZhiYear)
	}
	if result.Astro != "天蝎座" {
		t.Errorf("星座错误: 期望 '天蝎座', 实际 '%s'", result.Astro)
	}
}

// 测试农历转公历
func TestLunar2Solar(t *testing.T) {
	// 测试 1987年9月10日（农历）
	result, err := Lunar2Solar(1987, 9, 10, false)
	if err != nil {
		t.Fatalf("Lunar2Solar 失败: %v", err)
	}

	// 验证结果
	if result.SolarYear != 1987 {
		t.Errorf("公历年错误: 期望 1987, 实际 %d", result.SolarYear)
	}
	if result.SolarMonth != 11 {
		t.Errorf("公历月错误: 期望 11, 实际 %d", result.SolarMonth)
	}
	if result.SolarDay != 1 {
		t.Errorf("公历日错误: 期望 1, 实际 %d", result.SolarDay)
	}
}

// 测试往返转换一致性
func TestRoundTripConversion(t *testing.T) {
	// 公历 → 农历 → 公历
	solarYear, solarMonth, solarDay := 1987, 11, 1

	// 公历转农历
	lunar, err := Solar2Lunar(solarYear, solarMonth, solarDay)
	if err != nil {
		t.Fatalf("Solar2Lunar 失败: %v", err)
	}

	// 农历转公历
	back, err := Lunar2Solar(lunar.LunarYear, lunar.LunarMonth, lunar.LunarDay, lunar.IsLeap)
	if err != nil {
		t.Fatalf("Lunar2Solar 失败: %v", err)
	}

	// 验证一致性
	if back.SolarYear != solarYear || back.SolarMonth != solarMonth || back.SolarDay != solarDay {
		t.Errorf("往返转换不一致: 原始 (%d-%d-%d), 转换后 (%d-%d-%d)",
			solarYear, solarMonth, solarDay,
			back.SolarYear, back.SolarMonth, back.SolarDay)
	}
}

// 测试边界值
func TestBoundaryValues(t *testing.T) {
	// 测试最早日期 1900-01-31
	result, err := Solar2Lunar(1900, 1, 31)
	if err != nil {
		t.Fatalf("1900-01-31 转换失败: %v", err)
	}
	if result.SolarYear != 1900 {
		t.Errorf("1900-01-31 年份错误")
	}

	// 测试最晚日期 3000-12-31
	result, err = Solar2Lunar(3000, 12, 31)
	if err != nil {
		t.Fatalf("3000-12-31 转换失败: %v", err)
	}
	if result.SolarYear != 3000 {
		t.Errorf("3000-12-31 年份错误")
	}

	// 测试无效日期
	_, err = Solar2Lunar(1900, 1, 30)
	if err == nil {
		t.Error("1900-01-30 应该返回错误")
	}
}

