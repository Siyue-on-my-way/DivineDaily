/**
 * calendar.js 类型声明文件
 */

declare module '*/calendar.js' {
  interface CalendarResult {
    date: string;
    lunarDate: string;
    festival: string | null;
    lunarFestival: string | null;
    lYear: number;
    lMonth: number;
    lDay: number;
    Animal: string;
    IMonthCn: string;
    IDayCn: string;
    cYear: number;
    cMonth: number;
    cDay: number;
    gzYear: string;
    gzMonth: string;
    gzDay: string;
    isToday: boolean;
    isLeap: boolean;
    nWeek: number;
    ncWeek: string;
    isTerm: boolean;
    Term: string | null;
    astro: string;
  }

  interface Calendar {
    solar2lunar(year: number, month: number, day: number): CalendarResult | -1;
    lunar2solar(year: number, month: number, day: number, isLeapMonth?: boolean): CalendarResult | -1;
    leapMonth(year: number): number;
    leapDays(year: number): number;
    monthDays(year: number, month: number): number;
    lYearDays(year: number): number;
    getAnimal(year: number): string;
    toAstro(month: number, day: number): string;
    toChinaMonth(month: number): string;
    toChinaDay(day: number): string;
  }

  const calendar: Calendar;
  export default calendar;
}
