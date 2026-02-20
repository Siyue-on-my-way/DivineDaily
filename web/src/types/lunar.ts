/**
 * 农历日期类型定义
 */

export interface LunarDate {
  year: number;
  month: number;
  day: number;
  isLeap: boolean;
}

export interface SolarDate {
  year: number;
  month: number;
  day: number;
}

export interface CalendarInfo {
  // 公历信息
  date: string;
  cYear: number;
  cMonth: number;
  cDay: number;
  
  // 农历信息
  lunarDate: string;
  lYear: number;
  lMonth: number;
  lDay: number;
  isLeap: boolean;
  
  // 中文表示
  IMonthCn: string;  // 农历月份中文（如"三月"或"闰三月"）
  IDayCn: string;    // 农历日期中文（如"初一"）
  
  // 生肖星座
  Animal: string;
  astro: string;
  
  // 干支
  gzYear: string;
  gzMonth: string;
  gzDay: string;
  
  // 星期
  nWeek: number;
  ncWeek: string;
  
  // 节日节气
  festival: string | null;
  lunarFestival: string | null;
  isTerm: boolean;
  Term: string | null;
  
  // 其他
  isToday: boolean;
}

