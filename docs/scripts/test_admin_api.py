"""
测试管理后台API实现
验证所有接口是否正确注册
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.api.admin import orders, analytics, admin_users, admin_reviews, audit_logs, admin_products
from app.api import admin as admin_auth
from main import app


def test_admin_routes():
    """测试管理后台路由是否正确注册"""
    print("=" * 80)
    print("管理后台API路由测试")
    print("=" * 80)

    # 获取所有路由
    routes = []
    for route in app.routes:
        if hasattr(route, 'routes'):
            # APIRouter
            for sub_route in route.routes:
                if hasattr(sub_route, 'path') and hasattr(sub_route, 'methods'):
                    for method in sub_route.methods:
                        routes.append({
                            'path': sub_route.path,
                            'method': method,
                            'name': sub_route.name
                        })
        elif hasattr(route, 'path') and hasattr(route, 'methods'):
            # 直接路由
            for method in route.methods:
                routes.append({
                    'path': route.path,
                    'method': method,
                    'name': route.name
                })

    # 筛选管理后台相关的路由
    admin_routes = [r for r in routes if '/admin/' in r['path']]

    print(f"\n找到 {len(admin_routes)} 个管理后台API端点:\n")

    # 按功能分组
    categories = {
        '认证': [],
        '订单管理': [],
        '统计分析': [],
        '用户管理': [],
        '评价管理': [],
        '审计日志': [],
        '商品管理': []
    }

    for route in sorted(admin_routes, key=lambda x: x['path']):
        path = route['path']
        method = route['method']

        if '/admin/auth' in path:
            categories['认证'].append(route)
        elif '/admin/orders' in path:
            categories['订单管理'].append(route)
        elif '/admin/analytics' in path:
            categories['统计分析'].append(route)
        elif '/admin/users' in path:
            categories['用户管理'].append(route)
        elif '/admin/reviews' in path:
            categories['评价管理'].append(route)
        elif '/admin/audit-logs' in path:
            categories['审计日志'].append(route)
        elif '/admin/products' in path:
            categories['商品管理'].append(route)

    # 打印分组的路由
    for category, routes_list in categories.items():
        if routes_list:
            print(f"\n【{category}】({len(routes_list)} 个端点)")
            print("-" * 80)
            for route in routes_list:
                print(f"  {method:6} {route['path']}")

    # 验证关键端点
    print("\n" + "=" * 80)
    print("关键端点验证")
    print("=" * 80)

    required_endpoints = [
        ('POST', '/api/v1/admin/auth/login', '管理员登录'),
        ('POST', '/api/v1/admin/auth/logout', '管理员登出'),
        ('POST', '/api/v1/admin/auth/refresh', '刷新Token'),
        ('GET', '/api/v1/admin/auth/me', '获取当前管理员信息'),
        ('GET', '/api/v1/admin/orders', '全局订单列表'),
        ('GET', '/api/v1/admin/orders/{order_id}', '订单详情'),
        ('PUT', '/api/v1/admin/orders/{order_id}/status', '更新订单状态'),
        ('GET', '/api/v1/admin/orders/export/csv', '导出订单CSV'),
        ('GET', '/api/v1/admin/analytics/today', '今日统计'),
        ('GET', '/api/v1/admin/analytics/trend', '趋势分析'),
        ('GET', '/api/v1/admin/analytics/hot-products', '热销商品'),
        ('GET', '/api/v1/admin/users', '用户列表'),
        ('GET', '/api/v1/admin/users/{user_id}', '用户详情'),
        ('PUT', '/api/v1/admin/users/{user_id}/status', '更新用户状态'),
        ('GET', '/api/v1/admin/reviews', '评价列表'),
        ('DELETE', '/api/v1/admin/reviews/{review_id}', '删除评价'),
        ('POST', '/api/v1/admin/reviews/{review_id}/reply', '回复评价'),
        ('GET', '/api/v1/admin/audit-logs', '审计日志'),
        ('PUT', '/api/v1/admin/products/{product_id}/stock', '调整库存'),
        ('POST', '/api/v1/admin/products/batch', '批量操作'),
    ]

    all_found = True
    for method, path, description in required_endpoints:
        found = any(r['method'] == method and r['path'] == path for r in admin_routes)
        status = "✓" if found else "✗"
        print(f"  {status} {method:6} {path:50} {description}")
        if not found:
            all_found = False

    print("\n" + "=" * 80)
    if all_found:
        print("✓ 所有关键端点已正确注册!")
    else:
        print("✗ 部分关键端点未找到,请检查实现")
    print("=" * 80)

    return all_found


if __name__ == "__main__":
    success = test_admin_routes()
    sys.exit(0 if success else 1)
