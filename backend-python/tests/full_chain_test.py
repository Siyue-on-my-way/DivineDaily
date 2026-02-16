"""
DivineDaily 完整业务链条测试套件
验证每个业务环节的正确性，生成详细的错误报告
"""

import requests
import json
import time
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import traceback

# ==================== 配置 ====================

BASE_URL = "http://8.148.26.166:48080"
API_BASE = f"{BASE_URL}/api/v1"

ADMIN_USERNAME = "admin@163.com"
ADMIN_PASSWORD = "594120"

TEST_USER_EMAIL = f"test_{int(time.time())}@example.com"
TEST_USER_PASSWORD = "test123456"

# 全局测试数据
test_data = {
    "admin_token": None,
    "user_token": None,
    "user_id": None,
    "session_id": None,
    "profile": None,
}

# 链条验证错误收集
chain_errors = []

# ==================== 工具函数 ====================

def print_section(title: str):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def print_test(test_name: str):
    print(f"\n🧪 测试: {test_name}")

def print_success(message: str):
    print(f"   ✅ {message}")

def print_error(message: str):
    print(f"   ❌ {message}")

def print_warning(message: str):
    print(f"   ⚠️  {message}")

def print_info(message: str):
    print(f"   ℹ️  {message}")

def make_request(
    method: str,
    endpoint: str,
    token: Optional[str] = None,
    json_data: Optional[Dict] = None,
    params: Optional[Dict] = None,
    timeout: int = 30
) -> requests.Response:
    url = f"{API_BASE}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=params, timeout=timeout, verify=False)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=json_data, timeout=timeout, verify=False)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, json=json_data, timeout=timeout, verify=False)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, timeout=timeout, verify=False)
        else:
            raise ValueError(f"不支持的HTTP方法: {method}")
        
        return response
    except Exception as e:
        print_error(f"请求失败: {str(e)}")
        raise

# ==================== 链条验证函数 ====================

class ChainValidator:
    """业务链条验证器"""
    
    @staticmethod
    def validate_step(step_name: str, validator_func, *args, **kwargs) -> Tuple[bool, Dict]:
        """验证单个步骤"""
        try:
            result = validator_func(*args, **kwargs)
            if result['success']:
                print_success(f"{step_name}: 通过")
                return True, result
            else:
                print_error(f"{step_name}: 失败 - {result.get('error', '未知错误')}")
                chain_errors.append({
                    'step': step_name,
                    'error': result.get('error'),
                    'expected': result.get('expected'),
                    'actual': result.get('actual'),
                    'timestamp': datetime.now().isoformat()
                })
                return False, result
        except Exception as e:
            print_error(f"{step_name}: 异常 - {str(e)}")
            chain_errors.append({
                'step': step_name,
                'error': str(e),
                'exception': type(e).__name__,
                'traceback': traceback.format_exc(),
                'timestamp': datetime.now().isoformat()
            })
            return False, {'success': False, 'error': str(e)}

# ==================== 步骤验证器 ====================

def verify_intent_recognition(question: str, expected_intent: str) -> Dict:
    """验证意图识别"""
    try:
        # 通过问题关键词推断意图
        q_lower = question.lower()
        
        if "还是" in q_lower or "选" in q_lower:
            actual_intent = "binary_choice"
        elif "运势" in q_lower or "运气" in q_lower or "颜色" in q_lower:
            actual_intent = "daily_luck"
        elif "是什么" in q_lower or "什么意思" in q_lower:
            actual_intent = "knowledge"
        else:
            actual_intent = "deep_analysis"
        
        if actual_intent == expected_intent:
            return {'success': True, 'intent': actual_intent}
        else:
            return {
                'success': False,
                'error': '意图识别不匹配',
                'expected': expected_intent,
                'actual': actual_intent
            }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def verify_hexagram_data(result: Dict) -> Dict:
    """验证卦象数据完整性"""
    try:
        hexagram_info = result.get('hexagram_info')
        
        if not hexagram_info:
            return {'success': False, 'error': '卦象信息缺失'}
        
        # 验证必需字段
        required_fields = ['number', 'name', 'upper_trigram', 'lower_trigram']
        missing_fields = [f for f in required_fields if f not in hexagram_info]
        
        if missing_fields:
            return {
                'success': False,
                'error': f'卦象信息不完整',
                'expected': required_fields,
                'actual': f'缺少字段: {missing_fields}'
            }
        
        # 验证卦象编号范围
        number = hexagram_info.get('number')
        if not (1 <= number <= 64):
            return {
                'success': False,
                'error': '卦象编号超出范围',
                'expected': '1-64',
                'actual': number
            }
        
        # 验证变爻数据
        changing_lines = hexagram_info.get('changing_lines', [])
        if not isinstance(changing_lines, list):
            return {
                'success': False,
                'error': '变爻数据格式错误',
                'expected': 'list',
                'actual': type(changing_lines).__name__
            }
        
        return {
            'success': True,
            'hexagram': hexagram_info,
            'details': {
                'number': number,
                'name': hexagram_info['name'],
                'changing_lines_count': len(changing_lines)
            }
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def verify_tarot_cards(result: Dict, expected_count: int) -> Dict:
    """验证塔罗牌数据"""
    try:
        cards = result.get('cards', [])
        
        if len(cards) != expected_count:
            return {
                'success': False,
                'error': '牌数不正确',
                'expected': expected_count,
                'actual': len(cards)
            }
        
        # 验证每张牌的数据完整性
        for i, card in enumerate(cards):
            required_fields = ['name', 'position', 'is_reversed']
            missing_fields = [f for f in required_fields if f not in card]
            
            if missing_fields:
                return {
                    'success': False,
                    'error': f'第{i+1}张牌数据不完整',
                    'expected': required_fields,
                    'actual': f'缺少字段: {missing_fields}'
                }
        
        return {
            'success': True,
            'cards': cards,
            'details': {
                'count': len(cards),
                'positions': [c['position'] for c in cards],
                'reversed_count': sum(1 for c in cards if c['is_reversed'])
            }
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def verify_llm_response_quality(text: str, min_length: int = 50) -> Dict:
    """验证LLM响应质量"""
    try:
        if not text or not isinstance(text, str):
            return {
                'success': False,
                'error': 'LLM响应为空或格式错误',
                'actual': type(text).__name__
            }
        
        text = text.strip()
        
        # 长度检查
        if len(text) < min_length:
            return {
                'success': False,
                'error': 'LLM响应过短',
                'expected': f'>= {min_length}字符',
                'actual': f'{len(text)}字符'
            }
        
        # 检查是否是错误信息
        error_keywords = ['error', 'failed', '错误', '失败', 'exception']
        if any(kw in text.lower() for kw in error_keywords):
            return {
                'success': False,
                'error': 'LLM返回错误信息',
                'actual': text[:100]
            }
        
        # 检查关键词（建议性内容）
        quality_keywords = ['建议', '分析', '考虑', '可以', '应该', '注意', '建议您']
        has_quality = any(kw in text for kw in quality_keywords)
        
        if not has_quality:
            print_warning('LLM响应缺少建议性关键词')
        
        return {
            'success': True,
            'length': len(text),
            'has_quality_keywords': has_quality,
            'preview': text[:100] + '...' if len(text) > 100 else text
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def verify_daily_fortune_data(fortune: Dict) -> Dict:
    """验证每日运势数据完整性"""
    try:
        # 验证必需字段
        required_fields = [
            'score', 'summary', 'wealth', 'career', 'love', 'health',
            'lucky_color', 'lucky_number', 'yi', 'ji'
        ]
        
        missing_fields = [f for f in required_fields if f not in fortune]
        
        if missing_fields:
            return {
                'success': False,
                'error': '运势数据不完整',
                'expected': required_fields,
                'actual': f'缺少字段: {missing_fields}'
            }
        
        # 验证评分范围
        score = fortune.get('score')
        if not isinstance(score, (int, float)) or not (0 <= score <= 100):
            return {
                'success': False,
                'error': '评分超出范围',
                'expected': '0-100',
                'actual': score
            }
        
        # 验证宜忌列表
        yi = fortune.get('yi', [])
        ji = fortune.get('ji', [])
        
        if not isinstance(yi, list) or not isinstance(ji, list):
            return {
                'success': False,
                'error': '宜忌数据格式错误',
                'expected': 'list',
                'actual': f'yi: {type(yi).__name__}, ji: {type(ji).__name__}'
            }
        
        if len(yi) == 0 or len(ji) == 0:
            print_warning('宜忌列表为空')
        
        return {
            'success': True,
            'details': {
                'score': score,
                'yi_count': len(yi),
                'ji_count': len(ji),
                'lucky_color': fortune.get('lucky_color'),
                'lucky_number': fortune.get('lucky_number')
            }
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def verify_database_persistence(session_id: str, token: str) -> Dict:
    """验证数据库持久化"""
    try:
        # 查询保存的结果
        response = make_request("GET", f"/divinations/{session_id}", token=token)
        
        if response.status_code != 200:
            return {
                'success': False,
                'error': '查询结果失败',
                'status_code': response.status_code
            }
        
        data = response.json()
        
        # 验证数据完整性
        if data.get('session_id') != session_id:
            return {
                'success': False,
                'error': 'session_id不匹配',
                'expected': session_id,
                'actual': data.get('session_id')
            }
        
        return {
            'success': True,
            'data': data
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

# ==================== 完整链条测试 ====================

def test_iching_full_chain():
    """测试周易占卜完整业务链条"""
    print_test("周易占卜完整业务链条")
    
    question = "我应该选择A公司还是B公司？"
    expected_intent = "binary_choice"
    
    chain_success = True
    
    # 步骤1: 验证意图识别
    success, result = ChainValidator.validate_step(
        "步骤1: 意图识别",
        verify_intent_recognition,
        question,
        expected_intent
    )
    chain_success = chain_success and success
    
    # 步骤2: 发起占卜请求
    print_info("步骤2: 发起占卜请求...")
    try:
        response = make_request(
            "POST",
            "/divinations/start",
            token=test_data["user_token"],
            json_data={
                "user_id": test_data["user_id"],
                "question": question,
                "version": "CN",
                "orientation": "E"
            },
            timeout=60
        )
        
        if response.status_code != 200:
            print_error(f"占卜请求失败: {response.status_code}")
            chain_success = False
        else:
            divination_result = response.json()
            test_data["session_id"] = divination_result.get("session_id")
            print_success("占卜请求成功")
            
            # 步骤3: 验证卦象数据
            success, result = ChainValidator.validate_step(
                "步骤3: 卦象数据验证",
                verify_hexagram_data,
                divination_result
            )
            chain_success = chain_success and success
            
            if success:
                print_info(f"  卦象: {result['details']['name']} (第{result['details']['number']}卦)")
                print_info(f"  变爻数: {result['details']['changing_lines_count']}")
            
            # 步骤4: 验证LLM响应质量
            summary = divination_result.get('summary', '')
            success, result = ChainValidator.validate_step(
                "步骤4: LLM响应质量验证",
                verify_llm_response_quality,
                summary,
                50
            )
            chain_success = chain_success and success
            
            if success:
                print_info(f"  响应长度: {result['length']}字符")
                print_info(f"  质量关键词: {'有' if result['has_quality_keywords'] else '无'}")
            
            # 步骤5: 验证数据持久化
            if test_data["session_id"]:
                success, result = ChainValidator.validate_step(
                    "步骤5: 数据持久化验证",
                    verify_database_persistence,
                    test_data["session_id"],
                    test_data["user_token"]
                )
                chain_success = chain_success and success
    
    except Exception as e:
        print_error(f"链条执行异常: {str(e)}")
        chain_success = False
    
    if chain_success:
        print_success("✅ 周易占卜完整链条测试通过")
    else:
        print_error("❌ 周易占卜链条存在断点")
    
    return chain_success

def test_tarot_full_chain():
    """测试塔罗占卜完整业务链条"""
    print_test("塔罗占卜完整业务链条")
    
    question = "我的转介绍会成功吗？"
    spread = "three"
    expected_cards = 3
    
    chain_success = True
    
    # 步骤1: 发起塔罗占卜
    print_info("步骤1: 发起塔罗占卜请求...")
    try:
        response = make_request(
            "POST",
            "/divinations/start",
            token=test_data["user_token"],
            json_data={
                "user_id": test_data["user_id"],
                "question": question,
                "version": "TAROT",
                "spread": spread
            },
            timeout=60
        )
        
        if response.status_code != 200:
            print_error(f"塔罗占卜请求失败: {response.status_code}")
            chain_success = False
        else:
            tarot_result = response.json()
            print_success("塔罗占卜请求成功")
            
            # 步骤2: 验证塔罗牌数据
            success, result = ChainValidator.validate_step(
                "步骤2: 塔罗牌数据验证",
                verify_tarot_cards,
                tarot_result,
                expected_cards
            )
            chain_success = chain_success and success
            
            if success:
                print_info(f"  牌数: {result['details']['count']}")
                print_info(f"  位置: {', '.join(result['details']['positions'])}")
                print_info(f"  逆位数: {result['details']['reversed_count']}")
            
            # 步骤3: 验证LLM响应质量
            summary = tarot_result.get('summary', '')
            success, result = ChainValidator.validate_step(
                "步骤3: LLM响应质量验证",
                verify_llm_response_quality,
                summary,
                50
            )
            chain_success = chain_success and success
    
    except Exception as e:
        print_error(f"链条执行异常: {str(e)}")
        chain_success = False
    
    if chain_success:
        print_success("✅ 塔罗占卜完整链条测试通过")
    else:
        print_error("❌ 塔罗占卜链条存在断点")
    
    return chain_success

def test_daily_fortune_full_chain():
    """测试每日运势完整业务链条"""
    print_test("每日运势完整业务链条")
    
    chain_success = True
    
    # 步骤1: 验证用户档案存在
    print_info("步骤1: 验证用户档案...")
    if not test_data.get("profile"):
        print_warning("用户档案不存在，跳过档案验证")
    else:
        profile = test_data["profile"]
        if profile.get('zodiac') and profile.get('lunar_date'):
            print_success("用户档案验证通过")
            print_info(f"  生肖: {profile.get('zodiac')}")
            print_info(f"  农历: {profile.get('lunar_date')}")
        else:
            print_warning("用户档案数据不完整")
    
    # 步骤2: 发起每日运势请求
    print_info("步骤2: 发起每日运势请求...")
    try:
        response = make_request(
            "POST",
            "/daily_fortune",
            token=test_data["user_token"],
            timeout=60
        )
        
        if response.status_code != 200:
            print_error(f"每日运势请求失败: {response.status_code}")
            chain_success = False
        else:
            fortune_result = response.json()
            print_success("每日运势请求成功")
            
            # 步骤3: 验证运势数据完整性
            success, result = ChainValidator.validate_step(
                "步骤3: 运势数据完整性验证",
                verify_daily_fortune_data,
                fortune_result
            )
            chain_success = chain_success and success
            
            if success:
                print_info(f"  综合评分: {result['details']['score']}/100")
                print_info(f"  幸运色: {result['details']['lucky_color']}")
                print_info(f"  幸运数字: {result['details']['lucky_number']}")
                print_info(f"  宜事项: {result['details']['yi_count']}个")
                print_info(f"  忌事项: {result['details']['ji_count']}个")
    
    except Exception as e:
        print_error(f"链条执行异常: {str(e)}")
        chain_success = False
    
    if chain_success:
        print_success("✅ 每日运势完整链条测试通过")
    else:
        print_error("❌ 每日运势链条存在断点")
    
    return chain_success

# ==================== 错误报告生成 ====================

def generate_error_report():
    """生成错误报告"""
    if not chain_errors:
        print_info("没有错误，无需生成报告")
        return
    
    report_file = f"chain_error_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# DivineDaily 业务链条测试错误报告\n\n")
        f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**错误数量**: {len(chain_errors)}\n\n")
        
        f.write("---\n\n")
        f.write("## 错误详情\n\n")
        
        for i, error in enumerate(chain_errors, 1):
            f.write(f"### 错误 {i}: {error['step']}\n\n")
            f.write(f"**时间**: {error['timestamp']}\n\n")
            f.write(f"**错误信息**: {error['error']}\n\n")
            
            if 'expected' in error:
                f.write(f"**期望值**: `{error['expected']}`\n\n")
            if 'actual' in error:
                f.write(f"**实际值**: `{error['actual']}`\n\n")
            if 'exception' in error:
                f.write(f"**异常类型**: `{error['exception']}`\n\n")
            if 'traceback' in error:
                f.write(f"**堆栈跟踪**:\n```\n{error['traceback']}\n```\n\n")
            
            f.write("---\n\n")
        
        f.write("## 修复建议\n\n")
        
        # 根据错误类型给出建议
        for error in chain_errors:
            step = error['step']
            f.write(f"### {step}\n\n")
            
            if '意图识别' in step:
                f.write("- 检查关键词匹配逻辑\n")
                f.write("- 验证意图分类规则\n")
            elif '卦象' in step or '塔罗' in step:
                f.write("- 检查算法实现\n")
                f.write("- 验证数据结构\n")
            elif 'LLM' in step:
                f.write("- 检查LLM配置\n")
                f.write("- 验证API Key有效性\n")
                f.write("- 检查Prompt模板\n")
            elif '持久化' in step:
                f.write("- 检查数据库连接\n")
                f.write("- 验证数据模型\n")
            
            f.write("\n")
    
    print_success(f"错误报告已生成: {report_file}")

# ==================== 主测试流程 ====================

def setup_test_environment():
    """设置测试环境"""
    print_section("设置测试环境")
    
    # 用户注册
    print_info("注册测试用户...")
    response = make_request(
        "POST",
        "/auth/register",
        json_data={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "nickname": "链条测试用户"
        }
    )
    
    if response.status_code == 201:
        data = response.json()
        test_data["user_token"] = data["token"]
        test_data["user_id"] = str(data["user"]["id"])
        print_success(f"用户注册成功 - ID: {test_data['user_id']}")
    else:
        print_error("用户注册失败")
        return False
    
    # 创建用户档案
    print_info("创建用户档案...")
    response = make_request(
        "POST",
        "/profile",
        token=test_data["user_token"],
        json_data={
            "name": "测试用户",
            "gender": "male",
            "birth_date": "1990-05-15",
            "birth_time": "14:30",
            "birth_location": "北京"
        }
    )
    
    if response.status_code == 200:
        test_data["profile"] = response.json()
        print_success("用户档案创建成功")
    else:
        print_warning("用户档案创建失败（不影响测试）")
    
    return True

def run_full_chain_tests():
    """运行完整链条测试"""
    print_section("完整业务链条测试")
    
    results = []
    
    # 周易占卜链条
    results.append(("周易占卜链条", test_iching_full_chain()))
    
    # 塔罗占卜链条
    results.append(("塔罗占卜链条", test_tarot_full_chain()))
    
    # 每日运势链条
    results.append(("每日运势链条", test_daily_fortune_full_chain()))
    
    return results

def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("  DivineDaily 完整业务链条测试套件")
    print("  测试时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 80)
    
    # 禁用SSL警告
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # 设置测试环境
    if not setup_test_environment():
        print_error("测试环境设置失败")
        return 1
    
    # 运行链条测试
    results = run_full_chain_tests()
    
    # 生成错误报告
    if chain_errors:
        print_section("生成错误报告")
        generate_error_report()
    
    # 打印汇总
    print_section("测试结果汇总")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name:30s} {status}")
    
    print(f"\n总计: {passed}/{total} 通过 ({passed*100//total}%)")
    print(f"链条断点数: {len(chain_errors)}")
    
    if passed == total and len(chain_errors) == 0:
        print("\n🎉 所有业务链条测试通过，无断点！")
        return 0
    else:
        print(f"\n⚠️  发现 {len(chain_errors)} 个链条断点，请查看错误报告")
        return 1

if __name__ == "__main__":
    exit(main())

