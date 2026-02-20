import { useState, useEffect } from 'react';
import { LunarCalendar } from '../../utils/lunarCalendar';
import type { LunarDate } from '../../types/lunar';
import './LunarDatePicker.css';

interface LunarDatePickerProps {
  value?: LunarDate;
  onChange: (date: LunarDate) => void;
  minYear?: number;
  maxYear?: number;
}

export function LunarDatePicker({ 
  value, 
  onChange,
  minYear = 1900,
  maxYear = 2100
}: LunarDatePickerProps) {
  const [year, setYear] = useState(value?.year || 1990);
  const [month, setMonth] = useState(value?.month || 1);
  const [day, setDay] = useState(value?.day || 1);
  const [isLeap, setIsLeap] = useState(value?.isLeap || false);

  // 获取当前年份的闰月
  const leapMonth = LunarCalendar.getLeapMonth(year);
  
  // 获取当前月份的最大天数
  const maxDay = isLeap && leapMonth === month
    ? LunarCalendar.getLeapDays(year)
    : LunarCalendar.getMonthDays(year, month);

  // 当年份或月份改变时，重置闰月状态和日期
  useEffect(() => {
    // 如果当前月份不是闰月，取消闰月标识
    if (leapMonth !== month) {
      setIsLeap(false);
    }
    // 确保日期不超过当月最大天数
    if (day > maxDay) {
      setDay(maxDay);
    }
  }, [year, month, leapMonth, maxDay, day]);

  // 通知父组件日期变化
  useEffect(() => {
    onChange({ year, month, day, isLeap });
  }, [year, month, day, isLeap, onChange]);

  // 生成年份选项
  const years = Array.from(
    { length: maxYear - minYear + 1 }, 
    (_, i) => minYear + i
  );

  // 生成月份
  const months = Array.from({ length: 12 }, (_, i) => i + 1);

  // 生成日期
  const days = Array.from({ length: maxDay }, (_, i) => i + 1);

  // 获取对应的公历日期
  const getSolarDate = () => {
    try {
      return LunarCalendar.lunarToSolarString({ year, month, day, isLeap });
    } catch {
      return '';
    }
  };

  return (
    <div className="lunar-date-picker">
      <div className="lunar-picker-section">
        <label className="lunar-picker-label">年份</label>
        <select 
          className="lunar-picker-select"
          value={year} 
          onChange={(e) => setYear(Number(e.target.value))}
        >
          {years.map((y) => (
            <option key={y} value={y}>
              {y}年
            </option>
          ))}
        </select>
      </div>

      <div className="lunar-picker-section">
        <label className="lunar-picker-label">月份</label>
        <div className="lunar-month-grid">
          {months.map((m) => (
            <button
              key={m}
              type="button"
              className={`lunar-month-btn ${month === m && !isLeap ? 'active' : ''}`}
              onClick={() => {
                setMonth(m);
                if (leapMonth !== m) {
                  setIsLeap(false);
                }
              }}
            >
              {m}月
            </button>
          ))}
        </div>
      </div>

      {leapMonth > 0 && (
        <div className="lunar-picker-section">
          <label className="lunar-leap-checkbox">
            <input
              type="checkbox"
              checked={isLeap && month === leapMonth}
              disabled={month !== leapMonth}
              onChange={(e) => setIsLeap(e.target.checked)}
            />
            <span className="lunar-leap-text">
              闰{leapMonth}月
              {month !== leapMonth && (
                <span className="lunar-leap-hint"> (请先选择{leapMonth}月)</span>
              )}
            </span>
          </label>
        </div>
      )}

      <div className="lunar-picker-section">
        <label className="lunar-picker-label">日期</label>
        <div className="lunar-day-grid">
          {days.map((d) => (
            <button
              key={d}
              type="button"
              className={`lunar-day-btn ${day === d ? 'active' : ''}`}
              onClick={() => setDay(d)}
            >
              {d}
            </button>
          ))}
        </div>
      </div>

      <div className="lunar-picker-preview">
        <div className="lunar-preview-item">
          <span className="lunar-preview-label">已选择：</span>
          <span className="lunar-preview-value">
            {year}年{isLeap ? '闰' : ''}{month}月{day}日
          </span>
        </div>
        {getSolarDate() && (
          <div className="lunar-preview-item">
            <span className="lunar-preview-label">对应公历：</span>
            <span className="lunar-preview-value">{getSolarDate()}</span>
          </div>
        )}
      </div>
    </div>
  );
}

