/**
 * 漏洞验证测试脚本
 * 用于验证算法分析报告中发现的潜在问题
 */

// 注意：需要先导入 calendar 模块
// import calendar from './src/index.js';

// 或者如果使用构建后的版本：
// const calendar = require('./dist/js-calendar-converter.cjs');

console.log('=== 漏洞验证测试 ===\n');

// 测试 1: leapDays 函数参数不匹配问题
console.log('测试 1: leapDays 函数参数验证');
console.log('函数定义: leapDays(y) - 只接受一个参数');
console.log('问题调用: leapDays(y, m) - 传入了两个参数');
console.log('验证: JavaScript 会忽略第二个参数，但代码意图不明确\n');

// 测试 2: 边界条件检查
console.log('测试 2: 边界条件检查');
console.log('测试日期: 3000-12-2 (应该被拒绝)');
// const result1 = calendar.lunar2solar(3000, 12, 2);
// console.log('结果:', result1 === -1 ? '✓ 正确拒绝' : '✗ 未正确拒绝');

console.log('测试日期: 1900-1-30 (应该被拒绝)');
// const result2 = calendar.lunar2solar(1900, 1, 30);
// console.log('结果:', result2 === -1 ? '✓ 正确拒绝' : '✗ 未正确拒绝');

console.log('测试日期: 3000-12-1 (应该被接受)');
// const result3 = calendar.lunar2solar(3000, 12, 1);
// console.log('结果:', result3 !== -1 ? '✓ 正确接受' : '✗ 错误拒绝');

console.log('测试日期: 1900-1-31 (应该被接受)');
// const result4 = calendar.lunar2solar(1900, 1, 31);
// console.log('结果:', result4 !== -1 ? '✓ 正确接受' : '✗ 错误拒绝\n');

// 测试 3: 参数验证
console.log('测试 3: 参数验证');
console.log('测试: parseInt(null)');
console.log('结果:', isNaN(parseInt(null)) ? '✓ 返回 NaN' : '✗ 未返回 NaN');

console.log('测试: parseInt(undefined)');
console.log('结果:', isNaN(parseInt(undefined)) ? '✓ 返回 NaN' : '✗ 未返回 NaN');

console.log('测试: NaN 比较');
const nan = parseInt(null);
console.log('NaN < 1900:', nan < 1900);  // false
console.log('NaN > 3000:', nan > 3000);  // false
console.log('结论: NaN 不会触发边界检查，可能导致问题\n');

// 测试 4: 闰月处理
console.log('测试 4: 闰月处理逻辑');
console.log('问题: leapMonth(y) 在循环中重复调用');
console.log('建议: 在循环外计算一次\n');

// 测试 5: 往返转换一致性
console.log('测试 5: 往返转换一致性');
console.log('测试: 公历 → 农历 → 公历');
// const solarDate = { y: 1987, m: 11, d: 1 };
// const lunar = calendar.solar2lunar(solarDate.y, solarDate.m, solarDate.d);
// const backToSolar = calendar.lunar2solar(lunar.lYear, lunar.lMonth, lunar.lDay, lunar.isLeap);
// console.log('原始:', solarDate);
// console.log('转换后:', backToSolar);
// console.log('一致性:', 
//   backToSolar.cYear === solarDate.y && 
//   backToSolar.cMonth === solarDate.m && 
//   backToSolar.cDay === solarDate.d ? '✓ 一致' : '✗ 不一致');

console.log('\n=== 测试完成 ===');
console.log('\n注意: 取消注释相关代码以运行实际测试');

