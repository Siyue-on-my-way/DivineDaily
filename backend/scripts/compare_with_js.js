/**
 * 对比 Go 版本和 JavaScript 版本的转换结果
 * 使用方法: node scripts/compare_with_js.js
 */

const http = require('http');
const fs = require('fs');
const path = require('path');

// 读取 JavaScript 版本
const jsContent = fs.readFileSync(path.join(__dirname, '../../calendar.js/dist/js-calendar-converter.js'), 'utf-8');
eval(jsContent);

// 测试用例
const testCases = [
  { name: '1987-11-01', year: 1987, month: 11, day: 1 },
  { name: '2000-01-01', year: 2000, month: 1, day: 1 },
  { name: '2024-02-10', year: 2024, month: 2, day: 10 },
  { name: '1900-01-31', year: 1900, month: 1, day: 31 },
  { name: '3000-12-31', year: 3000, month: 12, day: 31 },
];

console.log('开始对比测试...\n');

// 测试公历转农历
console.log('=== 公历转农历对比测试 ===');
testCases.forEach(test => {
  try {
    const jsResult = calendar.solar2lunar(test.year, test.month, test.day);
    if (jsResult === -1) {
      console.log(`❌ ${test.name}: JavaScript 版本返回错误`);
      return;
    }
    
    console.log(`\n测试: ${test.name}`);
    console.log(`JS结果: 农历 ${jsResult.lYear}年${jsResult.IMonthCn}${jsResult.IDayCn}`);
    console.log(`  - 天干地支: ${jsResult.gzYear}年 ${jsResult.gzMonth}月 ${jsResult.gzDay}日`);
    console.log(`  - 生肖: ${jsResult.Animal}, 星座: ${jsResult.astro}`);
    
    // 这里可以添加 HTTP 请求到 Go 服务进行对比
    // 暂时只显示 JavaScript 结果
  } catch (error) {
    console.log(`❌ ${test.name}: 错误 - ${error.message}`);
  }
});

console.log('\n✅ JavaScript 版本测试完成');
console.log('\n提示: 启动 Go 服务器后，可以使用以下命令测试:');
console.log('curl -X POST http://localhost:8080/api/v1/time/solar2lunar \\');
console.log('  -H "Content-Type: application/json" \\');
console.log('  -d \'{"year": 1987, "month": 11, "day": 1}\'');

