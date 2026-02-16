"""
DivineDaily 完整测试套件运行器
运行所有测试并生成报告
"""

import subprocess
import sys
from datetime import datetime
from typing import List, Tuple

def print_header():
    """打印测试头部"""
    print("\n" + "=" * 80)
    print("  DivineDaily 完整测试套件")
    print("  测试时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 80)

def run_test_suite(script_name: str, description: str) -> Tuple[bool, str]:
    """运行单个测试套件"""
    print(f"\n{'='*80}")
    print(f"  运行: {description}")
    print(f"{'='*80}")
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )
        
        # 打印输出
        print(result.stdout)
        if result.stderr:
            print("错误输出:", result.stderr)
        
        success = result.returncode == 0
        return success, result.stdout
    
    except subprocess.TimeoutExpired:
        print(f"❌ 测试超时: {description}")
        return False, "测试超时"
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False, str(e)

def generate_report(results: List[Tuple[str, bool, str]]):
    """生成测试报告"""
    print("\n" + "=" * 80)
    print("  测试报告汇总")
    print("=" * 80)
    
    total = len(results)
    passed = sum(1 for _, success, _ in results if success)
    
    print(f"\n测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"总测试套件: {total}")
    print(f"通过: {passed}")
    print(f"失败: {total - passed}")
    print(f"通过率: {passed*100//total}%")
    
    print("\n详细结果:")
    for name, success, _ in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {name:40s} {status}")
    
    # 保存报告到文件
    report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("DivineDaily 测试报告\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"总测试套件: {total}\n")
        f.write(f"通过: {passed}\n")
        f.write(f"失败: {total - passed}\n")
        f.write(f"通过率: {passed*100//total}%\n\n")
        
        f.write("详细结果:\n")
        for name, success, output in results:
            status = "通过" if success else "失败"
            f.write(f"\n{name}: {status}\n")
            f.write("-" * 80 + "\n")
            f.write(output + "\n")
    
    print(f"\n📄 详细报告已保存到: {report_file}")
    
    return passed == total

def main():
    """主函数"""
    print_header()
    
    # 定义测试套件
    test_suites = [
        ("need_test_case.py", "基础功能测试"),
        ("comprehensive_test.py", "用户端完整测试"),
        ("admin_test.py", "管理端完整测试"),
    ]
    
    results = []
    
    # 运行所有测试套件
    for script, description in test_suites:
        success, output = run_test_suite(script, description)
        results.append((description, success, output))
    
    # 生成报告
    all_passed = generate_report(results)
    
    if all_passed:
        print("\n🎉 所有测试套件通过！")
        return 0
    else:
        print("\n⚠️  部分测试套件失败，请查看详细报告")
        return 1

if __name__ == "__main__":
    exit(main())

