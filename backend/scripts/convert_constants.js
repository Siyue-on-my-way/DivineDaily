/**
 * 将 JavaScript 常量文件转换为 Go 常量文件
 * 使用方法: node convert_constants.js
 */

const fs = require('fs');
const path = require('path');

// 常量文件路径
const CALENDAR_JS_DIR = path.join(__dirname, '../../calendar.js/src/constant');
const OUTPUT_DIR = path.join(__dirname, '../internal/service');

// 确保输出目录存在
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

/**
 * 解析 Unicode 转义序列
 */
function parseUnicodeString(str) {
  // 处理 \uXXXX 格式的 Unicode 转义
  return str.replace(/\\u([0-9a-fA-F]{4})/g, (match, hex) => {
    return String.fromCharCode(parseInt(hex, 16));
  });
}

/**
 * 读取并解析 JavaScript 模块
 */
function requireJSModule(filePath) {
  const content = fs.readFileSync(filePath, 'utf-8');
  const module = {};
  
  try {
    if (filePath.includes('Lunar.js')) {
      // 提取 lunarInfo 数组（十六进制）
      const lunarMatch = content.match(/const\s+lunarInfo\s*=\s*\[([\s\S]*?)\];/);
      if (lunarMatch) {
        const arrayContent = lunarMatch[1];
        // 提取所有 0x 开头的十六进制数
        const hexValues = arrayContent.match(/0x[0-9a-fA-F]+/g) || [];
        module.lunarInfo = hexValues.map(hex => parseInt(hex, 16));
      }
      
      // 提取 solarMonth 数组
      const solarMatch = content.match(/const\s+solarMonth\s*=\s*\[([\s\S]*?)\];/);
      if (solarMatch) {
        const arrayContent = solarMatch[1];
        const values = arrayContent.split(',').map(s => parseInt(s.trim())).filter(n => !isNaN(n));
        module.solarMonth = values;
      }
    } else if (filePath.includes('ChineseEra.js')) {
      // 提取 Gan 数组
      const ganMatch = content.match(/const\s+Gan\s*=\s*\[([\s\S]*?)\];/);
      if (ganMatch) {
        const arrayContent = ganMatch[1];
        // 提取所有字符串（包括 Unicode 转义）
        const strings = arrayContent.match(/"([^"]+)"/g) || arrayContent.match(/'([^']+)'/g) || [];
        module.Gan = strings.map(s => {
          const str = s.slice(1, -1); // 去掉引号
          return parseUnicodeString(str);
        });
      }
      
      // 提取 Zhi 数组
      const zhiMatch = content.match(/const\s+Zhi\s*=\s*\[([\s\S]*?)\];/);
      if (zhiMatch) {
        const arrayContent = zhiMatch[1];
        const strings = arrayContent.match(/"([^"]+)"/g) || arrayContent.match(/'([^']+)'/g) || [];
        module.Zhi = strings.map(s => {
          const str = s.slice(1, -1);
          return parseUnicodeString(str);
        });
      }
    } else if (filePath.includes('ChineseZodiac.js')) {
      const zodiacMatch = content.match(/const\s+ChineseZodiac\s*=\s*\[([\s\S]*?)\];/);
      if (zodiacMatch) {
        const arrayContent = zodiacMatch[1];
        const strings = arrayContent.match(/"([^"]+)"/g) || arrayContent.match(/'([^']+)'/g) || [];
        module.ChineseZodiac = strings.map(s => {
          const str = s.slice(1, -1);
          return parseUnicodeString(str);
        });
      }
    } else if (filePath.includes('Salutation.js')) {
      ['nStr1', 'nStr2', 'nStr3'].forEach(varName => {
        const match = content.match(new RegExp(`const\\s+${varName}\\s*=\\s*\\[([\\s\\S]*?)\\];`));
        if (match) {
          const arrayContent = match[1];
          const strings = arrayContent.match(/"([^"]+)"/g) || arrayContent.match(/'([^']+)'/g) || [];
          module[varName] = strings.map(s => {
            const str = s.slice(1, -1);
            return parseUnicodeString(str);
          });
        }
      });
    } else if (filePath.includes('SolarTerm.js')) {
      // solarTerm 数组
      const termMatch = content.match(/const\s+solarTerm\s*=\s*\[([\s\S]*?)\];/);
      if (termMatch) {
        const arrayContent = termMatch[1];
        const strings = arrayContent.match(/"([^"]+)"/g) || arrayContent.match(/'([^']+)'/g) || [];
        module.solarTerm = strings.map(s => {
          const str = s.slice(1, -1);
          return parseUnicodeString(str);
        });
      }
      
      // sTermInfo 数组（字符串数组）
      const sTermInfoMatch = content.match(/const\s+sTermInfo\s*=\s*\[([\s\S]*?)\];/);
      if (sTermInfoMatch) {
        const arrayContent = sTermInfoMatch[1];
        const strings = arrayContent.match(/'([^']+)'/g) || arrayContent.match(/"([^"]+)"/g) || [];
        module.sTermInfo = strings.map(s => s.slice(1, -1)); // 不需要解析 Unicode，已经是 ASCII
      }
    } else if (filePath.includes('Festival.js')) {
      // festival 对象
      const festivalMatch = content.match(/const\s+festival\s*=\s*\{([\s\S]*?)\};/);
      if (festivalMatch) {
        const objContent = festivalMatch[1];
        module.festival = {};
        // 提取 'key': { title: 'value' } 格式
        const entries = objContent.match(/'([^']+)':\s*\{\s*title:\s*'([^']+)'\s*\}/g) || [];
        entries.forEach(entry => {
          const match = entry.match(/'([^']+)':\s*\{\s*title:\s*'([^']+)'\s*\}/);
          if (match) {
            module.festival[match[1]] = { title: match[2] };
          }
        });
      }
      
      // lFestival 对象
      const lFestivalMatch = content.match(/const\s+lFestival\s*=\s*\{([\s\S]*?)\};/);
      if (lFestivalMatch) {
        const objContent = lFestivalMatch[1];
        module.lFestival = {};
        const entries = objContent.match(/'([^']+)':\s*\{\s*title:\s*'([^']+)'\s*\}/g) || [];
        entries.forEach(entry => {
          const match = entry.match(/'([^']+)':\s*\{\s*title:\s*'([^']+)'\s*\}/);
          if (match) {
            module.lFestival[match[1]] = { title: match[2] };
          }
        });
      }
    }
  } catch (e) {
    console.error(`Error parsing ${filePath}:`, e.message);
    console.error(e.stack);
  }
  
  return module;
}

/**
 * 转换十六进制数组为 Go 格式
 */
function convertHexArrayToGo(name, values) {
  let goCode = `var ${name} = []uint32{\n`;
  
  // 每行10个元素
  for (let i = 0; i < values.length; i += 10) {
    const line = values.slice(i, i + 10);
    const lineStr = line.map(v => {
      if (typeof v === 'number') {
        return `0x${v.toString(16).padStart(4, '0')}`;
      }
      if (typeof v === 'string') {
        const hex = v.trim();
        if (hex.startsWith('0x')) {
          return hex;
        }
        return `0x${hex}`;
      }
      return v.toString();
    }).join(', ');
    goCode += `\t${lineStr}`;
    // Go 允许在最后一个元素后加逗号，这样更安全
    goCode += ',\n';
  }
  
  goCode += '}\n';
  return goCode;
}

/**
 * 转换字符串数组为 Go 格式
 */
function convertStringArrayToGo(name, values) {
  let goCode = `var ${name} = []string{\n`;
  
  for (let i = 0; i < values.length; i += 10) {
    const line = values.slice(i, i + 10);
    const lineStr = line.map(v => `"${v}"`).join(', ');
    goCode += `\t${lineStr}`;
    // Go 允许在最后一个元素后加逗号
    goCode += ',\n';
  }
  
  goCode += '}\n';
  return goCode;
}

/**
 * 转换整数数组为 Go 格式
 */
function convertIntArrayToGo(name, values) {
  let goCode = `var ${name} = []int{\n`;
  
  for (let i = 0; i < values.length; i += 12) {
    const line = values.slice(i, i + 12);
    const lineStr = line.join(', ');
    goCode += `\t${lineStr}`;
    // Go 允许在最后一个元素后加逗号
    goCode += ',\n';
  }
  
  goCode += '}\n';
  return goCode;
}

/**
 * 转换对象为 Go map 格式
 */
function convertObjectToGoMap(name, obj) {
  let goCode = `var ${name} = map[string]string{\n`;
  
  const entries = Object.entries(obj);
  for (const [key, value] of entries) {
    goCode += `\t"${key}": "${value.title || value}",\n`;
  }
  
  goCode += '}\n';
  return goCode;
}

/**
 * 主转换函数
 */
function convertConstants() {
  console.log('开始转换常量文件...\n');
  
  let goCode = `package service

// 此文件由 scripts/convert_constants.js 自动生成
// 请勿手动编辑

`;

  // 1. 转换 Lunar.js
  console.log('转换 Lunar.js...');
  const lunarPath = path.join(CALENDAR_JS_DIR, 'Lunar.js');
  const lunarModule = requireJSModule(lunarPath);
  
  if (lunarModule.lunarInfo && Array.isArray(lunarModule.lunarInfo)) {
    // lunarInfo 已经是解析好的整数数组
    goCode += convertHexArrayToGo('lunarInfo', lunarModule.lunarInfo);
    goCode += '\n';
  }
  
  if (lunarModule.solarMonth) {
    goCode += convertIntArrayToGo('solarMonth', lunarModule.solarMonth);
    goCode += '\n';
  }

  // 2. 转换 ChineseEra.js
  console.log('转换 ChineseEra.js...');
  const eraPath = path.join(CALENDAR_JS_DIR, 'ChineseEra.js');
  const eraModule = requireJSModule(eraPath);
  
  if (eraModule.Gan) {
    goCode += convertStringArrayToGo('gan', eraModule.Gan);
    goCode += '\n';
  }
  
  if (eraModule.Zhi) {
    goCode += convertStringArrayToGo('zhi', eraModule.Zhi);
    goCode += '\n';
  }

  // 3. 转换 ChineseZodiac.js
  console.log('转换 ChineseZodiac.js...');
  const zodiacPath = path.join(CALENDAR_JS_DIR, 'ChineseZodiac.js');
  const zodiacModule = requireJSModule(zodiacPath);
  
  if (zodiacModule.ChineseZodiac) {
    goCode += convertStringArrayToGo('chineseZodiac', zodiacModule.ChineseZodiac);
    goCode += '\n';
  }

  // 4. 转换 Salutation.js
  console.log('转换 Salutation.js...');
  const salutationPath = path.join(CALENDAR_JS_DIR, 'Salutation.js');
  const salutationModule = requireJSModule(salutationPath);
  
  if (salutationModule.nStr1) {
    goCode += convertStringArrayToGo('nStr1', salutationModule.nStr1);
    goCode += '\n';
  }
  
  if (salutationModule.nStr2) {
    goCode += convertStringArrayToGo('nStr2', salutationModule.nStr2);
    goCode += '\n';
  }
  
  if (salutationModule.nStr3) {
    goCode += convertStringArrayToGo('nStr3', salutationModule.nStr3);
    goCode += '\n';
  }

  // 5. 转换 SolarTerm.js
  console.log('转换 SolarTerm.js...');
  const solarTermPath = path.join(CALENDAR_JS_DIR, 'SolarTerm.js');
  const solarTermModule = requireJSModule(solarTermPath);
  
  if (solarTermModule.solarTerm) {
    goCode += convertStringArrayToGo('solarTerm', solarTermModule.solarTerm);
    goCode += '\n';
  }
  
  if (solarTermModule.sTermInfo) {
    goCode += convertStringArrayToGo('sTermInfo', solarTermModule.sTermInfo);
    goCode += '\n';
  }

  // 6. 转换 Festival.js
  console.log('转换 Festival.js...');
  const festivalPath = path.join(CALENDAR_JS_DIR, 'Festival.js');
  const festivalModule = requireJSModule(festivalPath);
  
  if (festivalModule.festival) {
    goCode += convertObjectToGoMap('festival', festivalModule.festival);
    goCode += '\n';
  }
  
  if (festivalModule.lFestival) {
    goCode += convertObjectToGoMap('lFestival', festivalModule.lFestival);
    goCode += '\n';
  }

  // 写入文件
  const outputPath = path.join(OUTPUT_DIR, 'time_convert_constants.go');
  fs.writeFileSync(outputPath, goCode, 'utf-8');
  
  console.log(`\n✅ 转换完成！输出文件: ${outputPath}`);
  console.log(`文件大小: ${(goCode.length / 1024).toFixed(2)} KB`);
}

// 运行转换
try {
  convertConstants();
} catch (error) {
  console.error('转换失败:', error);
  process.exit(1);
}

