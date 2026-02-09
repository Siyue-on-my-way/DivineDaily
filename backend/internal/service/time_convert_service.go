package service

import "time"

// TimeConvertService 时间转换服务
type TimeConvertService struct {
	// 可以添加缓存等优化
}

// NewTimeConvertService 创建时间转换服务
func NewTimeConvertService() *TimeConvertService {
	return &TimeConvertService{}
}

// Solar2Lunar 公历转农历
func (s *TimeConvertService) Solar2Lunar(year, month, day int) (*ConversionResult, error) {
	return Solar2Lunar(year, month, day)
}

// Lunar2Solar 农历转公历
func (s *TimeConvertService) Lunar2Solar(year, month, day int, isLeapMonth bool) (*ConversionResult, error) {
	return Lunar2Solar(year, month, day, isLeapMonth)
}

// GetDailyInfo 获取指定日期的详细信息（包含农历、节气、节日等）
func (s *TimeConvertService) GetDailyInfo(date time.Time) (*ConversionResult, error) {
	return Solar2Lunar(date.Year(), int(date.Month()), date.Day())
}

// GetSolarTerm 获取指定日期的节气
func (s *TimeConvertService) GetSolarTerm(date time.Time) (string, error) {
	res, err := s.GetDailyInfo(date)
	if err != nil {
		return "", err
	}
	return res.Term, nil
}

// GetFestivals 获取指定日期的节日列表（公历和农历）
func (s *TimeConvertService) GetFestivals(date time.Time) ([]string, error) {
	res, err := s.GetDailyInfo(date)
	if err != nil {
		return nil, err
	}
	var festivals []string
	if res.Festival != "" {
		festivals = append(festivals, res.Festival)
	}
	if res.LunarFestival != "" {
		festivals = append(festivals, res.LunarFestival)
	}
	return festivals, nil
}

