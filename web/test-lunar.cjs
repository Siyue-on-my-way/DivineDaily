/**
 * 农历日期转换测试
 * 测试1993年闰三月的转换功能
 */

const calendar = require('./src/utils/calendar.js');

console.log('=== 1993年闰三月测试 ===\n');

// 测试1: 检查1993年的闰月
const leapMonth1993 = calendar.leapMonth(1993);
console.log(`1993年闰月: ${leapMonth1993}月`);
console.log(`预期: 3月`);
console.log(`结果: ${leapMonth1993 === 3 ? '✅ 通过' : '❌ 失败'}\n`);

// 测试2: 检查闰三月的天数
const leapDays1993 = calendar.leapDays(1993);
console.log(`1993年闰三月天数: ${leapDays1993}天`);
console.log(`预期: 29天`);
console.log(`结果: ${leapDays1993 === 29 ? '✅ 通过' : '❌ 失败'}\n`);

// 测试3: 农历转公历 - 1993年闰三月十五
console.log('测试: 1993年闰三月十五 -> 公历');
try {
  const result = calendar.lunar2solar(1993, 3, 15, true);
  console.log(`公历日期: ${result.cYear}-${result.cMonth}-${result.cDay}`);
  console.log(`预期: 1993-5-6`);
  console.log(`农历显示: ${result.IMonthCn}${result.IDayCn}`);
  console.log(`是否闰月: ${result.isLeap}`);
  console.log(`结果: ${result.cYear === 1993 && result.cMonth === 5 && result.cDay === 6 && result.isLeap ? '✅ 通过' : '❌ 失败'}\n`);
} catch (error) {
  console.log(`❌ 错误: ${error}\n`);
}

// 测试4: 公历转农历 - 1993-05-06
console.log('测试: 1993-05-06 -> 农历');
try {
  const result = calendar.solar2lunar(1993, 5, 6);
  console.log(`农历日期: ${result.lYear}年${result.IMonthCn}${result.IDayCn}`);
  console.log(`预期: 1993年闰三月十五`);
  console.log(`是否闰月: ${result.isLeap}`);
  console.log(`结果: ${result.lYear === 1993 && result.lMonth === 3 && result.lDay === 15 && result.isLeap ? '✅ 通过' : '❌ 失败'}\n`);
} catch (error) {
  console.log(`❌ 错误: ${error}\n`);
}

// 测试5: 闰三月边界测试
console.log('=== 闰三月边界测试 ===\n');

const testDates = [
  { date: '1993-03-23', expected: '二月初一', isLeap: false },
  { date: '1993-04-21', expected: '三月三十', isLeap: false },
  { date: '1993-04-22', expected: '闰三月初一', isLeap: true },
  { date: '1993-05-20', expected: '闰三月廿九', isLeap: true },
  { date: '1993-05-21', expected: '四月初一', isLeap: false },
];

testDates.forEach(({ date, expected, isLeap }) => {
  const [y, m, d] = date.split('-').map(Number);
  const result = calendar.solar2lunar(y, m, d);
  const actual = result.IMonthCn + result.IDayCn;
  const pass = actual === expected && result.isLeap === isLeap;
  console.log(`${date}: ${actual} (闰月:${result.isLeap}) ${pass ? '✅' : '❌'}`);
  if (!pass) {
    console.log(`  预期: ${expected} (闰月:${isLeap})`);
  }
});

console.log('\n=== 所有测试完成 ===');

