import { useState, useEffect } from 'react';
import { Button } from './Button';
import { LunarDatePicker } from './LunarDatePicker';
import { LunarCalendar } from '../../utils/lunarCalendar';
import type { LunarDate } from '../../types/lunar';
import './BirthdayEditModal.css';

interface BirthdayEditModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentBirthDate?: string;
  currentBirthTime?: string;
  onSave: (birthDate: string, birthTime: string) => void;
}

export function BirthdayEditModal({
  isOpen,
  onClose,
  currentBirthDate = '',
  currentBirthTime = '',
  onSave,
}: BirthdayEditModalProps) {
  const [calendarType, setCalendarType] = useState<'solar' | 'lunar'>('solar');
  const [birthDate, setBirthDate] = useState(currentBirthDate);
  const [birthTime, setBirthTime] = useState(currentBirthTime);
  const [lunarDate, setLunarDate] = useState<LunarDate>({
    year: 1990,
    month: 1,
    day: 1,
    isLeap: false,
  });

  useEffect(() => {
    if (isOpen) {
      setBirthDate(currentBirthDate);
      setBirthTime(currentBirthTime);
      setCalendarType('solar');
      
      // 如果有当前日期，尝试转换为农历
      if (currentBirthDate) {
        try {
          const info = LunarCalendar.solarStringToLunar(currentBirthDate);
          setLunarDate({
            year: info.lYear,
            month: info.lMonth,
            day: info.lDay,
            isLeap: info.isLeap,
          });
        } catch (error) {
          console.error('Failed to convert to lunar date:', error);
        }
      }
    }
  }, [isOpen, currentBirthDate, currentBirthTime]);

  // 处理农历日期变化
  const handleLunarDateChange = (date: LunarDate) => {
    setLunarDate(date);
    // 转换为公历并更新
    try {
      const solarDateStr = LunarCalendar.lunarToSolarString(date);
      setBirthDate(solarDateStr);
    } catch (error) {
      console.error('Failed to convert lunar to solar:', error);
    }
  };

  const handleSave = () => {
    if (!birthDate) {
      alert('请选择出生日期');
      return;
    }
    onSave(birthDate, birthTime);
  };

  if (!isOpen) return null;

  return (
    <div className="birthday-modal-overlay" onClick={onClose}>
      <div className="birthday-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="birthday-modal-header">
          <h3>编辑生日信息</h3>
          <button className="birthday-modal-close" onClick={onClose}>
            ✕
          </button>
        </div>

        <div className="birthday-modal-body">
          <div className="birthday-calendar-type">
            <label className="birthday-label">历法类型</label>
            <div className="birthday-calendar-tabs">
              <button
                className={`birthday-calendar-tab ${calendarType === 'solar' ? 'active' : ''}`}
                onClick={() => setCalendarType('solar')}
              >
                公历
              </button>
              <button
                className={`birthday-calendar-tab ${calendarType === 'lunar' ? 'active' : ''}`}
                onClick={() => setCalendarType('lunar')}
              >
                农历
              </button>
            </div>
          </div>

          {calendarType === 'solar' ? (
            <div className="birthday-form-group">
              <label className="birthday-label">出生日期</label>
              <input
                type="date"
                className="birthday-input"
                value={birthDate}
                onChange={(e) => setBirthDate(e.target.value)}
                max={new Date().toISOString().split('T')[0]}
              />
            </div>
          ) : (
            <div className="birthday-form-group">
              <label className="birthday-label">农历出生日期</label>
              <LunarDatePicker
                value={lunarDate}
                onChange={handleLunarDateChange}
              />
            </div>
          )}

          <div className="birthday-form-group">
            <label className="birthday-label">出生时间（可选）</label>
            <input
              type="time"
              className="birthday-input"
              value={birthTime}
              onChange={(e) => setBirthTime(e.target.value)}
            />
          </div>
        </div>

        <div className="birthday-modal-footer">
          <Button variant="secondary" onClick={onClose} fullWidth>
            取消
          </Button>
          <Button variant="primary" onClick={handleSave} fullWidth>
            保存
          </Button>
        </div>
      </div>
    </div>
  );
}
