"""
重启服务后必须测试的用例
这些测试用例用于验证服务重启后核心功能是否正常
"""

import requests
import json

# 基础配置
BASE_URL = "http://8.148.26.166:40081"
API_BASE = f"{BASE_URL}/api/v1"

def get_token():
    """获取认证 token"""
    response = requests.post(
        f"{API_BASE}/auth/login",
        json={
            "username": "admin@163.com",
            "password": "594120"
        },
        verify=False
    )
    if response.status_code == 200:
        return response.json()['token']
    else:
        raise Exception(f"登录失败: {response.status_code} - {response.text}")

def test_login():
    """测试用例 1: 用户登录"""
    print("测试 1: 用户登录...")
    try:
        response = requests.post(
            f"{API_BASE}/auth/login",
            json={
                "username": "admin@163.com",
                "password": "594120"
            },
            verify=False
        )
        assert response.status_code == 200, f"登录失败: {response.status_code}"
        data = response.json()
        assert 'token' in data, "响应中缺少 token"
        assert 'user' in data, "响应中缺少 user"
        assert data['user']['role'] == 'admin', "用户角色不正确"
        print("✅ 登录测试通过")
        return True
    except Exception as e:
        print(f"❌ 登录测试失败: {e}")
        return False

def test_llm_config_list():
    """测试用例 2: 获取 LLM 配置列表"""
    print("\n测试 2: 获取 LLM 配置列表...")
    try:
        token = get_token()
        response = requests.get(
            f"{API_BASE}/configs/llm",
            headers={"Authorization": f"Bearer {token}"},
            verify=False
        )
        assert response.status_code == 200, f"获取配置失败: {response.status_code}"
        data = response.json()
        assert 'data' in data, "响应中缺少 data"
        assert isinstance(data['data'], list), "data 应该是列表"
        print(f"✅ LLM 配置列表测试通过 (共 {len(data['data'])} 个配置)")
        return True
    except Exception as e:
        print(f"❌ LLM 配置列表测试失败: {e}")
        return False

def test_assistant_config_list():
    """测试用例 3: 获取 Assistant 配置列表"""
    print("\n测试 3: 获取 Assistant 配置列表...")
    try:
        token = get_token()
        response = requests.get(
            f"{API_BASE}/configs/assistant",
            headers={"Authorization": f"Bearer {token}"},
            verify=False
        )
        assert response.status_code == 200, f"获取配置失败: {response.status_code}"
        data = response.json()
        assert 'data' in data, "响应中缺少 data"
        assert isinstance(data['data'], list), "data 应该是列表"
        print(f"✅ Assistant 配置列表测试通过 (共 {len(data['data'])} 个配置)")
        return True
    except Exception as e:
        print(f"❌ Assistant 配置列表测试失败: {e}")
        return False

def test_llm_test_api():
    """测试用例 4: LLM 测试接口"""
    print("\n测试 4: LLM 测试接口...")
    try:
        token = get_token()
        response = requests.post(
            f"{API_BASE}/configs/llm/3/test",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "message": "你好，请用一句话介绍你自己",
                "mode": "block"
            },
            verify=False
        )
        assert response.status_code == 200, f"测试接口失败: {response.status_code}"
        data = response.json()
        assert 'success' in data, "响应中缺少 success"
        assert 'request' in data, "响应中缺少 request"
        assert data['request']['user_message'] == "你好，请用一句话介绍你自己", "消息不匹配"
        print(f"✅ LLM 测试接口通过 (success={data['success']})")
        return True
    except Exception as e:
        print(f"❌ LLM 测试接口失败: {e}")
        return False

def test_assistant_test_cases():
    """测试用例 5: 获取 Assistant 测试用例"""
    print("\n测试 5: 获取 Assistant 测试用例...")
    try:
        token = get_token()
        response = requests.get(
            f"{API_BASE}/configs/assistant/test-cases",
            headers={"Authorization": f"Bearer {token}"},
            verify=False
        )
        assert response.status_code == 200, f"获取测试用例失败: {response.status_code}"
        data = response.json()
        assert 'data' in data, "响应中缺少 data"
        assert 'count' in data, "响应中缺少 count"
        print(f"✅ Assistant 测试用例获取通过 (共 {data['count']} 个用例)")
        return True
    except Exception as e:
        print(f"❌ Assistant 测试用例获取失败: {e}")
        return False

def test_assistant_test_api():
    """测试用例 6: Assistant 测试接口"""
    print("\n测试 6: Assistant 测试接口...")
    try:
        token = get_token()
        response = requests.post(
            f"{API_BASE}/configs/assistant/2/test",
            headers={"Authorization": f"Bearer {token}"},
            verify=False
        )
        assert response.status_code == 200, f"测试接口失败: {response.status_code}"
        data = response.json()
        assert 'success' in data, "响应中缺少 success"
        assert 'test_case' in data, "响应中缺少 test_case"
        assert 'rendered_prompt' in data, "响应中缺少 rendered_prompt"
        print(f"✅ Assistant 测试接口通过 (success={data['success']})")
        return True
    except Exception as e:
        print(f"❌ Assistant 测试接口失败: {e}")
        return False

def test_divination_start():
    """测试用例 7: 占卜开始接口"""
    print("\n测试 7: 占卜开始接口...")
    try:
        token = get_token()
        response = requests.post(
            f"{API_BASE}/divinations/start",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "user_id": "6",
                "question": "我今年的官运如何",
                "version": "CN",
                "orientation": "E"
            },
            verify=False,
            timeout=30
        )
        assert response.status_code == 200, f"占卜开始失败: {response.status_code} - {response.text}"
        data = response.json()
        assert 'session_id' in data, "响应中缺少 session_id"
        assert 'summary' in data, "响应中缺少 summary"
        assert 'detail' in data, "响应中缺少 detail"
        print(f"✅ 占卜开始接口通过 (session_id={data['session_id'][:8]}...)")
        print(f"   摘要: {data['summary'][:50]}...")
        return True
    except Exception as e:
        print(f"❌ 占卜开始接口失败: {e}")
        return False

def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("开始运行重启后测试用例")
    print("=" * 60)
    
    results = []
    results.append(("用户登录", test_login()))
    results.append(("LLM 配置列表", test_llm_config_list()))
    results.append(("Assistant 配置列表", test_assistant_config_list()))
    results.append(("LLM 测试接口", test_llm_test_api()))
    results.append(("Assistant 测试用例", test_assistant_test_cases()))
    results.append(("Assistant 测试接口", test_assistant_test_api()))
    results.append(("占卜开始接口", test_divination_start()))
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
    
    print(f"\n总计: {passed}/{total} 通过")
    print("=" * 60)
    
    return passed == total

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    success = run_all_tests()
    exit(0 if success else 1)
