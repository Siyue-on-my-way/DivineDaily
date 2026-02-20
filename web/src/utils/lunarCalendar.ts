/**
 * 农历日历工具类
 * 封装 calendar.js 提供类型安全的接口
 */

import type { LunarDate, CalendarInfo } from '../types/lunar';

// 声明全局 calendar 变量
declare global {
  var calendar: any;
}

// 获取全局 calendar 对象的辅助函数
function getCalendar() {
  if (typeof window !== 'undefined' && (window as any).calendar) {
    return (window as any).calendar;
  }
  throw new Error('calendar.js not loaded. Please ensure calendar.js is loaded before using LunarCalendar.');
}

export class LunarCalendar {
  /**
   * 公历转农历
   */
  static solarToLunar(year: number, month: number, day: number): CalendarInfo {
    const calendar = getCalendar();
    const result = calendar.solar2lunar(year, month, day);
    if (result === -1) {
      throw new Error('日期超出支持范围（1900-2100）');
    }
    return result as CalendarInfo;
  }

  /**
   * 农历转公历
   */
  static lunarToSolar(
    year: number,
    month: number,
    day: number,
    isLeap: boolean = false
  ): CalendarInfo {
    const calendar = getCalendar();
    const result = calendar.lunar2solar(year, month, day, isLeap);
    if (result === -1) {
      throw new Error('日期转换失败');
    }
    return result as CalendarInfo;
  }

  /**
   * 获取某年的闰月（0表示无闰月）
   */
  static getLeapMonth(year: number): number {
    const calendar = getCalendar();
    return calendar.leapMonth(year);
  }

  /**
   * 获取某年闰月的天数
   */
  static getLeapDays(year: number): number {
    const calendar = getCalendar();
    return calendar.leapDays(year);
  }

  /**
   * 获取某年某月的天数
   */
  static getMonthDays(year: number, month: number): number {
    const calendar = getCalendar();
    return calendar.monthDays(year, month);
  }

  /**
   * 获取农历年的总天数
   */
  static getYearDays(year: number): number {
    const calendar = getCalendar();
    return calendar.lYearDays(year);
  }

  /**
   * 将农历日期转换为公历日期字符串（YYYY-MM-DD格式）
   */
  static lunarToSolarString(lunarDate: LunarDate): string {
    const info = this.lunarToSolar(
      lunarDate.year,
      lunarDate.month,
      lunarDate.day,
      lunarDate.isLeap
    );
    const year = info.cYear;
    const month = String(info.cMonth).padStart(2, '0');
    const day = String(info.cDay).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  /**
   * 将公历日期字符串转换为农历信息
   */
  static solarStringToLunar(dateString: string): CalendarInfo {
    const [year, month, day] = dateString.split('-').map(Number);
    return this.solarToLunar(year, month, day);
  }

  /**
   * 格式化农历日期为中文
   */
  static formatLunarDate(lunarDate: LunarDate): string {
    const info = this.lunarToSolar(
      lunarDate.year,
      lunarDate.month,
      lunarDate.day,
      lunarDate.isLeap
    );
    return `${info.lYear}年${info.IMonthCn}${info.IDayCn}`;
  }

  /**
   * 检查某年某月是否为闰月
   */
  static isLeapMonth(year: number, month: number): boolean {
    return this.getLeapMonth(year) === month;
  }

  /**
   * 获取某年的生肖
   */
  static getAnimal(year: number): string {
    const calendar = getCalendar();
    return calendar.getAnimal(year);
  }

  /**
   * 获取某公历日期的星座
   */
  static getAstro(month: number, day: number): string {
    const calendar = getCalendar();
    return calendar.toAstro(month, day);
  }
}
