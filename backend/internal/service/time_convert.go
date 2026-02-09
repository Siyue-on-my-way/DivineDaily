package service

import (
	"errors"
	"fmt"
	"strconv"
	"time"
)

// ConversionResult 转换结果结构
type ConversionResult struct {
	// 公历信息
	SolarYear  int    `json:"solar_year"`
	SolarMonth int    `json:"solar_month"`
	SolarDay   int    `json:"solar_day"`

	// 农历信息
	LunarYear  int    `json:"lunar_year"`
	LunarMonth int    `json:"lunar_month"`
	LunarDay   int    `json:"lunar_day"`
	IsLeap     bool   `json:"is_leap"`
	LunarMonthCn string `json:"lunar_month_cn"` // 农历月份中文（如"九月"、"闰九月"）
	LunarDayCn   string `json:"lunar_day_cn"`   // 农历日期中文（如"初十"、"廿一"）

	// 天干地支
	GanZhiYear  string `json:"ganzhi_year"`
	GanZhiMonth string `json:"ganzhi_month"`
	GanZhiDay   string `json:"ganzhi_day"`

	// 其他信息
	Animal        string `json:"animal"`         // 生肖
	Weekday       int    `json:"weekday"`        // 星期几（1-7，1为周一）
	WeekdayCn     string `json:"weekday_cn"`     // 星期中文（如"星期一"）
	Astro         string `json:"astro"`           // 星座
	Term          string `json:"term"`           // 节气（如果有）
	IsTerm        bool   `json:"is_term"`        // 是否是节气
	Festival      string `json:"festival"`       // 公历节日
	LunarFestival string `json:"lunar_festival"` // 农历节日
	IsToday       bool   `json:"is_today"`       // 是否是今天
}

// lYearDays 返回农历y年一整年的总天数
func lYearDays(y int) int {
	sum := 348
	for i := uint32(0x8000); i > 0x8; i >>= 1 {
		if lunarInfo[y-1900]&i != 0 {
			sum++
		}
	}
	return sum + leapDays(y)
}

// leapMonth 返回农历y年闰月是哪个月；若y年没有闰月则返回0
func leapMonth(y int) int {
	return int(lunarInfo[y-1900] & 0xf)
}

// leapDays 返回农历y年闰月的天数 若该年没有闰月则返回0
func leapDays(y int) int {
	if leapMonth(y) != 0 {
		if lunarInfo[y-1900]&0x10000 != 0 {
			return 30
		}
		return 29
	}
	return 0
}

// monthDays 返回农历y年m月（非闰月）的总天数，计算m为闰月时的天数请使用leapDays方法
func monthDays(y, m int) int {
	if m > 12 || m < 1 {
		return -1
	}
	if lunarInfo[y-1900]&(0x10000>>uint(m)) != 0 {
		return 30
	}
	return 29
}

// solarDays 返回公历y年m月的天数
func solarDays(y, m int) int {
	if m > 12 || m < 1 {
		return -1
	}
	ms := m - 1
	if ms == 1 { // 2月份
		if (y%4 == 0 && y%100 != 0) || (y%400 == 0) {
			return 29
		}
		return 28
	}
	return solarMonth[ms]
}

// toGanZhiYear 农历年份转换为干支纪年
func toGanZhiYear(lYear int) string {
	ganKey := (lYear - 3) % 10
	zhiKey := (lYear - 3) % 12
	if ganKey == 0 {
		ganKey = 10
	}
	if zhiKey == 0 {
		zhiKey = 12
	}
	return gan[ganKey-1] + zhi[zhiKey-1]
}

// toGanZhi 传入offset偏移量返回干支
func toGanZhi(offset int) string {
	return gan[offset%10] + zhi[offset%12]
}

// getTerm 传入公历年获得该年第n个节气的公历日期
// JavaScript 版本逻辑：将16进制字符串转换为整数，然后按位解析
func getTerm(y, n int) int {
	if y < 1900 || y > 3000 || n < 1 || n > 24 {
		return -1
	}
	table := sTermInfo[y-1900]
	if len(table) < 30 { // 至少需要6个节气数据（6*5=30字符）
		return -1
	}

	// 解析节气数据：每个节气用5个字符表示（16进制字符串）
	calcDay := make([]int, 0, 24)
	for i := 0; i < len(table); i += 5 {
		if i+5 > len(table) {
			break
		}
		chunk := table[i : i+5]
		// 将16进制字符串转换为整数（JavaScript: parseInt('0x' + chunk)）
		var val int64
		if _, err := fmt.Sscanf(chunk, "%x", &val); err != nil {
			continue
		}
		// 转换为字符串（JavaScript: val.toString()）
		valStr := fmt.Sprintf("%d", val)
		
		// JavaScript 版本解析逻辑：
		// calcDay.push(chunk[0], chunk.slice(1, 3), chunk[3], chunk.slice(4, 6))
		if len(valStr) >= 1 {
			calcDay = append(calcDay, int(valStr[0]-'0'))
		}
		if len(valStr) >= 3 {
			if day, err := strconv.Atoi(valStr[1:3]); err == nil {
				calcDay = append(calcDay, day)
			}
		}
		if len(valStr) >= 4 {
			calcDay = append(calcDay, int(valStr[3]-'0'))
		}
		if len(valStr) >= 6 {
			if day, err := strconv.Atoi(valStr[4:6]); err == nil {
				calcDay = append(calcDay, day)
			}
		}
	}

	if n-1 < len(calcDay) {
		return calcDay[n-1]
	}
	return -1
}

// toChinaMonth 传入农历数字月份返回汉语表示
func toChinaMonth(m int) string {
	if m > 12 || m < 1 {
		return ""
	}
	return nStr3[m-1] + "月"
}

// toChinaDay 传入农历日期数字返回汉字表示
func toChinaDay(d int) string {
	switch d {
	case 10:
		return "初十"
	case 20:
		return "二十"
	case 30:
		return "三十"
	default:
		// 确保索引在有效范围内
		dayTens := d / 10
		dayOnes := d % 10
		if dayTens >= len(nStr2) {
			dayTens = len(nStr2) - 1
		}
		if dayOnes >= len(nStr1) {
			dayOnes = len(nStr1) - 1
		}
		return nStr2[dayTens] + nStr1[dayOnes]
	}
}

// getAnimal 年份转生肖
func getAnimal(y int) string {
	return chineseZodiac[(y-4)%12]
}

// toAstro 公历月、日判断所属星座
func toAstro(month, day int) string {
	// 星座字符串（Unicode转义：\u6469\u7faf\u6c34\u74f6...）
	// 每个星座2个字符，共12个星座，最后重复摩羯
	astroStr := "摩羯水瓶双鱼白羊金牛双子巨蟹狮子处女天秤天蝎射手摩羯"
	arr := []int{20, 19, 21, 21, 21, 22, 23, 23, 23, 23, 22, 22}
	
	// JavaScript: const start = cMonth * 2 - (cDay < arr[cMonth - 1] ? 2 : 0);
	start := month * 2
	if day < arr[month-1] {
		start -= 2
	}
	
	// 转换为rune数组以便正确处理中文字符
	runes := []rune(astroStr)
	
	// start是字符位置（每个星座2个字符），需要转换为rune索引
	// 因为中文字符每个占3个字节，但作为rune只占1个位置
	runeStart := start
	if runeStart < 0 {
		runeStart = 0
	}
	if runeStart >= len(runes) {
		runeStart = len(runes) - 2
	}
	if runeStart+2 > len(runes) {
		runeStart = len(runes) - 2
	}
	
	return string(runes[runeStart:runeStart+2]) + "座"
}

// Solar2Lunar 公历转农历
func Solar2Lunar(year, month, day int) (*ConversionResult, error) {
	// 参数验证
	if year < 1900 || year > 3000 {
		return nil, errors.New("年份超出支持范围（1900-3000）")
	}
	if year == 1900 && month == 1 && day < 31 {
		return nil, errors.New("日期超出支持范围（最早1900年1月31日）")
	}

	// 创建日期对象
	objDate := time.Date(year, time.Month(month), day, 0, 0, 0, 0, time.UTC)
	
	// 修正年月日
	y := objDate.Year()
	m := int(objDate.Month())
	d := objDate.Day()

	// 计算与1900年1月31日的天数差
	baseDate := time.Date(1900, 1, 31, 0, 0, 0, 0, time.UTC)
	offset := int(objDate.Sub(baseDate).Hours() / 24)

	// 计算农历年
	var i int
	var temp int
	for i = 1900; i < 2101 && offset > 0; i++ {
		temp = lYearDays(i)
		offset -= temp
	}
	if offset < 0 {
		offset += temp
		i--
	}

	// 判断是否是今天
	now := time.Now()
	isToday := now.Year() == y && int(now.Month()) == m && now.Day() == d

	// 计算星期
	weekday := int(objDate.Weekday())
	if weekday == 0 {
		weekday = 7 // 周日改为7
	}
	weekdayCn := "星期" + nStr1[weekday]

	// 农历年
	lunarYear := i
	leap := leapMonth(i)
	isLeap := false

	// 计算农历月
	var lunarMonth int
	var lunarDay int
	for i = 1; i < 13 && offset > 0; i++ {
		// 闰月
		if leap > 0 && i == (leap+1) && !isLeap {
			i--
			isLeap = true
			temp = leapDays(lunarYear)
		} else {
			temp = monthDays(lunarYear, i)
		}
		// 解除闰月
		if isLeap && i == (leap+1) {
			isLeap = false
		}
		offset -= temp
	}

	// 闰月导致数组下标重叠取反
	if offset == 0 && leap > 0 && i == leap+1 {
		if isLeap {
			isLeap = false
		} else {
			isLeap = true
			i--
		}
	}
	if offset < 0 {
		offset += temp
		i--
	}

	lunarMonth = i
	lunarDay = offset + 1

	// 天干地支处理
	gzY := toGanZhiYear(lunarYear)

	// 当月的两个节气
	firstNode := getTerm(y, m*2-1)
	secondNode := getTerm(y, m*2)

	// 依据12节气修正干支月
	gzM := toGanZhi((y-1900)*12 + m + 11)
	if d >= firstNode {
		gzM = toGanZhi((y-1900)*12 + m + 12)
	}

	// 传入的日期的节气与否
	var term string
	isTerm := false
	if firstNode == d {
		isTerm = true
		term = solarTerm[m*2-2]
	}
	if secondNode == d {
		isTerm = true
		term = solarTerm[m*2-1]
	}

	// 日柱
	dayBase := time.Date(y, time.Month(m), 1, 0, 0, 0, 0, time.UTC)
	base1900 := time.Date(1900, 1, 1, 0, 0, 0, 0, time.UTC)
	dayCyclical := int(dayBase.Sub(base1900).Hours()/24) + 25567 + 10
	gzD := toGanZhi(dayCyclical + d - 1)

	// 星座
	astro := toAstro(m, d)

	// 节日
	festivalDate := fmt.Sprintf("%d-%d", m, d)
	var festivalTitle string
	if title, ok := festival[festivalDate]; ok {
		festivalTitle = title
	}

	lunarFestivalDate := fmt.Sprintf("%d-%d", lunarMonth, lunarDay)
	var lunarFestivalTitle string
	// 农历节日修正：农历12月小月则29号除夕，大月则30号除夕
	if lunarMonth == 12 && lunarDay == 29 && monthDays(lunarYear, lunarMonth) == 29 {
		lunarFestivalDate = "12-30"
	}
	if title, ok := lFestival[lunarFestivalDate]; ok {
		lunarFestivalTitle = title
	}

	// 农历月份中文
	lunarMonthCn := toChinaMonth(lunarMonth)
	if isLeap {
		lunarMonthCn = "闰" + lunarMonthCn
	}

	return &ConversionResult{
		SolarYear:     y,
		SolarMonth:    m,
		SolarDay:      d,
		LunarYear:     lunarYear,
		LunarMonth:    lunarMonth,
		LunarDay:      lunarDay,
		IsLeap:        isLeap,
		LunarMonthCn:  lunarMonthCn,
		LunarDayCn:    toChinaDay(lunarDay),
		GanZhiYear:    gzY,
		GanZhiMonth:   gzM,
		GanZhiDay:     gzD,
		Animal:        getAnimal(lunarYear),
		Weekday:       weekday,
		WeekdayCn:     weekdayCn,
		Astro:         astro,
		Term:          term,
		IsTerm:        isTerm,
		Festival:      festivalTitle,
		LunarFestival: lunarFestivalTitle,
		IsToday:       isToday,
	}, nil
}

// Lunar2Solar 农历转公历
func Lunar2Solar(year, month, day int, isLeapMonth bool) (*ConversionResult, error) {
	// 参数验证
	if year < 1900 || year > 3000 {
		return nil, errors.New("年份超出支持范围（1900-3000）")
	}
	if (year == 3000 && month == 12 && day > 1) || (year == 1900 && month == 1 && day < 31) {
		return nil, errors.New("日期超出支持范围")
	}

	leapMonthNum := leapMonth(year)
	if isLeapMonth && leapMonthNum != month {
		return nil, fmt.Errorf("该年没有闰%d月", month)
	}

	dayCount := monthDays(year, month)
	if isLeapMonth {
		dayCount = leapDays(year)
	}
	if day > dayCount {
		return nil, fmt.Errorf("日期超出该月范围（最大%d天）", dayCount)
	}

	// 计算农历的时间差
	offset := 0
	for i := 1900; i < year; i++ {
		offset += lYearDays(i)
	}

	// 在循环外计算闰月信息，提高效率
	leap := leapMonth(year)
	isAdd := false
	for i := 1; i < month; i++ {
		// 处理闰月
		if !isAdd && leap > 0 && leap <= i {
			offset += leapDays(year)
			isAdd = true
		}
		offset += monthDays(year, i)
	}

	// 转换闰月农历 需补充该年闰月的前一个月的时差
	if isLeapMonth {
		offset += monthDays(year, month)
	}

	// 1900年农历正月一日的公历时间为1900年1月30日0时0分0秒
	baseDate := time.Date(1900, 2, 30, 0, 0, 0, 0, time.UTC)
	targetDate := baseDate.AddDate(0, 0, offset+day-31)

	cY := targetDate.Year()
	cM := int(targetDate.Month())
	cD := targetDate.Day()

	// 使用 Solar2Lunar 获取完整信息
	return Solar2Lunar(cY, cM, cD)
}

