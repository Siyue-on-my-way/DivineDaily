package service

import (
	"testing"
)

// 测试常量数据的基本正确性
func TestConstantsData(t *testing.T) {
	// 测试 lunarInfo 数组长度
	expectedLunarInfoLen := 1101 // 1900-3000 共1101年
	if len(lunarInfo) != expectedLunarInfoLen {
		t.Errorf("lunarInfo 长度错误: 期望 %d, 实际 %d", expectedLunarInfoLen, len(lunarInfo))
	}

	// 测试 solarMonth 数组长度
	expectedSolarMonthLen := 12
	if len(solarMonth) != expectedSolarMonthLen {
		t.Errorf("solarMonth 长度错误: 期望 %d, 实际 %d", expectedSolarMonthLen, len(solarMonth))
	}

	// 测试天干数组长度
	expectedGanLen := 10
	if len(gan) != expectedGanLen {
		t.Errorf("gan 长度错误: 期望 %d, 实际 %d", expectedGanLen, len(gan))
	}

	// 测试地支数组长度
	expectedZhiLen := 12
	if len(zhi) != expectedZhiLen {
		t.Errorf("zhi 长度错误: 期望 %d, 实际 %d", expectedZhiLen, len(zhi))
	}

	// 测试生肖数组长度
	expectedZodiacLen := 12
	if len(chineseZodiac) != expectedZodiacLen {
		t.Errorf("chineseZodiac 长度错误: 期望 %d, 实际 %d", expectedZodiacLen, len(chineseZodiac))
	}

	// 测试节气数组长度
	expectedSolarTermLen := 24
	if len(solarTerm) != expectedSolarTermLen {
		t.Errorf("solarTerm 长度错误: 期望 %d, 实际 %d", expectedSolarTermLen, len(solarTerm))
	}
}

// 测试关键数据点的值
func TestKeyDataPoints(t *testing.T) {
	// 测试 1900 年的农历数据（第一个元素）
	// 1900年的数据应该是 0x04bd8
	expected1900 := uint32(0x04bd8)
	if lunarInfo[0] != expected1900 {
		t.Errorf("1900年农历数据错误: 期望 0x%x, 实际 0x%x", expected1900, lunarInfo[0])
	}

	// 测试 1987 年的农历数据（第87个元素，索引87，因为1900年是索引0）
	// 1987年的数据应该是 0xaf46（从1980-1989行看，1987是第8个，即0x0af46）
	expected1987 := uint32(0xaf46)
	if lunarInfo[87] != expected1987 {
		t.Errorf("1987年农历数据错误: 期望 0x%x, 实际 0x%x", expected1987, lunarInfo[87])
	}

	// 测试 3000 年的农历数据（最后一个元素）
	// 3000年的数据应该是 0x150d6
	expected3000 := uint32(0x150d6)
	if lunarInfo[len(lunarInfo)-1] != expected3000 {
		t.Errorf("3000年农历数据错误: 期望 0x%x, 实际 0x%x", expected3000, lunarInfo[len(lunarInfo)-1])
	}

	// 测试天干第一个和最后一个
	if gan[0] != "甲" {
		t.Errorf("gan[0] 错误: 期望 '甲', 实际 '%s'", gan[0])
	}
	if gan[9] != "癸" {
		t.Errorf("gan[9] 错误: 期望 '癸', 实际 '%s'", gan[9])
	}

	// 测试地支第一个和最后一个
	if zhi[0] != "子" {
		t.Errorf("zhi[0] 错误: 期望 '子', 实际 '%s'", zhi[0])
	}
	if zhi[11] != "亥" {
		t.Errorf("zhi[11] 错误: 期望 '亥', 实际 '%s'", zhi[11])
	}

	// 测试生肖第一个和最后一个
	if chineseZodiac[0] != "鼠" {
		t.Errorf("chineseZodiac[0] 错误: 期望 '鼠', 实际 '%s'", chineseZodiac[0])
	}
	if chineseZodiac[11] != "猪" {
		t.Errorf("chineseZodiac[11] 错误: 期望 '猪', 实际 '%s'", chineseZodiac[11])
	}

	// 测试节气第一个和最后一个
	if solarTerm[0] != "小寒" {
		t.Errorf("solarTerm[0] 错误: 期望 '小寒', 实际 '%s'", solarTerm[0])
	}
	if solarTerm[23] != "冬至" {
		t.Errorf("solarTerm[23] 错误: 期望 '冬至', 实际 '%s'", solarTerm[23])
	}
}

// 测试农历信息解析
func TestLunarInfoParsing(t *testing.T) {
	// 测试 1987 年的闰月信息
	// 1987年的数据是 0xaf46
	// 低4位是闰月：0xaf46 & 0xf = 0x6 = 6，表示闰6月
	// 第17位是闰月大小：0xaf46 & 0x10000 = 0，表示小月（29天）
	year1987 := lunarInfo[87]
	leapMonth := int(year1987 & 0xf)
	leapDays := 0
	if year1987&0x10000 != 0 {
		leapDays = 30
	} else {
		leapDays = 29
	}

	if leapMonth != 6 {
		t.Errorf("1987年闰月错误: 期望 6, 实际 %d", leapMonth)
	}
	if leapDays != 29 {
		t.Errorf("1987年闰月天数错误: 期望 29, 实际 %d", leapDays)
	}

	// 测试 1900 年的闰月信息
	// 1900年的数据是 0x04bd8
	// 低4位是闰月：0x04bd8 & 0xf = 0x8 = 8，表示闰8月
	year1900 := lunarInfo[0]
	leapMonth1900 := int(year1900 & 0xf)
	if leapMonth1900 != 8 {
		t.Errorf("1900年闰月错误: 期望 8, 实际 %d", leapMonth1900)
	}
}

// 测试 solarMonth 数据
func TestSolarMonth(t *testing.T) {
	expected := []int{31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31}
	for i, v := range expected {
		if solarMonth[i] != v {
			t.Errorf("solarMonth[%d] 错误: 期望 %d, 实际 %d", i, v, solarMonth[i])
		}
	}
}

// 测试节日数据
func TestFestivalData(t *testing.T) {
	// 测试公历节日
	if festival["1-1"] != "元旦节" {
		t.Errorf("festival['1-1'] 错误: 期望 '元旦节', 实际 '%s'", festival["1-1"])
	}
	if festival["10-1"] != "国庆节" {
		t.Errorf("festival['10-1'] 错误: 期望 '国庆节', 实际 '%s'", festival["10-1"])
	}

	// 测试农历节日
	if lFestival["1-1"] != "春节" {
		t.Errorf("lFestival['1-1'] 错误: 期望 '春节', 实际 '%s'", lFestival["1-1"])
	}
	if lFestival["8-15"] != "中秋节" {
		t.Errorf("lFestival['8-15'] 错误: 期望 '中秋节', 实际 '%s'", lFestival["8-15"])
	}
}

// 测试 sTermInfo 数据
func TestSTermInfo(t *testing.T) {
	// sTermInfo 应该有 1101 个元素（对应1900-3000年）
	expectedLen := 1101
	if len(sTermInfo) != expectedLen {
		t.Errorf("sTermInfo 长度错误: 期望 %d, 实际 %d", expectedLen, len(sTermInfo))
	}

	// 测试第一个和最后一个元素不为空
	if len(sTermInfo[0]) == 0 {
		t.Error("sTermInfo[0] 为空")
	}
	if len(sTermInfo[len(sTermInfo)-1]) == 0 {
		t.Error("sTermInfo 最后一个元素为空")
	}
}
