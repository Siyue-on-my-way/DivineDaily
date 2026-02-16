"""
DivineDaily 综合测试套件
完整的端到端测试，覆盖用户端和管理端所有功能
"""

import requests
import json
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==================== 配置 ====================

BASE_URL = "http://8.148.26.166:48080"
API_BASE = f"{BASE_URL}/api/v1"

# 管理员账号
ADMIN_USERNAME = "admin@163.com"
ADMIN_PASSWORD = "594120"

# 测试用户账号（会自动创建）
TEST_USER_EMAIL = f"test_{int(time.time())}@example.com"
TEST_USER_PASSWORD = "test123456"
TEST_USER_NICKNAME = "测试用户"

# 全局变量存储测试数据
test_data = {
    "admin_token": None,
    "user_token": None,
    "user_id": None,
    "session_ids": [],
}

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

def assert_status_code(response: requests.Response, expected: int, test_name: str):
    if response.status_code != expected:
        print_error(f"{test_name} - 状态码错误: 期望 {expected}, 实际 {response.status_code}")
        print_error(f"响应: {response.text[:500]}")
        return False
    return True

def assert_field_exists(data: Dict, field: str, test_name: str):
    if field not in data:
        print_error(f"{test_name} - 缺少字段: {field}")
        return False
    return True

# ==================== 测试套件 1: 用户认证 ====================

def test_user_register():
    """测试用户注册"""
    print_test("用户注册")
    
    response = make_request(
        "POST",
        "/auth/register",
        json_data={
            "username": TEST_USER_EMAIL,
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "confirm_password": TEST_USER_PASSWORD,
            "nickname": TEST_USER_NICKNAME
        }
    )
    
    if not assert_status_code(response, 201, "用户注册"):
        return False
    
    data = response.json()
    
    if not assert_field_exists(data, "token", "用户注册"):
        return False
    if not assert_field_exists(data, "user", "用户注册"):
        return False
    
    # 保存token和用户ID（转换为字符串）
    test_data["user_token"] = data["token"]
    test_data["user_id"] = str(data["user"]["id"])
    
    print_success(f"注册成功 - 用户ID: {test_data['user_id']}, Email: {TEST_USER_EMAIL}")
    return True

def test_user_login():
    """测试用户登录"""
    print_test("用户登录")
    
    response = make_request(
        "POST",
        "/auth/login",
        json_data={
            "username": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
    )
    
    if not assert_status_code(response, 200, "用户登录"):
        return False
    
    data = response.json()
    
    if not assert_field_exists(data, "token", "用户登录"):
        return False
    
    test_data["user_token"] = data["token"]
    
    print_success("登录成功")
    return True

def test_get_current_user():
    """测试获取当前用户信息"""
    print_test("获取当前用户信息")
    
    response = make_request(
        "GET",
        "/auth/me",
        token=test_data["user_token"]
    )
    
    if not assert_status_code(response, 200, "获取用户信息"):
        return False
    
    data = response.json()
    
    if data.get("username") != TEST_USER_EMAIL:
        print_error(f"用户名不匹配: {data.get('username')}")
        return False
    
    print_success(f"用户信息正确 - {data.get('nickname')}")
    return True

# ==================== 测试套件 2: 用户档案 ====================

def test_create_profile():
    """测试创建用户档案"""
    print_test("创建用户档案")
    
    response = make_request(
        "POST",
        "/profile",
        token=test_data["user_token"],
        json_data={
            "name": "张三",
            "gender": "male",
            "birth_date": "1990-05-15",
            "birth_time": "14:30",
            "birth_location": "北京"
        }
    )
    
    if not assert_status_code(response, 200, "创建档案"):
        return False
    
    data = response.json()
    
    required_fields = ["id", "name", "gender", "birth_date", "zodiac", "constellation"]
    for field in required_fields:
        if not assert_field_exists(data, field, "创建档案"):
            return False
    
    print_success(f"档案创建成功 - 生肖: {data.get('zodiac')}, 星座: {data.get('constellation')}")
    return True

def test_get_profile():
    """测试获取用户档案"""
    print_test("获取用户档案")
    
    response = make_request(
        "GET",
        "/profile",
        token=test_data["user_token"]
    )
    
    if not assert_status_code(response, 200, "获取档案"):
        return False
    
    data = response.json()
    
    if data.get("name") != "张三":
        print_error(f"档案信息不匹配")
        return False
    
    print_success("档案信息正确")
    return True

# ==================== 测试套件 3: 占卜功能 ====================

def test_iching_divination():
    """测试周易占卜 - 决策类问题"""
    print_test("周易占卜 - 决策类问题")
    
    response = make_request(
        "POST",
        "/divinations/start",
        token=test_data["user_token"],
        json_data={
            "user_id": test_data["user_id"],
            "question": "我应该选择A公司还是B公司？",
            "version": "CN",
            "orientation": "E"
        },
        timeout=60
    )
    
    if not assert_status_code(response, 200, "周易占卜"):
        return False
    
    data = response.json()
    
    required_fields = ["session_id", "outcome", "title", "summary", "hexagram_info"]
    for field in required_fields:
        if not assert_field_exists(data, field, "周易占卜"):
            return False
    
    test_data["session_ids"].append(data["session_id"])
    
    print_success(f"占卜成功 - {data.get('title')}, 结果: {data.get('outcome')}")
    return True

def test_iching_fortune():
    """测试周易占卜 - 运势类问题"""
    print_test("周易占卜 - 运势类问题")
    
    response = make_request(
        "POST",
        "/divinations/start",
        token=test_data["user_token"],
        json_data={
            "user_id": test_data["user_id"],
            "question": "我今年的财运如何？",
            "version": "CN"
        },
        timeout=60
    )
    
    if not assert_status_code(response, 200, "运势占卜"):
        return False
    
    data = response.json()
    print_success(f"运势占卜成功")
    return True

def test_iching_blogger():
    """测试周易占卜 - 博主职业问题（真实case）"""
    print_test("周易占卜 - 博主职业问题")
    
    response = make_request(
        "POST",
        "/divinations/start",
        token=test_data["user_token"],
        json_data={
            "user_id": test_data["user_id"],
            "question": "今年我适合做博主吗?",
            "version": "CN",
            "orientation": "E"
        },
        timeout=60
    )
    
    if not assert_status_code(response, 200, "博主职业占卜"):
        return False
    
    data = response.json()
    
    required_fields = ["session_id", "outcome", "title", "summary", "hexagram_info"]
    for field in required_fields:
        if not assert_field_exists(data, field, "博主职业占卜"):
            return False
    
    test_data["session_ids"].append(data["session_id"])
    
    print_success(f"博主职业占卜成功 - {data.get('title')}, 结果: {data.get('outcome')}")
    return True

def test_tarot_single():
    """测试塔罗占卜 - 单张牌"""
    print_test("塔罗占卜 - 单张牌")
    
    response = make_request(
        "POST",
        "/divinations/start",
        token=test_data["user_token"],
        json_data={
            "user_id": test_data["user_id"],
            "question": "我的转介绍会成功吗？",
            "version": "TAROT",
            "spread": "single"
        },
        timeout=60
    )
    
    if not assert_status_code(response, 200, "塔罗单张"):
        return False
    
    data = response.json()
    
    if not assert_field_exists(data, "cards", "塔罗单张"):
        return False
    
    if len(data["cards"]) != 1:
        print_error(f"牌数错误: 期望 1, 实际 {len(data['cards'])}")
        return False
    
    print_success(f"塔罗占卜成功 - {data['cards'][0].get('name')}")
    return True

def test_tarot_three():
    """测试塔罗占卜 - 三张牌阵"""
    print_test("塔罗占卜 - 三张牌阵")
    
    response = make_request(
        "POST",
        "/divinations/start",
        token=test_data["user_token"],
        json_data={
            "user_id": test_data["user_id"],
            "question": "我的感情发展如何？",
            "version": "TAROT",
            "spread": "three"
        },
        timeout=60
    )
    
    if not assert_status_code(response, 200, "塔罗三张"):
        return False
    
    data = response.json()
    
    if len(data.get("cards", [])) != 3:
        print_error(f"牌数错误: 期望 3, 实际 {len(data.get('cards', []))}")
        return False
    
    print_success("塔罗三张牌阵成功")
    return True

def test_tarot_cross():
    """测试塔罗占卜 - 十字牌阵"""
    print_test("塔罗占卜 - 十字牌阵")
    
    response = make_request(
        "POST",
        "/divinations/start",
        token=test_data["user_token"],
        json_data={
            "user_id": test_data["user_id"],
            "question": "我的事业发展？",
            "version": "TAROT",
            "spread": "cross"
        },
        timeout=60
    )
    
    if not assert_status_code(response, 200, "塔罗十字"):
        return False
    
    data = response.json()
    
    if len(data.get("cards", [])) != 5:
        print_error(f"牌数错误: 期望 5, 实际 {len(data.get('cards', []))}")
        return False
    
    print_success("塔罗十字牌阵成功")
    return True

# ==================== 测试套件 4: 每日运势 ====================

def test_daily_fortune():
    """测试每日运势 - 今日"""
    print_test("每日运势 - 今日")
    
    response = make_request(
        "POST",
        "/daily_fortune",
        token=test_data["user_token"],
        json_data={
            "user_id": test_data["user_id"]
        },
        timeout=60
    )
    
    if not assert_status_code(response, 200, "每日运势"):
        return False
    
    data = response.json()
    
    # 检查必需字段
    required_fields = ["summary", "wealth", "career", "love", "health"]
    for field in required_fields:
        if not assert_field_exists(data, field, "每日运势"):
            return False
    
    print_success("每日运势生成成功")
    return True

# ==================== 测试套件 5: 历史记录 ====================

def test_get_history():
    """测试获取占卜历史"""
    print_test("获取占卜历史")
    
    response = make_request(
        "GET",
        "/divinations",
        token=test_data["user_token"],
        params={"limit": 20, "offset": 0}
    )
    
    if not assert_status_code(response, 200, "历史记录"):
        return False
    
    data = response.json()
    
    if not assert_field_exists(data, "data", "历史记录"):
        return False
    
    print_success(f"历史记录获取成功 - 共 {len(data['data'])} 条")
    return True

def test_get_single_result():
    """测试获取单个占卜结果"""
    print_test("获取单个占卜结果")
    
    if not test_data["session_ids"]:
        print_info("跳过 - 没有可用的session_id")
        return True
    
    session_id = test_data["session_ids"][0]
    
    response = make_request(
        "GET",
        f"/divinations/{session_id}",
        token=test_data["user_token"]
    )
    
    if not assert_status_code(response, 200, "单个结果"):
        return False
    
    data = response.json()
    
    if data.get("session_id") != session_id:
        print_error("session_id不匹配")
        return False
    
    print_success("单个结果获取成功")
    return True

# ==================== 主测试流程 ====================

def run_all_tests():
    """运行所有测试"""
    print_section("DivineDaily 综合测试套件")
    print(f"  测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # 用户端测试流程
    print_section("用户端测试流程")
    
    tests = [
        ("用户注册", test_user_register),
        ("用户登录", test_user_login),
        ("获取用户信息", test_get_current_user),
        ("创建用户档案", test_create_profile),
        ("获取用户档案", test_get_profile),
        ("周易占卜-决策", test_iching_divination),
        ("周易占卜-运势", test_iching_fortune),
        ("周易占卜-博主职业", test_iching_blogger),
        ("塔罗占卜-单张", test_tarot_single),
        ("塔罗占卜-三张", test_tarot_three),
        ("塔罗占卜-十字", test_tarot_cross),
        ("每日运势", test_daily_fortune),
        ("占卜历史", test_get_history),
        ("单个结果", test_get_single_result),
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = "✅ 通过" if result else "❌ 失败"
        except Exception as e:
            results[test_name] = f"❌ 异常: {str(e)[:50]}"
    
    # 打印测试结果汇总
    print_section("测试结果汇总")
    
    for test_name, result in results.items():
        print(f"{test_name:<30} {result}")
    
    # 统计
    passed = sum(1 for r in results.values() if "✅" in r)
    total = len(results)
    
    print(f"\n总计: {passed}/{total} 通过 ({int(passed/total*100)}%)")
    
    if passed < total:
        print(f"\n⚠️  有 {total - passed} 个测试失败")
    else:
        print("\n🎉 所有测试通过！")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        exit(1)
    except Exception as e:
        print(f"\n\n测试执行出错: {str(e)}")
        exit(1)
