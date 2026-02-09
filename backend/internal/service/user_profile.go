package service

import (
	"database/sql"
	"divine-daily-backend/internal/database"
	"divine-daily-backend/internal/model"
	"fmt"
	"strings"
	"time"
)

// UserProfileService 用户档案服务
type UserProfileService struct {
	timeConvertSvc *TimeConvertService
}

// NewUserProfileService 创建用户档案服务
func NewUserProfileService() *UserProfileService {
	return &UserProfileService{
		timeConvertSvc: NewTimeConvertService(),
	}
}

// CreateOrUpdateProfile 创建或更新用户档案
func (s *UserProfileService) CreateOrUpdateProfile(userID string, req *model.CreateUserProfileRequest) (*model.UserProfile, error) {
	db := database.GetDB()
	if db == nil {
		return nil, fmt.Errorf("database not initialized")
	}

	// 检查是否存在
	existing, err := s.GetProfile(userID)
	if err != nil && err != sql.ErrNoRows {
		return nil, fmt.Errorf("get existing profile: %w", err)
	}

	// 如果提供了 birth_date，进行农历转换
	var lunarInfo *ConversionResult
	if req.BirthDate != "" {
		// 解析日期
		birthDate, err := time.Parse("2006-01-02", req.BirthDate)
		if err != nil {
			return nil, fmt.Errorf("invalid birth_date format: %w", err)
		}

		// 调用时间转换服务
		lunarInfo, err = s.timeConvertSvc.Solar2Lunar(
			birthDate.Year(),
			int(birthDate.Month()),
			birthDate.Day(),
		)
		if err != nil {
			return nil, fmt.Errorf("convert to lunar: %w", err)
		}
	}

	if existing == nil {
		// 创建新档案
		return s.createProfile(db, userID, req, lunarInfo)
	} else {
		// 更新现有档案
		updateReq := &model.UpdateUserProfileRequest{
			Nickname:       &req.Nickname,
			Gender:         &req.Gender,
			BirthDate:      &req.BirthDate,
			BirthTime:      &req.BirthTime,
			ZodiacSign:     &req.ZodiacSign,
			IsMenstruating: &req.IsMenstruating,
			RecentExercise: &req.RecentExercise,
		}
		return s.updateProfile(db, userID, updateReq, existing, lunarInfo)
	}
}

// UpdateProfile 更新用户档案
func (s *UserProfileService) UpdateProfile(userID string, req *model.UpdateUserProfileRequest) (*model.UserProfile, error) {
	db := database.GetDB()
	if db == nil {
		return nil, fmt.Errorf("database not initialized")
	}

	// 获取现有档案
	existing, err := s.GetProfile(userID)
	if err != nil {
		if err == sql.ErrNoRows {
			return nil, fmt.Errorf("profile not found")
		}
		return nil, fmt.Errorf("get existing profile: %w", err)
	}

	// 检查是否需要重新转换农历信息
	var lunarInfo *ConversionResult
	if req.BirthDate != nil && *req.BirthDate != existing.BirthDate {
		// 日期发生变化，需要重新转换
		birthDate, err := time.Parse("2006-01-02", *req.BirthDate)
		if err != nil {
			return nil, fmt.Errorf("invalid birth_date format: %w", err)
		}

		lunarInfo, err = s.timeConvertSvc.Solar2Lunar(
			birthDate.Year(),
			int(birthDate.Month()),
			birthDate.Day(),
		)
		if err != nil {
			return nil, fmt.Errorf("convert to lunar: %w", err)
		}
	}

	return s.updateProfile(db, userID, req, existing, lunarInfo)
}

// GetProfile 获取用户档案
func (s *UserProfileService) GetProfile(userID string) (*model.UserProfile, error) {
	db := database.GetDB()
	if db == nil {
		return nil, fmt.Errorf("database not initialized")
	}

	query := `
		SELECT user_id, nickname, gender, birth_date, birth_time,
		       lunar_year, lunar_month, lunar_day, is_leap_month,
		       lunar_month_cn, lunar_day_cn,
		       ganzhi_year, ganzhi_month, ganzhi_day,
		       animal, term, is_term,
		       zodiac_sign, is_menstruating, recent_exercise,
		       created_at, updated_at
		FROM user_profiles
		WHERE user_id = $1
	`

	var profile model.UserProfile
	var birthDate sql.NullTime
	var birthTime sql.NullTime
	var createdAt, updatedAt time.Time

	err := db.QueryRow(query, userID).Scan(
		&profile.UserID,
		&profile.Nickname,
		&profile.Gender,
		&birthDate,
		&birthTime,
		&profile.LunarYear,
		&profile.LunarMonth,
		&profile.LunarDay,
		&profile.IsLeapMonth,
		&profile.LunarMonthCn,
		&profile.LunarDayCn,
		&profile.GanZhiYear,
		&profile.GanZhiMonth,
		&profile.GanZhiDay,
		&profile.Animal,
		&profile.Term,
		&profile.IsTerm,
		&profile.ZodiacSign,
		&profile.IsMenstruating,
		&profile.RecentExercise,
		&createdAt,
		&updatedAt,
	)

	if err != nil {
		return nil, err
	}

	// 转换日期格式
	if birthDate.Valid {
		profile.BirthDate = birthDate.Time.Format("2006-01-02")
	}
	if birthTime.Valid {
		profile.BirthTime = birthTime.Time.Format("15:04")
	}
	profile.CreatedAt = createdAt.Format(time.RFC3339)
	profile.UpdatedAt = updatedAt.Format(time.RFC3339)

	return &profile, nil
}

// createProfile 创建新档案
func (s *UserProfileService) createProfile(db *sql.DB, userID string, req *model.CreateUserProfileRequest, lunarInfo *ConversionResult) (*model.UserProfile, error) {
	query := `
		INSERT INTO user_profiles (
			user_id, nickname, gender, birth_date, birth_time,
			lunar_year, lunar_month, lunar_day, is_leap_month,
			lunar_month_cn, lunar_day_cn,
			ganzhi_year, ganzhi_month, ganzhi_day,
			animal, term, is_term,
			zodiac_sign, is_menstruating, recent_exercise
		) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20)
		RETURNING created_at, updated_at
	`

	var birthDate interface{}
	var birthTime interface{}
	if req.BirthDate != "" {
		birthDate = req.BirthDate
	}
	if req.BirthTime != "" {
		birthTime = req.BirthTime
	}

	var lunarYear, lunarMonth, lunarDay interface{}
	var isLeapMonth interface{}
	var lunarMonthCn, lunarDayCn interface{}
	var ganzhiYear, ganzhiMonth, ganzhiDay interface{}
	var animal, term interface{}
	var isTerm interface{}

	if lunarInfo != nil {
		lunarYear = lunarInfo.LunarYear
		lunarMonth = lunarInfo.LunarMonth
		lunarDay = lunarInfo.LunarDay
		isLeapMonth = lunarInfo.IsLeap
		lunarMonthCn = lunarInfo.LunarMonthCn
		lunarDayCn = lunarInfo.LunarDayCn
		ganzhiYear = lunarInfo.GanZhiYear
		ganzhiMonth = lunarInfo.GanZhiMonth
		ganzhiDay = lunarInfo.GanZhiDay
		animal = lunarInfo.Animal
		term = lunarInfo.Term
		isTerm = lunarInfo.IsTerm
	}

	var createdAt, updatedAt time.Time
	err := db.QueryRow(query,
		userID,
		req.Nickname,
		req.Gender,
		birthDate,
		birthTime,
		lunarYear,
		lunarMonth,
		lunarDay,
		isLeapMonth,
		lunarMonthCn,
		lunarDayCn,
		ganzhiYear,
		ganzhiMonth,
		ganzhiDay,
		animal,
		term,
		isTerm,
		req.ZodiacSign,
		req.IsMenstruating,
		req.RecentExercise,
	).Scan(&createdAt, &updatedAt)

	if err != nil {
		return nil, fmt.Errorf("insert profile: %w", err)
	}

	// 构建返回结果
	profile := &model.UserProfile{
		UserID:         userID,
		Nickname:       req.Nickname,
		Gender:         req.Gender,
		BirthDate:      req.BirthDate,
		BirthTime:      req.BirthTime,
		ZodiacSign:     req.ZodiacSign,
		IsMenstruating: req.IsMenstruating,
		RecentExercise: req.RecentExercise,
		CreatedAt:      createdAt.Format(time.RFC3339),
		UpdatedAt:      updatedAt.Format(time.RFC3339),
	}

	if lunarInfo != nil {
		profile.LunarYear = lunarInfo.LunarYear
		profile.LunarMonth = lunarInfo.LunarMonth
		profile.LunarDay = lunarInfo.LunarDay
		profile.IsLeapMonth = lunarInfo.IsLeap
		profile.LunarMonthCn = lunarInfo.LunarMonthCn
		profile.LunarDayCn = lunarInfo.LunarDayCn
		profile.GanZhiYear = lunarInfo.GanZhiYear
		profile.GanZhiMonth = lunarInfo.GanZhiMonth
		profile.GanZhiDay = lunarInfo.GanZhiDay
		profile.Animal = lunarInfo.Animal
		profile.Term = lunarInfo.Term
		profile.IsTerm = lunarInfo.IsTerm
	}

	return profile, nil
}

// updateProfile 更新现有档案
func (s *UserProfileService) updateProfile(db *sql.DB, userID string, req *model.UpdateUserProfileRequest, existing *model.UserProfile, lunarInfo *ConversionResult) (*model.UserProfile, error) {
	// 构建更新字段
	var updates []string
	var args []interface{}
	argIndex := 1

	// 更新基础字段
	if req.Nickname != nil {
		updates = append(updates, fmt.Sprintf("nickname = $%d", argIndex))
		args = append(args, *req.Nickname)
		argIndex++
	}
	if req.Gender != nil {
		updates = append(updates, fmt.Sprintf("gender = $%d", argIndex))
		args = append(args, *req.Gender)
		argIndex++
	}
	if req.BirthDate != nil {
		updates = append(updates, fmt.Sprintf("birth_date = $%d", argIndex))
		args = append(args, *req.BirthDate)
		argIndex++
	}
	if req.BirthTime != nil {
		updates = append(updates, fmt.Sprintf("birth_time = $%d", argIndex))
		args = append(args, *req.BirthTime)
		argIndex++
	}
	if req.ZodiacSign != nil {
		updates = append(updates, fmt.Sprintf("zodiac_sign = $%d", argIndex))
		args = append(args, *req.ZodiacSign)
		argIndex++
	}
	if req.IsMenstruating != nil {
		updates = append(updates, fmt.Sprintf("is_menstruating = $%d", argIndex))
		args = append(args, *req.IsMenstruating)
		argIndex++
	}
	if req.RecentExercise != nil {
		updates = append(updates, fmt.Sprintf("recent_exercise = $%d", argIndex))
		args = append(args, *req.RecentExercise)
		argIndex++
	}

	// 如果日期变化，更新农历信息
	if lunarInfo != nil {
		updates = append(updates, fmt.Sprintf("lunar_year = $%d", argIndex))
		args = append(args, lunarInfo.LunarYear)
		argIndex++
		updates = append(updates, fmt.Sprintf("lunar_month = $%d", argIndex))
		args = append(args, lunarInfo.LunarMonth)
		argIndex++
		updates = append(updates, fmt.Sprintf("lunar_day = $%d", argIndex))
		args = append(args, lunarInfo.LunarDay)
		argIndex++
		updates = append(updates, fmt.Sprintf("is_leap_month = $%d", argIndex))
		args = append(args, lunarInfo.IsLeap)
		argIndex++
		updates = append(updates, fmt.Sprintf("lunar_month_cn = $%d", argIndex))
		args = append(args, lunarInfo.LunarMonthCn)
		argIndex++
		updates = append(updates, fmt.Sprintf("lunar_day_cn = $%d", argIndex))
		args = append(args, lunarInfo.LunarDayCn)
		argIndex++
		updates = append(updates, fmt.Sprintf("ganzhi_year = $%d", argIndex))
		args = append(args, lunarInfo.GanZhiYear)
		argIndex++
		updates = append(updates, fmt.Sprintf("ganzhi_month = $%d", argIndex))
		args = append(args, lunarInfo.GanZhiMonth)
		argIndex++
		updates = append(updates, fmt.Sprintf("ganzhi_day = $%d", argIndex))
		args = append(args, lunarInfo.GanZhiDay)
		argIndex++
		updates = append(updates, fmt.Sprintf("animal = $%d", argIndex))
		args = append(args, lunarInfo.Animal)
		argIndex++
		updates = append(updates, fmt.Sprintf("term = $%d", argIndex))
		args = append(args, lunarInfo.Term)
		argIndex++
		updates = append(updates, fmt.Sprintf("is_term = $%d", argIndex))
		args = append(args, lunarInfo.IsTerm)
		argIndex++
	}

	if len(updates) == 0 {
		// 没有需要更新的字段
		return existing, nil
	}

	// 添加 updated_at
	updates = append(updates, fmt.Sprintf("updated_at = CURRENT_TIMESTAMP"))
	args = append(args, userID)

	query := fmt.Sprintf(`
		UPDATE user_profiles
		SET %s
		WHERE user_id = $%d
		RETURNING user_id, nickname, gender, birth_date, birth_time,
		          lunar_year, lunar_month, lunar_day, is_leap_month,
		          lunar_month_cn, lunar_day_cn,
		          ganzhi_year, ganzhi_month, ganzhi_day,
		          animal, term, is_term,
		          zodiac_sign, is_menstruating, recent_exercise,
		          created_at, updated_at
	`, strings.Join(updates, ", "), argIndex)

	var profile model.UserProfile
	var birthDate sql.NullTime
	var birthTime sql.NullTime
	var createdAt, updatedAt time.Time

	err := db.QueryRow(query, args...).Scan(
		&profile.UserID,
		&profile.Nickname,
		&profile.Gender,
		&birthDate,
		&birthTime,
		&profile.LunarYear,
		&profile.LunarMonth,
		&profile.LunarDay,
		&profile.IsLeapMonth,
		&profile.LunarMonthCn,
		&profile.LunarDayCn,
		&profile.GanZhiYear,
		&profile.GanZhiMonth,
		&profile.GanZhiDay,
		&profile.Animal,
		&profile.Term,
		&profile.IsTerm,
		&profile.ZodiacSign,
		&profile.IsMenstruating,
		&profile.RecentExercise,
		&createdAt,
		&updatedAt,
	)

	if err != nil {
		return nil, fmt.Errorf("update profile: %w", err)
	}

	// 转换日期格式
	if birthDate.Valid {
		profile.BirthDate = birthDate.Time.Format("2006-01-02")
	}
	if birthTime.Valid {
		profile.BirthTime = birthTime.Time.Format("15:04")
	}
	profile.CreatedAt = createdAt.Format(time.RFC3339)
	profile.UpdatedAt = updatedAt.Format(time.RFC3339)

	return &profile, nil
}

