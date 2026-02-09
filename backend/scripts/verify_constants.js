/**
 * 验证 Go 常量文件与 JavaScript 源文件的一致性
 * 使用方法: node scripts/verify_constants.js
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const CALENDAR_JS_DIR = path.join(__dirname, '../../calendar.js/src/constant');
const GO_CONSTANTS_FILE = path.join(__dirname, '../internal/service/time_convert_constants.go');

console.log('开始验证常量数据一致性...\n');

// 读取 JavaScript 源文件
function readJSConstants() {
  const constants = {};
  
  // 读取 Lunar.js
  const lunarContent = fs.readFileSync(path.join(CALENDAR_JS_DIR, 'Lunar.js'), 'utf-8');
  const lunarMatch = lunarContent.match(/const\s+lunarInfo\s*=\s*\[([\s\S]*?)\];/);
  if (lunarMatch) {
    const hexValues = lunarMatch[1].match(/0x[0-9a-fA-F]+/g) || [];
    constants.lunarInfo = hexValues.map(hex => parseInt(hex, 16));
  }
  
  const solarMatch = lunarContent.match(/const\s+solarMonth\s*=\s*\[([\s\S]*?)\];/);
  if (solarMatch) {
    constants.solarMonth = solarMatch[1].split(',').map(s => parseInt(s.trim())).filter(n => !isNaN(n));
  }
  
  // 读取其他常量文件...
  // 这里可以添加更多验证
  
  return constants;
}

// 读取 Go 文件并提取数据
function readGoConstants() {
  const content = fs.readFileSync(GO_CONSTANTS_FILE, 'utf-8');
  const constants = {};
  
  // 提取 lunarInfo
  const lunarMatch = content.match(/var\s+lunarInfo\s*=\s*\[\]uint32\{([\s\S]*?)\}/);
  if (lunarMatch) {
    const hexValues = lunarMatch[1].match(/0x[0-9a-fA-F]+/g) || [];
    constants.lunarInfo = hexValues.map(hex => parseInt(hex, 16));
  }
  
  // 提取 solarMonth
  const solarMatch = content.match(/var\s+solarMonth\s*=\s*\[\]int\{([\s\S]*?)\}/);
  if (solarMatch) {
    constants.solarMonth = solarMatch[1].split(',').map(s => parseInt(s.trim())).filter(n => !isNaN(n));
  }
  
  return constants;
}

// 对比数据
function compareConstants(jsConstants, goConstants) {
  let allMatch = true;
  
  // 对比 lunarInfo
  if (jsConstants.lunarInfo && goConstants.lunarInfo) {
    if (jsConstants.lunarInfo.length !== goConstants.lunarInfo.length) {
      console.log(`❌ lunarInfo 长度不匹配: JS=${jsConstants.lunarInfo.length}, Go=${goConstants.lunarInfo.length}`);
      allMatch = false;
    } else {
      let mismatchCount = 0;
      for (let i = 0; i < jsConstants.lunarInfo.length; i++) {
        if (jsConstants.lunarInfo[i] !== goConstants.lunarInfo[i]) {
          if (mismatchCount < 5) {
            console.log(`❌ lunarInfo[${i}] 不匹配: JS=0x${jsConstants.lunarInfo[i].toString(16)}, Go=0x${goConstants.lunarInfo[i].toString(16)}`);
          }
          mismatchCount++;
        }
      }
      if (mismatchCount === 0) {
        console.log(`✅ lunarInfo: ${jsConstants.lunarInfo.length} 个元素全部匹配`);
      } else {
        console.log(`❌ lunarInfo: ${mismatchCount} 个元素不匹配`);
        allMatch = false;
      }
    }
  }
  
  // 对比 solarMonth
  if (jsConstants.solarMonth && goConstants.solarMonth) {
    if (JSON.stringify(jsConstants.solarMonth) === JSON.stringify(goConstants.solarMonth)) {
      console.log(`✅ solarMonth: 完全匹配`);
    } else {
      console.log(`❌ solarMonth 不匹配`);
      allMatch = false;
    }
  }
  
  return allMatch;
}

// 测试关键年份的数据
function testKeyYears() {
  console.log('\n测试关键年份数据:');
  
  const testYears = [1900, 1987, 2000, 2024, 3000];
  const jsConstants = readJSConstants();
  const goConstants = readGoConstants();
  
  testYears.forEach(year => {
    const index = year - 1900;
    if (jsConstants.lunarInfo && goConstants.lunarInfo) {
      const jsValue = jsConstants.lunarInfo[index];
      const goValue = goConstants.lunarInfo[index];
      if (jsValue === goValue) {
        console.log(`  ✅ ${year}年: 0x${jsValue.toString(16)}`);
      } else {
        console.log(`  ❌ ${year}年: JS=0x${jsValue.toString(16)}, Go=0x${goValue.toString(16)}`);
      }
    }
  });
}

// 主函数
try {
  const jsConstants = readJSConstants();
  const goConstants = readGoConstants();
  
  console.log('对比常量数据...');
  const allMatch = compareConstants(jsConstants, goConstants);
  
  testKeyYears();
  
  console.log('\n' + '='.repeat(50));
  if (allMatch) {
    console.log('✅ 所有常量数据验证通过！');
    process.exit(0);
  } else {
    console.log('❌ 发现数据不一致，请检查转换脚本');
    process.exit(1);
  }
} catch (error) {
  console.error('验证失败:', error);
  process.exit(1);
}

