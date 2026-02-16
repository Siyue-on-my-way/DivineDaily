"""
DivineDaily 管理端测试套件
测试管理员配置管理功能
"""

import requests
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime

# ==================== 配置 ====================

BASE_URL = "http://8.148.26.166:48080"
API_BASE = f"{BASE_URL}/api/v1"

# 管理员账号
ADMIN_USERNAME = "admin@163.com"
ADMIN_PASSWORD = "594120"

# 全局变量
test_data = {
    "admin_token": None,
    "test_llm_config_id": None,
    "test_assistant_config_id": None,
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
        print_error(f"响应: {response.text[:200]}")
        return False
    return True

def assert_field_exists(data: Dict, field: str, test_name: str):
    if field not in data:
        print_error(f"{test_name} - 缺少字段: {field}")
        return False
    return True

# ==================== 管理员认证 ====================

def test_admin_login():
    """测试管理员登录"""
    print_test("管理员登录")
    
    response = make_request(
        "POST",
        "/auth/login",
        json_data={
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        }
    )
    
    if not assert_status_code(response, 200, "管理员登录"):
        return False
    
    data = response.json()
    
    if data.get("user", {}).get("role") != "admin":
        print_error("用户角色不是管理员")
        return False
    
    test_data["admin_token"] = data["token"]
    print_success("管理员登录成功")
    return True

# ==================== LLM 配置管理 ====================

def test_get_llm_configs():
    """测试获取LLM配置列表"""
    print_test("获取LLM配置列表")
    
    response = make_request(
        "GET",
        "/configs/llm",
        token=test_data["admin_token"]
    )
    
    if not assert_status_code(response, 200, "获取LLM配置"):
        return False
    
    data = response.json()
    
    if not assert_field_exists(data, "data", "获取LLM配置"):
        return False
    
    configs = data.get("data", [])
    print_success(f"获取成功 - 共 {len(configs)} 个配置")
    
    # 打印配置信息
    for config in configs[:3]:
        print_info(f"  - {config.get('name')} ({config.get('provider')}/{config.get('model')})")
    
    return True

def test_create_llm_config():
    """测试创建LLM配置"""
    print_test("创建LLM配置")
    
    config_name = f"测试LLM_{int(time.time())}"
    
    response = make_request(
        "POST",
        "/configs/llm",
        token=test_data["admin_token"],
        json_data={
            "name": config_name,
            "provider": "openai",
            "url_type": "openai_compatible",
            "api_key": "sk-test-key",
            "endpoint": "https://api.openai.com/v1/chat/completions",
            "model_name": "gpt-3.5-turbo",
            "is_default": False,
            "is_enabled": True,
            "description": "自动化测试创建的配置",
            "temperature": 0.7,
            "max_tokens": 2000,
            "timeout": 30
        }
    )
    
    if not assert_status_code(response, 200, "创建LLM配置"):
        return False
    
    data = response.json()
    
    if not assert_field_exists(data, "data", "创建LLM配置"):
        return False
    
    test_data["test_llm_config_id"] = data["data"]["id"]
    print_success(f"创建成功 - ID: {test_data['test_llm_config_id']}, 名称: {config_name}")
    
    return True

def test_update_llm_config():
    """测试更新LLM配置"""
    print_test("更新LLM配置")
    
    if not test_data["test_llm_config_id"]:
        print_info("跳过 - 没有可用的配置ID")
        return True
    
    response = make_request(
        "PUT",
        f"/configs/llm/{test_data['test_llm_config_id']}",
        token=test_data["admin_token"],
        json_data={
            "description": "已更新的描述",
            "temperature": 0.8
        }
    )
    
    if not assert_status_code(response, 200, "更新LLM配置"):
        return False
    
    print_success("更新成功")
    return True

def test_llm_config_test():
    """测试LLM配置测试接口"""
    print_test("测试LLM配置")
    
    # 使用已存在的配置ID（假设ID=3存在）
    config_id = 3
    
    response = make_request(
        "POST",
        f"/configs/llm/{config_id}/test",
        token=test_data["admin_token"],
        json_data={
            "message": "你好，请用一句话介绍你自己",
            "mode": "block"
        },
        timeout=60
    )
    
    if not assert_status_code(response, 200, "测试LLM"):
        return False
    
    data = response.json()
    
    if not assert_field_exists(data, "success", "测试LLM"):
        return False
    
    if data.get("success"):
        print_success("LLM测试成功")
        print_info(f"响应: {data.get('response', '')[:100]}...")
    else:
        print_error(f"LLM测试失败: {data.get('error', '')}")
        return False
    
    return True

def test_delete_llm_config():
    """测试删除LLM配置"""
    print_test("删除LLM配置")
    
    if not test_data["test_llm_config_id"]:
        print_info("跳过 - 没有可用的配置ID")
        return True
    
    response = make_request(
        "DELETE",
        f"/configs/llm/{test_data['test_llm_config_id']}",
        token=test_data["admin_token"]
    )
    
    if not assert_status_code(response, 200, "删除LLM配置"):
        return False
    
    print_success("删除成功")
    return True

# ==================== Assistant 配置管理 ====================

def test_get_assistant_configs():
    """测试获取Assistant配置列表"""
    print_test("获取Assistant配置列表")
    
    response = make_request(
        "GET",
        "/configs/assistant",
        token=test_data["admin_token"]
    )
    
    if not assert_status_code(response, 200, "获取Assistant配置"):
        return False
    
    data = response.json()
    
    if not assert_field_exists(data, "data", "获取Assistant配置"):
        return False
    
    configs = data.get("data", [])
    print_success(f"获取成功 - 共 {len(configs)} 个配置")
    
    for config in configs[:3]:
        print_info(f"  - {config.get('name')} ({config.get('scene')}/{config.get('prompt_type')})")
    
    return True

def test_create_assistant_config():
    """测试创建Assistant配置"""
    print_test("创建Assistant配置")
    
    config_name = f"测试Assistant_{int(time.time())}"
    
    response = make_request(
        "POST",
        "/configs/assistant",
        token=test_data["admin_token"],
        json_data={
            "name": config_name,
            "scene": "divination",
            "prompt_type": "answer",
            "question_type": "decision",
            "template": "你是一位专业的占卜师。\n\n用户问题：{{.question}}\n卦象：{{.hexagram}}\n\n请给出专业的解读。",
            "llm_config_id": 1,
            "variables": [
                {"name": "question", "type": "string"},
                {"name": "hexagram", "type": "string"}
            ],
            "temperature": 0.7,
            "max_tokens": 2000,
            "timeout_seconds": 30,
            "is_enabled": True,
            "description": "自动化测试创建的配置"
        }
    )
    
    if not assert_status_code(response, 200, "创建Assistant配置"):
        return False
    
    data = response.json()
    
    if not assert_field_exists(data, "data", "创建Assistant配置"):
        return False
    
    test_data["test_assistant_config_id"] = data["data"]["id"]
    print_success(f"创建成功 - ID: {test_data['test_assistant_config_id']}, 名称: {config_name}")
    
    return True

def test_update_assistant_config():
    """测试更新Assistant配置"""
    print_test("更新Assistant配置")
    
    if not test_data["test_assistant_config_id"]:
        print_info("跳过 - 没有可用的配置ID")
        return True
    
    response = make_request(
        "PUT",
        f"/configs/assistant/{test_data['test_assistant_config_id']}",
        token=test_data["admin_token"],
        json_data={
            "description": "已更新的描述",
            "temperature": 0.8
        }
    )
    
    if not assert_status_code(response, 200, "更新Assistant配置"):
        return False
    
    print_success("更新成功")
    return True

def test_get_test_cases():
    """测试获取测试用例"""
    print_test("获取测试用例")
    
    response = make_request(
        "GET",
        "/configs/assistant/test-cases",
        token=test_data["admin_token"]
    )
    
    if not assert_status_code(response, 200, "获取测试用例"):
        return False
    
    data = response.json()
    
    if not assert_field_exists(data, "data", "获取测试用例"):
        return False
    
    count = data.get("count", 0)
    print_success(f"获取成功 - 共 {count} 个测试用例")
    
    return True

def test_assistant_config_test():
    """测试Assistant配置测试接口"""
    print_test("测试Assistant配置")
    
    # 使用已存在的配置ID（假设ID=2存在）
    config_id = 2
    
    response = make_request(
        "POST",
        f"/configs/assistant/{config_id}/test",
        token=test_data["admin_token"],
        timeout=60
    )
    
    if not assert_status_code(response, 200, "测试Assistant"):
        return False
    
    data = response.json()
    
    if not assert_field_exists(data, "success", "测试Assistant"):
        return False
    
    if data.get("success"):
        print_success("Assistant测试成功")
        validation = data.get("validation", {})
        print_info(f"关键词匹配: {validation.get('keyword_match_rate', 'N/A')}")
    else:
        print_error(f"Assistant测试失败: {data.get('error', '')}")
        return False
    
    return True

def test_delete_assistant_config():
    """测试删除Assistant配置"""
    print_test("删除Assistant配置")
    
    if not test_data["test_assistant_config_id"]:
        print_info("跳过 - 没有可用的配置ID")
        return True
    
    response = make_request(
        "DELETE",
        f"/configs/assistant/{test_data['test_assistant_config_id']}",
        token=test_data["admin_token"]
    )
    
    if not assert_status_code(response, 200, "删除Assistant配置"):
        return False
    
    print_success("删除成功")
    return True

# ==================== 主测试流程 ====================

def run_admin_flow_tests():
    """运行管理端测试流程"""
    print_section("管理端测试流程")
    
    results = []
    
    # 认证测试
    results.append(("管理员登录", test_admin_login()))
    
    # LLM配置测试
    results.append(("获取LLM配置列表", test_get_llm_configs()))
    results.append(("创建LLM配置", test_create_llm_config()))
    results.append(("更新LLM配置", test_update_llm_config()))
    results.append(("测试LLM配置", test_llm_config_test()))
    results.append(("删除LLM配置", test_delete_llm_config()))
    
    # Assistant配置测试
    results.append(("获取Assistant配置列表", test_get_assistant_configs()))
    results.append(("创建Assistant配置", test_create_assistant_config()))
    results.append(("更新Assistant配置", test_update_assistant_config()))
    results.append(("获取测试用例", test_get_test_cases()))
    results.append(("测试Assistant配置", test_assistant_config_test()))
    results.append(("删除Assistant配置", test_delete_assistant_config()))
    
    return results

def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("  DivineDaily 管理端测试套件")
    print("  测试时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 80)
    
    # 禁用SSL警告
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # 运行测试
    results = run_admin_flow_tests()
    
    # 打印汇总
    print_section("测试结果汇总")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name:30s} {status}")
    
    print(f"\n总计: {passed}/{total} 通过 ({passed*100//total}%)")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败")
        return 1

if __name__ == "__main__":
    exit(main())

