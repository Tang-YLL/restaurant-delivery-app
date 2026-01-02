"""
商品详情内容分区API测试脚本

使用方法:
1. 确保后端服务运行在 http://localhost:8000
2. 确保已有管理员账号和测试商品
3. 修改下方的 BASE_URL, ADMIN_USERNAME, ADMIN_PASSWORD
4. 运行: python test_api_content_sections.py
"""
import requests
import json
from typing import Optional

# ==================== 配置 ====================
BASE_URL = "http://localhost:8000"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# 全局变量
access_token: Optional[str] = None
test_product_id: Optional[int] = None
test_section_id: Optional[int] = None


def print_section(title: str):
    """打印分节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_response(response: requests.Response, show_data: bool = True):
    """打印响应信息"""
    print(f"状态码: {response.status_code}")
    if show_data and response.text:
        try:
            print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        except:
            print(f"响应: {response.text}")


def login_admin():
    """管理员登录获取token"""
    global access_token

    print_section("1. 管理员登录")

    url = f"{BASE_URL}/admin/auth/login"
    data = {
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD
    }

    response = requests.post(url, json=data)
    print_response(response)

    if response.status_code == 200:
        result = response.json()
        access_token = result.get("access_token")
        print(f"\n✅ 登录成功，获取token: {access_token[:50]}...")
        return True
    else:
        print(f"\n❌ 登录失败")
        return False


def get_headers():
    """获取认证头"""
    if not access_token:
        raise Exception("未登录，请先调用 login_admin()")

    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }


def get_test_product():
    """获取第一个测试商品ID"""
    global test_product_id

    print_section("2. 获取测试商品ID")

    url = f"{BASE_URL}/admin/products"
    headers = get_headers()

    response = requests.get(url, headers=headers)
    print_response(response, show_data=False)

    if response.status_code == 200:
        result = response.json()
        if result.get("list") and len(result["list"]) > 0:
            test_product_id = result["list"][0]["id"]
            print(f"\n✅ 获取到测试商品ID: {test_product_id}")
            print(f"   商品名称: {result['list'][0]['title']}")
            return True
        else:
            print(f"\n❌ 没有找到测试商品")
            return False
    else:
        print(f"\n❌ 获取商品列表失败")
        return False


def create_content_section():
    """创建内容分区"""
    global test_section_id

    print_section("3. 创建内容分区")

    url = f"{BASE_URL}/admin/products/{test_product_id}/details/sections"
    headers = get_headers()

    # 测试XSS防护
    test_content = """
    <h2>品牌故事</h2>
    <p>这是一个测试内容。</p>
    <p><strong>重要:</strong> <script>alert('XSS攻击')</script> 这段脚本应该被过滤</p>
    <ul>
        <li>第一点</li>
        <li>第二点</li>
    </ul>
    """

    data = {
        "section_type": "story",
        "title": "品牌故事",
        "content": test_content,
        "display_order": 1
    }

    print("测试XSS防护：输入包含 <script> 标签的内容")
    response = requests.post(url, headers=headers, json=data)
    print_response(response)

    if response.status_code == 201:
        result = response.json()
        test_section_id = result.get("id")
        print(f"\n✅ 创建成功，分区ID: {test_section_id}")
        print(f"   内容是否被过滤: {'<script>' not in result.get('content', '')}")

        # 显示过滤后的内容
        filtered_content = result.get("content", "")
        if "<script>" not in filtered_content:
            print(f"   ✅ XSS防护成功！脚本标签已被移除")
            print(f"   过滤后内容: {filtered_content[:200]}...")

        return True
    else:
        print(f"\n❌ 创建失败")
        return False


def get_product_details():
    """获取商品完整详情"""
    print_section("4. 获取商品完整详情")

    url = f"{BASE_URL}/admin/products/{test_product_id}/details"
    headers = get_headers()

    response = requests.get(url, headers=headers)
    print_response(response)

    if response.status_code == 200:
        result = response.json()
        sections_count = len(result.get("content_sections", []))
        print(f"\n✅ 获取成功，共有 {sections_count} 个内容分区")
        return True
    else:
        print(f"\n❌ 获取失败")
        return False


def update_content_section():
    """更新内容分区"""
    print_section("5. 更新内容分区")

    url = f"{BASE_URL}/admin/products/{test_product_id}/details/sections/{test_section_id}"
    headers = get_headers()

    data = {
        "title": "品牌故事（已更新）",
        "content": "<h2>更新后的品牌故事</h2><p>这是更新后的内容。</p>"
    }

    response = requests.put(url, headers=headers, json=data)
    print_response(response)

    if response.status_code == 200:
        print(f"\n✅ 更新成功")
        return True
    else:
        print(f"\n❌ 更新失败")
        return False


def batch_update_sections():
    """批量更新内容分区"""
    print_section("6. 批量更新内容分区")

    url = f"{BASE_URL}/admin/products/{test_product_id}/details/sections/batch"
    headers = get_headers()

    data = [
        {
            "section_type": "story",
            "title": "品牌故事",
            "content": "<h2>品牌故事</h2><p>这是我们品牌的故事...</p>",
            "display_order": 1
        },
        {
            "section_type": "nutrition",
            "title": "营养成分",
            "content": "<h2>营养成分表</h2><p>详细营养成分信息...</p>",
            "display_order": 2
        },
        {
            "section_type": "ingredients",
            "title": "食材介绍",
            "content": "<h2>食材介绍</h2><p>精选优质食材...</p>",
            "display_order": 3
        }
    ]

    response = requests.put(url, headers=headers, json=data)
    print_response(response, show_data=False)

    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ 批量更新成功")
        print(f"   消息: {result.get('message')}")
        print(f"   创建分区数: {len(result.get('data', []))}")
        return True
    else:
        print(f"\n❌ 批量更新失败")
        return False


def test_user_api():
    """测试用户端API（无需认证）"""
    print_section("7. 测试用户端API（无需认证）")

    url = f"{BASE_URL}/products/{test_product_id}/full-details"

    response = requests.get(url)
    print_response(response, show_data=False)

    if response.status_code == 200:
        result = response.json()
        sections_count = len(result.get("content_sections", []))
        has_nutrition = result.get("nutrition_facts") is not None
        print(f"\n✅ 用户端API访问成功")
        print(f"   内容分区数: {sections_count}")
        print(f"   包含营养数据: {has_nutrition}")
        return True
    else:
        print(f"\n❌ 用户端API访问失败")
        return False


def delete_content_section():
    """删除内容分区"""
    print_section("8. 删除内容分区")

    url = f"{BASE_URL}/admin/products/{test_product_id}/details/sections/{test_section_id}"
    headers = get_headers()

    response = requests.delete(url, headers=headers)
    print_response(response)

    if response.status_code == 200:
        print(f"\n✅ 删除成功")
        return True
    else:
        print(f"\n❌ 删除失败")
        return False


def test_xss_protection():
    """专门测试XSS防护"""
    print_section("9. 专项XSS防护测试")

    url = f"{BASE_URL}/admin/products/{test_product_id}/details/sections"
    headers = get_headers()

    # 各种XSS攻击向量
    xss_tests = [
        ("<script>alert('XSS')</script>", "基础脚本标签"),
        ("<img src=x onerror=alert('XSS')>", "图片onerror事件"),
        ("<svg onload=alert('XSS')>", "SVG onload事件"),
        ("<iframe src='javascript:alert(XSS)'></iframe>", "iframe javascript"),
        ("<a href='javascript:alert(XSS)'>点击</a>", "链接javascript"),
    ]

    print("\n测试各种XSS攻击向量：\n")

    all_passed = True
    for xss_payload, description in xss_tests:
        data = {
            "section_type": "test",
            "content": xss_payload,
            "display_order": 99
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 201:
            result = response.json()
            content = result.get("content", "")

            # 检查是否过滤了危险内容
            is_safe = (
                "<script>" not in content and
                "onerror=" not in content and
                "onload=" not in content and
                "javascript:" not in content
            )

            status = "✅ 通过" if is_safe else "❌ 失败"
            print(f"{status} - {description}: {xss_payload}")

            if not is_safe:
                all_passed = False
                print(f"   过滤后内容: {content}")
        else:
            print(f"❌ 失败 - {description}: 请求失败")
            all_passed = False

    if all_passed:
        print(f"\n✅ 所有XSS防护测试通过！")
    else:
        print(f"\n❌ 部分XSS防护测试失败！")

    return all_passed


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("  商品详情内容分区API测试")
    print("=" * 60)

    # 执行测试流程
    tests = [
        ("管理员登录", login_admin),
        ("获取测试商品", get_test_product),
        ("创建内容分区", create_content_section),
        ("获取商品详情", get_product_details),
        ("更新内容分区", update_content_section),
        ("批量更新分区", batch_update_sections),
        ("测试用户端API", test_user_api),
        ("XSS防护测试", test_xss_protection),
        ("删除内容分区", delete_content_section),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ {test_name} 发生异常: {str(e)}")
            results.append((test_name, False))

    # 打印测试总结
    print_section("测试总结")
    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{status} - {test_name}")

    print(f"\n总计: {passed}/{total} 测试通过")
    print("=" * 60)

    if passed == total:
        print("\n🎉 所有测试通过！API实现正确！")
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败，请检查实现")


if __name__ == "__main__":
    main()
