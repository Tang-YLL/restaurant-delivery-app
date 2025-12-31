"""
Locust性能测试脚本
测试餐厅管理系统的API性能
"""
from locust import HttpUser, task, between, events
from locust.runners import MasterRunner
import json
import random


class RestaurantUser(HttpUser):
    """餐厅系统用户模拟"""

    # 等待时间: 1-3秒
    wait_time = between(1, 3)

    def on_start(self):
        """用户开始时的初始化"""
        # 注册/登录获取token
        self.login()
        # 获取商品列表
        self.get_products()

    def login(self):
        """登录获取token"""
        # 使用测试账号
        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "phone": "13800138000",
                "password": "test123456"
            }
        )

        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token", "")
        else:
            # 如果登录失败,尝试注册
            register_response = self.client.post(
                "/api/v1/auth/register",
                json={
                    "phone": f"138{random.randint(10000000, 99999999)}",
                    "password": "test123456",
                    "nickname": f"测试用户{random.randint(1, 1000)}"
                }
            )
            if register_response.status_code in [200, 201]:
                # 重新登录
                response = self.client.post(
                    "/api/v1/auth/login",
                    json={
                        "phone": register_response.json()["phone"],
                        "password": "test123456"
                    }
                )
                if response.status_code == 200:
                    self.token = response.json().get("access_token", "")
                else:
                    self.token = ""
            else:
                self.token = ""

    def get_headers(self):
        """获取请求头"""
        if hasattr(self, 'token') and self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}

    @task(10)
    def view_products(self):
        """查看商品列表(高频操作)"""
        self.client.get("/api/v1/products")

    @task(8)
    def view_hot_products(self):
        """查看热门商品(高频操作)"""
        self.client.get("/api/v1/products/hot")

    @task(5)
    def view_categories(self):
        """查看分类(中频操作)"""
        self.client.get("/api/v1/categories")

    @task(7)
    def view_product_detail(self):
        """查看商品详情(高频操作)"""
        product_id = random.randint(1, 10)
        self.client.get(f"/api/v1/products/{product_id}")

    @task(4)
    def add_to_cart(self):
        """添加商品到购物车(中频操作)"""
        product_id = random.randint(1, 10)
        quantity = random.randint(1, 5)
        self.client.post(
            "/api/v1/cart",
            json={
                "product_id": product_id,
                "quantity": quantity
            },
            headers=self.get_headers()
        )

    @task(3)
    def view_cart(self):
        """查看购物车(中频操作)"""
        self.client.get(
            "/api/v1/cart",
            headers=self.get_headers()
        )

    @task(2)
    def create_order(self):
        """创建订单(低频操作)"""
        # 随机选择配送方式
        delivery_type = random.choice(["pickup", "delivery"])

        if delivery_type == "pickup":
            order_data = {
                "delivery_type": "pickup",
                "pickup_name": f"测试用户{random.randint(1, 100)}",
                "pickup_phone": f"138{random.randint(10000000, 99999999)}"
            }
        else:
            order_data = {
                "delivery_type": "delivery",
                "delivery_address": f"测试地址{random.randint(1, 100)}号",
                "delivery_phone": f"138{random.randint(10000000, 99999999)}",
                "delivery_name": f"测试用户{random.randint(1, 100)}"
            }

        self.client.post(
            "/api/v1/orders",
            json=order_data,
            headers=self.get_headers()
        )

    @task(3)
    def view_my_orders(self):
        """查看我的订单(中频操作)"""
        self.client.get(
            "/api/v1/orders/my",
            headers=self.get_headers()
        )

    @task(1)
    def view_order_detail(self):
        """查看订单详情(低频操作)"""
        order_id = random.randint(1, 20)
        self.client.get(
            f"/api/v1/orders/{order_id}",
            headers=self.get_headers()
        )

    @task(2)
    def view_product_reviews(self):
        """查看商品评价(中频操作)"""
        product_id = random.randint(1, 10)
        self.client.get(f"/api/v1/reviews/product/{product_id}")

    @task(1)
    def create_review(self):
        """创建评价(低频操作)"""
        ratings = [5, 4, 5, 3, 5, 4, 5]
        contents = [
            "非常好!",
            "质量不错",
            "推荐购买",
            "性价比高",
            "很好吃",
            "服务态度好",
            "会再次购买"
        ]

        self.client.post(
            "/api/v1/reviews",
            json={
                "order_id": random.randint(1, 10),
                "product_id": random.randint(1, 10),
                "rating": random.choice(ratings),
                "content": random.choice(contents)
            },
            headers=self.get_headers()
        )


class AdminUser(HttpUser):
    """管理员用户模拟"""

    wait_time = between(2, 5)

    def on_start(self):
        """管理员登录"""
        # 这里需要使用管理员账号
        response = self.client.post(
            "/api/v1/admin/auth/login",
            json={
                "username": "admin",
                "password": "admin123"
            }
        )

        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token", "")
        else:
            self.token = ""

    def get_headers(self):
        """获取请求头"""
        if hasattr(self, 'token') and self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}

    @task(5)
    def view_dashboard_stats(self):
        """查看仪表盘统计"""
        self.client.get(
            "/api/v1/admin/analytics/dashboard",
            headers=self.get_headers()
        )

    @task(4)
    def view_all_orders(self):
        """查看所有订单"""
        self.client.get(
            "/api/v1/admin/orders",
            headers=self.get_headers()
        )

    @task(3)
    def view_all_users(self):
        """查看所有用户"""
        self.client.get(
            "/api/v1/admin/users",
            headers=self.get_headers()
        )

    @task(3)
    def view_sales_stats(self):
        """查看销售统计"""
        self.client.get(
            "/api/v1/admin/analytics/sales",
            headers=self.get_headers()
        )

    @task(2)
    def update_order_status(self):
        """更新订单状态"""
        order_id = random.randint(1, 20)
        statuses = ["confirmed", "preparing", "ready", "completed", "cancelled"]
        self.client.patch(
            f"/api/v1/admin/orders/{order_id}/status",
            json={"status": random.choice(statuses)},
            headers=self.get_headers()
        )

    @task(1)
    def view_audit_logs(self):
        """查看审计日志"""
        self.client.get(
            "/api/v1/admin/audit-logs",
            headers=self.get_headers()
        )


# 性能测试事件监听器
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """请求事件监听"""
    if exception:
        print(f"请求失败: {name} - {exception}")
    elif response_time > 1000:  # 响应时间超过1秒
        print(f"慢请求警告: {name} - {response_time}ms")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """测试结束事件"""
    if isinstance(environment.runner, MasterRunner):
        print("测试完成,生成报告...")
    else:
        print("测试完成!")
