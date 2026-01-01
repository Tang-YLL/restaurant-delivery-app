"""
Service层 - 业务逻辑层
负责处理业务逻辑,调用Repository层
"""
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from datetime import datetime, timedelta
from decimal import Decimal
import secrets
import json
import csv
import io

from app.models import User, Admin, Product, Category, Order, CartItem, Review, AdminLog, OrderItem
from app.repositories import (
    UserRepository, AdminRepository, ProductRepository, CategoryRepository,
    CartRepository, OrderRepository, ReviewRepository,
    BaseRepository
)
from app.core.security import (
    verify_password, get_password_hash,
    create_user_access_token, create_admin_access_token
)
from app.core.redis_client import redis_client
from app.core.config import get_settings

settings = get_settings()


# ==================== 用户认证Service ====================
class AuthService:
    """认证服务"""

    @staticmethod
    def get_user_repo(db: AsyncSession) -> UserRepository:
        """获取用户Repository"""
        return UserRepository(User, db)

    @staticmethod
    def get_admin_repo(db: AsyncSession) -> AdminRepository:
        """获取管理员Repository"""
        return AdminRepository(Admin, db)

    async def register(
        self,
        phone: str,
        password: str,
        nickname: Optional[str] = None,
        db: AsyncSession = None
    ) -> User:
        """用户注册"""
        user_repo = self.get_user_repo(db)

        # 检查手机号是否已存在
        existing_user = await user_repo.get_by_phone(phone)
        if existing_user:
            raise ValueError("手机号已注册")

        # 创建用户
        password_hash = get_password_hash(password)
        user = await user_repo.create_user(
            phone=phone,
            password_hash=password_hash,
            nickname=nickname or f"用户{phone[-4:]}"
        )
        return user

    async def login(
        self,
        phone: str,
        password: str,
        db: AsyncSession = None
    ) -> Tuple[User, str, str]:
        """用户登录"""
        user_repo = self.get_user_repo(db)

        # 查找用户
        user = await user_repo.get_by_phone(phone)
        if not user:
            raise ValueError("手机号或密码错误")

        # 验证密码
        if not verify_password(password, user.password_hash):
            raise ValueError("手机号或密码错误")

        # 检查用户状态
        if not user.is_active:
            raise ValueError("用户已被禁用")

        # 生成token
        access_token, refresh_token = create_user_access_token(user.id)

        # 缓存用户信息
        await redis_client.set_json(
            f"user:info:{user.id}",
            {"id": user.id, "phone": user.phone, "nickname": user.nickname},
            expire=3600
        )

        return user, access_token, refresh_token

    async def admin_login(
        self,
        username: str,
        password: str,
        db: AsyncSession = None
    ) -> Tuple[Admin, str, str]:
        """管理员登录"""
        admin_repo = self.get_admin_repo(db)

        # 查找管理员
        admin = await admin_repo.get_by_username(username)
        if not admin:
            raise ValueError("用户名或密码错误")

        # 验证密码
        if not verify_password(password, admin.password_hash):
            raise ValueError("用户名或密码错误")

        # 检查管理员状态
        if not admin.is_active:
            raise ValueError("管理员已被禁用")

        # 生成token
        access_token, refresh_token = create_admin_access_token(admin.id)

        return admin, access_token, refresh_token

    async def logout(self, token: str, expire_seconds: int = None) -> bool:
        """用户登出"""
        # 将token加入黑名单
        if expire_seconds:
            return await redis_client.add_to_blacklist(token, expire_seconds)
        return await redis_client.add_to_blacklist(token)

    async def refresh_token(self, refresh_token: str, db: AsyncSession = None) -> Tuple[str, str]:
        """刷新token"""
        from app.core.security import decode_token

        payload = decode_token(refresh_token)
        if not payload:
            raise ValueError("无效的refresh token")

        # 检查token类型
        if payload.get("type") != "refresh":
            raise ValueError("Token类型错误")

        user_id = payload.get("sub")
        is_admin = payload.get("is_admin", False)

        # 生成新的token
        if is_admin:
            access_token, new_refresh_token = create_admin_access_token(user_id)
        else:
            access_token, new_refresh_token = create_user_access_token(user_id)

        # 将旧的refresh token加入黑名单
        await redis_client.add_to_blacklist(refresh_token)

        return access_token, new_refresh_token


# ==================== 分类Service ====================
class CategoryService:
    """分类服务"""

    @staticmethod
    def get_category_repo(db: AsyncSession) -> CategoryRepository:
        """获取分类Repository"""
        return CategoryRepository(Category, db)

    async def get_categories(
        self,
        db: AsyncSession = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Category]:
        """获取分类列表(带缓存)"""
        category_repo = self.get_category_repo(db)

        # 尝试从缓存获取
        cache_key = f"categories:all:{skip}:{limit}"
        cached_categories = await redis_client.get_json(cache_key)
        if cached_categories:
            return cached_categories

        # 从数据库获取
        categories = await category_repo.get_active_categories(skip, limit)

        # 缓存结果
        await redis_client.set_json(
            cache_key,
            categories,
            expire=1800  # 30分钟
        )

        return categories

    async def get_category_by_id(self, category_id: int, db: AsyncSession = None) -> Optional[Category]:
        """获取分类详情"""
        category_repo = self.get_category_repo(db)
        return await category_repo.get_by_id(category_id)

    async def create_category(
        self,
        name: str,
        code: str,
        description: Optional[str] = None,
        sort_order: int = 0,
        is_active: bool = True,
        db: AsyncSession = None
    ) -> Category:
        """创建分类"""
        category_repo = self.get_category_repo(db)

        # 检查代码是否已存在
        existing = await category_repo.get_by_code(code)
        if existing:
            raise ValueError(f"分类代码 {code} 已存在")

        # 创建分类
        category_data = {
            "name": name,
            "code": code,
            "description": description,
            "sort_order": sort_order,
            "is_active": is_active
        }
        category = await category_repo.create(category_data)

        # 清除分类列表缓存
        await redis_client.delete_pattern("categories:*")

        return category

    async def update_category(
        self,
        category_id: int,
        **kwargs
    ) -> Optional[Category]:
        """更新分类"""
        category_repo = self.get_category_repo(db)
        category = await category_repo.update(category_id, kwargs)

        # 清除分类列表缓存
        await redis_client.delete_pattern("categories:*")

        return category

    async def delete_category(self, category_id: int, db: AsyncSession = None) -> bool:
        """删除分类"""
        category_repo = self.get_category_repo(db)
        success = await category_repo.delete(category_id)

        # 清除分类列表缓存
        await redis_client.delete_pattern("categories:*")

        return success


# ==================== 商品Service ====================
class ProductService:
    """商品服务"""

    @staticmethod
    def get_product_repo(db: AsyncSession) -> ProductRepository:
        """获取商品Repository"""
        return ProductRepository(Product, db)

    async def get_products(
        self,
        category_id: Optional[int] = None,
        keyword: Optional[str] = None,
        sort_by: str = "created_at",
        page: int = 1,
        page_size: int = 20,
        db: AsyncSession = None
    ) -> Tuple[List[Product], int]:
        """获取商品列表(带缓存、筛选、排序)"""
        product_repo = self.get_product_repo(db)

        # 生成缓存key
        cache_key = f"products:{category_id}:{keyword}:{sort_by}:{page}:{page_size}"
        try:
            cached_data = await redis_client.get_json(cache_key)
            if cached_data:
                return cached_data["products"], cached_data["total"]
        except Exception:
            # Redis失败时继续从数据库获取
            pass

        # 从数据库获取
        skip = (page - 1) * page_size
        products, total = await product_repo.get_products_with_filter(
            category_id=category_id,
            keyword=keyword,
            sort_by=sort_by,
            skip=skip,
            limit=page_size
        )

        # 尝试缓存结果（失败不影响业务）
        try:
            # 将ORM对象转换为字典以便序列化
            products_dict = [
                {
                    "id": p.id,
                    "title": p.title,
                    "category_id": p.category_id,
                    "description": p.description,
                    "price": float(p.price),
                    "stock": p.stock,
                    "sales_count": p.sales_count,
                    "views": p.views,
                    "status": p.status,
                    "is_active": p.is_active
                }
                for p in products
            ]
            cache_data = {
                "products": products_dict,
                "total": total
            }
            await redis_client.set_json(
                cache_key,
                cache_data,
                expire=600  # 10分钟
            )
        except Exception:
            # 缓存失败不影响业务
            pass

        return products, total

    async def get_hot_products(
        self,
        limit: int = 10,
        db: AsyncSession = None
    ) -> List[Product]:
        """获取热销商品(带缓存)"""
        product_repo = self.get_product_repo(db)

        # 尝试从缓存获取
        cache_key = redis_client.hot_products_key(limit)
        try:
            cached_products = await redis_client.get_json(cache_key)
            if cached_products:
                return cached_products
        except Exception:
            # Redis失败时继续从数据库获取
            pass

        # 从数据库获取
        products = await product_repo.get_hot_products(limit)

        # 尝试缓存结果（失败不影响业务）
        try:
            # 将ORM对象转换为字典以便序列化
            products_dict = [
                {
                    "id": p.id,
                    "title": p.title,
                    "category_id": p.category_id,
                    "description": p.description,
                    "price": float(p.price),
                    "stock": p.stock,
                    "sales_count": p.sales_count,
                    "views": p.views,
                    "status": p.status,
                    "is_active": p.is_active
                }
                for p in products
            ]
            await redis_client.set_json(
                cache_key,
                products_dict,
                expire=1800  # 30分钟
            )
        except Exception:
            # 缓存失败不影响业务
            pass

        return products

    async def get_product_detail(self, product_id: int, db: AsyncSession = None) -> Optional[Product]:
        """获取商品详情(带缓存)"""
        product_repo = self.get_product_repo(db)

        # 尝试从缓存获取
        cache_key = redis_client.product_detail_key(product_id)
        try:
            cached_product = await redis_client.get_json(cache_key)
            if cached_product:
                # 增加浏览量
                await redis_client.increment_view_count(product_id)
                return cached_product
        except Exception:
            # Redis失败时继续从数据库获取
            pass

        # 从数据库获取
        product = await product_repo.get_by_id(product_id)
        if product:
            # 增加浏览量
            await product_repo.increment_views(product_id)

            # 尝试缓存结果（失败不影响业务）
            try:
                # 将ORM对象转换为字典以便序列化
                product_dict = {
                    "id": product.id,
                    "title": product.title,
                    "category_id": product.category_id,
                    "description": product.description,
                    "price": float(product.price),
                    "stock": product.stock,
                    "sales_count": product.sales_count,
                    "views": product.views,
                    "status": product.status,
                    "is_active": product.is_active
                }
                await redis_client.set_json(
                    cache_key,
                    product_dict,
                    expire=3600  # 1小时
                )
            except Exception:
                # 缓存失败不影响业务
                pass

        return product

    async def search_products(
        self,
        keyword: str,
        sort_by: str = "created_at",
        page: int = 1,
        page_size: int = 20,
        db: AsyncSession = None
    ) -> Tuple[List[Product], int]:
        """搜索商品"""
        product_repo = self.get_product_repo(db)
        skip = (page - 1) * page_size

        products, total = await product_repo.get_products_with_filter(
            keyword=keyword,
            sort_by=sort_by,
            skip=skip,
            limit=page_size
        )

        return products, total

    async def create_product(
        self,
        product_data: dict,
        db: AsyncSession = None
    ) -> Product:
        """创建商品"""
        product_repo = self.get_product_repo(db)
        product = await product_repo.create(product_data)

        # 清除商品列表缓存
        await redis_client.delete_pattern("products:*")

        return product

    async def update_product(
        self,
        product_id: int,
        product_data: dict,
        db: AsyncSession = None
    ) -> Optional[Product]:
        """更新商品"""
        product_repo = self.get_product_repo(db)
        product = await product_repo.update(product_id, product_data)

        # 清除相关缓存
        await redis_client.delete(redis_client.product_detail_key(product_id))
        await redis_client.delete_pattern("products:*")

        return product

    async def delete_product(self, product_id: int, db: AsyncSession = None) -> bool:
        """删除商品"""
        product_repo = self.get_product_repo(db)
        success = await product_repo.delete(product_id)

        # 清除相关缓存
        await redis_client.delete(redis_client.product_detail_key(product_id))
        await redis_client.delete_pattern("products:*")

        return success


# ==================== 购物车Service ====================
class CartService:
    """购物车服务"""

    @staticmethod
    def get_cart_repo(db: AsyncSession) -> CartRepository:
        """获取购物车Repository"""
        return CartRepository(CartItem, db)

    async def get_user_cart(self, user_id: int, db: AsyncSession = None) -> List[CartItem]:
        """获取用户购物车(带缓存)"""
        cart_repo = self.get_cart_repo(db)

        # 尝试从缓存获取
        cache_key = redis_client.cart_key(user_id)
        cached_cart = await redis_client.get_json(cache_key)
        if cached_cart:
            return cached_cart

        # 从数据库获取
        cart_items = await cart_repo.get_user_cart(user_id)

        # 缓存结果
        await redis_client.set_json(
            cache_key,
            cart_items,
            expire=300  # 5分钟
        )

        return cart_items

    async def get_cart_summary(self, user_id: int, db: AsyncSession = None) -> dict:
        """获取购物车汇总信息"""
        from decimal import Decimal

        cart_items = await self.get_user_cart(user_id, db)

        total_quantity = sum(item.quantity for item in cart_items)
        total_amount = sum(
            item.quantity * float(item.product.price) if item.product else 0
            for item in cart_items
        )

        return {
            "total_items": len(cart_items),
            "total_quantity": total_quantity,
            "total_amount": Decimal(str(total_amount)),
            "items": cart_items
        }

    async def add_item(
        self,
        user_id: int,
        product_id: int,
        quantity: int,
        db: AsyncSession = None
    ) -> CartItem:
        """添加商品到购物车"""
        cart_repo = self.get_cart_repo(db)

        # 检查商品是否存在
        product_repo = ProductRepository(Product, db)
        product = await product_repo.get_by_id(product_id)
        if not product:
            raise ValueError("商品不存在")

        if not product.is_active or product.status != "active":
            raise ValueError("商品已下架")

        # 验证库存
        if not await product_repo.validate_stock(product_id, quantity):
            raise ValueError(f"库存不足,当前库存: {product.stock}")

        # 添加或更新购物车
        cart_item = await cart_repo.add_or_update_item(user_id, product_id, quantity)

        # 清除购物车缓存
        await redis_client.delete(redis_client.cart_key(user_id))

        return cart_item

    async def update_item_quantity(
        self,
        user_id: int,
        product_id: int,
        quantity: int,
        db: AsyncSession = None
    ) -> Optional[CartItem]:
        """更新购物车商品数量"""
        cart_repo = self.get_cart_repo(db)
        product_repo = ProductRepository(Product, db)

        # 验证商品和库存
        cart_item = await cart_repo.get_cart_item(user_id, product_id)
        if not cart_item:
            raise ValueError("购物车商品不存在")

        if not await product_repo.validate_stock(product_id, quantity):
            product = await product_repo.get_by_id(product_id)
            raise ValueError(f"库存不足,当前库存: {product.stock if product else 0}")

        cart_item.quantity = quantity
        await db.commit()
        await db.refresh(cart_item)

        # 清除购物车缓存
        await redis_client.delete(redis_client.cart_key(user_id))

        return cart_item

    async def remove_item(self, user_id: int, product_id: int, db: AsyncSession = None) -> bool:
        """删除购物车商品"""
        cart_repo = self.get_cart_repo(db)
        success = await cart_repo.remove_item(user_id, product_id)

        # 清除购物车缓存
        await redis_client.delete(redis_client.cart_key(user_id))

        return success

    async def clear_cart(self, user_id: int, db: AsyncSession = None) -> bool:
        """清空购物车"""
        cart_repo = self.get_cart_repo(db)
        success = await cart_repo.clear_cart(user_id)

        # 清除购物车缓存
        await redis_client.delete(redis_client.cart_key(user_id))

        return success


# ==================== 订单Service ====================
class OrderService:
    """订单服务"""

    # 配送费
    DELIVERY_FEE = 5.0

    @staticmethod
    def get_order_repo(db: AsyncSession) -> OrderRepository:
        """获取订单Repository"""
        return OrderRepository(Order, db)

    def generate_order_number(self) -> str:
        """生成唯一订单号"""
        return f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{secrets.token_hex(2).upper()}"

    def calculate_order_amount(
        self,
        cart_items: List[CartItem],
        delivery_type: str
    ) -> dict:
        """计算订单金额"""
        from decimal import Decimal

        # 商品小计
        subtotal = Decimal("0.00")
        for item in cart_items:
            if item.product:
                subtotal += Decimal(str(item.product.price)) * item.quantity

        # 配送费
        delivery_fee = Decimal(str(self.DELIVERY_FEE)) if delivery_type == "delivery" else Decimal("0.00")

        # 优惠(后续扩展优惠券)
        discount = Decimal("0.00")

        # 总金额
        total = subtotal + delivery_fee - discount

        return {
            "subtotal": subtotal,
            "delivery_fee": delivery_fee,
            "discount": discount,
            "total": total
        }

    async def create_order_from_cart(
        self,
        user_id: int,
        delivery_type: str,
        delivery_address: Optional[str] = None,
        pickup_name: Optional[str] = None,
        pickup_phone: Optional[str] = None,
        remark: Optional[str] = None,
        db: AsyncSession = None
    ) -> Order:
        """从购物车创建订单(事务处理)"""
        order_repo = self.get_order_repo(db)
        product_repo = ProductRepository(Product, db)
        cart_repo = CartRepository(CartItem, db)

        # 使用事务处理
        async with db.begin():
            # 1. 获取购物车商品
            cart_items = await cart_repo.get_user_cart(user_id)

            if not cart_items:
                raise ValueError("购物车为空")

            # 2. 计算订单金额
            amount_breakdown = self.calculate_order_amount(cart_items, delivery_type)

            # 3. 锁定库存(防止并发超卖)
            for item in cart_items:
                try:
                    await product_repo.lock_stock(item.product_id, item.quantity)
                except ValueError as e:
                    raise ValueError(f"商品 {item.product.title if item.product else item.product_id} {str(e)}")

            # 4. 创建订单
            order_data = {
                "order_number": self.generate_order_number(),
                "user_id": user_id,
                "total_amount": amount_breakdown["total"],
                "status": "pending",
                "delivery_type": delivery_type,
                "delivery_address": delivery_address,
                "delivery_fee": amount_breakdown["delivery_fee"],
                "pickup_name": pickup_name,
                "pickup_phone": pickup_phone,
                "remark": remark
            }

            # 5. 创建订单商品
            order_items_data = []
            for item in cart_items:
                if item.product:
                    order_items_data.append({
                        "product_id": item.product_id,
                        "product_name": item.product.title,
                        "product_image": item.product.local_image_path,
                        "quantity": item.quantity,
                        "price": item.product.price,
                        "subtotal": Decimal(str(item.product.price)) * item.quantity
                    })

            order = await order_repo.create_order(order_data, order_items_data)

            # 6. 清空购物车
            await cart_repo.clear_cart(user_id)

            # 7. 发送订单通知(Pub/Sub)
            await redis_client.publish(
                "order_notifications",
                {
                    "order_id": order.id,
                    "order_number": order.order_number,
                    "user_id": user_id,
                    "total_amount": str(amount_breakdown["total"])
                }
            )

        return order

    async def get_user_orders(
        self,
        user_id: int,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        db: AsyncSession = None
    ) -> Tuple[List[Order], int]:
        """获取用户订单"""
        order_repo = self.get_order_repo(db)
        skip = (page - 1) * page_size

        orders = await order_repo.get_user_orders(user_id, skip, page_size, status)
        total = await order_repo.get_user_orders_count(user_id, status)

        return orders, total

    async def get_order_detail(self, order_id: int, user_id: int, db: AsyncSession = None) -> Optional[Order]:
        """获取订单详情(验证用户权限)"""
        order_repo = self.get_order_repo(db)
        order = await order_repo.get_by_id(order_id)

        if not order:
            raise ValueError("订单不存在")

        if order.user_id != user_id:
            raise ValueError("无权访问该订单")

        return order

    async def cancel_order(self, order_id: int, user_id: int, db: AsyncSession = None) -> Order:
        """取消订单(释放库存)"""
        from sqlalchemy.orm import selectinload

        order_repo = self.get_order_repo(db)
        product_repo = ProductRepository(Product, db)

        # 1. 查询订单（预加载order_items）
        result = await db.execute(
            select(Order)
            .options(selectinload(Order.order_items))
            .where(Order.id == order_id)
        )
        order = result.scalar_one_or_none()

        if not order:
            raise ValueError("订单不存在")

        if order.user_id != user_id:
            raise ValueError("无权访问该订单")

        # 2. 检查状态(只有待付款订单可以取消)
        if order.status != "pending":
            raise ValueError("只有待付款订单可以取消")

        # 3. 释放库存
        for item in order.order_items:
            await product_repo.release_stock(item.product_id, item.quantity)

        # 4. 更新订单状态
        order = await order_repo.update_status_with_check(order_id, "cancelled")

        return order

    async def pay_order(self, order_id: int, user_id: int, db: AsyncSession = None) -> Order:
        """模拟支付"""
        order_repo = self.get_order_repo(db)

        # 查询订单
        order = await self.get_order_detail(order_id, user_id, db)

        # 检查状态
        if order.status != "pending":
            raise ValueError("只有待付款订单可以支付")

        # 更新订单状态
        order = await order_repo.update_status_with_check(order_id, "paid")

        return order

    async def update_order_status(
        self,
        order_id: int,
        status: str,
        db: AsyncSession = None
    ) -> Optional[Order]:
        """更新订单状态"""
        order_repo = self.get_order_repo(db)
        return await order_repo.update_status_with_check(order_id, status)


# ==================== 评价Service ====================
class ReviewService:
    """评价服务"""

    @staticmethod
    def get_review_repo(db: AsyncSession) -> ReviewRepository:
        """获取评价Repository"""
        return ReviewRepository(Review, db)

    async def create_review(
        self,
        user_id: int,
        product_id: int,
        order_id: int,
        rating: int,
        content: Optional[str] = None,
        images: Optional[List[str]] = None,
        db: AsyncSession = None
    ) -> Review:
        """创建评价"""
        import json
        from app.models import Order

        review_repo = self.get_review_repo(db)
        order_repo = OrderRepository(Order, db)
        product_repo = ProductRepository(Product, db)

        # 1. 验证订单状态
        order = await order_repo.get_by_id(order_id)
        if not order:
            raise ValueError("订单不存在")

        if order.user_id != user_id:
            raise ValueError("无权评价该订单的商品")

        if order.status != "completed":
            raise ValueError("只有已完成订单可以评价")

        # 2. 检查商品是否在订单中
        order_item_exists = False
        for item in order.order_items:
            if item.product_id == product_id:
                order_item_exists = True
                break

        if not order_item_exists:
            raise ValueError("该商品不在此订单中")

        # 3. 检查是否已评价
        if await review_repo.check_user_reviewed(user_id, product_id, order_id):
            raise ValueError("该商品已评价")

        # 4. 创建评价
        review_data = {
            "user_id": user_id,
            "product_id": product_id,
            "order_id": order_id,
            "rating": rating,
            "content": content,
            "images": json.dumps(images) if images else None
        }
        review = await review_repo.create(review_data)

        # 5. 更新商品评分
        await product_repo.update_rating(product_id)

        return review

    async def get_product_reviews(
        self,
        product_id: int,
        page: int = 1,
        page_size: int = 20,
        db: AsyncSession = None
    ) -> Tuple[List[Review], int]:
        """获取商品评价"""
        review_repo = self.get_review_repo(db)
        skip = (page - 1) * page_size

        reviews = await review_repo.get_product_reviews(product_id, skip, page_size)
        total = await review_repo.get_review_count(product_id)

        return reviews, total

    async def get_product_rating_summary(
        self,
        product_id: int,
        db: AsyncSession = None
    ) -> dict:
        """获取商品评分汇总"""
        review_repo = self.get_review_repo(db)

        avg_rating = await review_repo.get_average_rating(product_id)
        review_count = await review_repo.get_review_count(product_id)
        rating_distribution = await review_repo.get_rating_distribution(product_id)

        return {
            "product_id": product_id,
            "average_rating": round(avg_rating, 1),
            "review_count": review_count,
            "rating_distribution": rating_distribution
        }

    async def get_review_detail(self, review_id: int, db: AsyncSession = None) -> Optional[Review]:
        """获取评价详情"""
        review_repo = self.get_review_repo(db)
        return await review_repo.get_by_id(review_id)

    async def get_user_reviews(
        self,
        user_id: int,
        page: int = 1,
        page_size: int = 20,
        db: AsyncSession = None
    ) -> List[Review]:
        """获取用户评价"""
        review_repo = self.get_review_repo(db)
        skip = (page - 1) * page_size
        return await review_repo.get_user_reviews(user_id, skip, page_size)


# ==================== 管理后台Service ====================
class AdminService:
    """管理后台服务"""

    @staticmethod
    def get_admin_repo(db: AsyncSession):
        """获取管理员Repository"""
        return AdminRepository(Admin, db)

    async def log_action(
        self,
        admin_id: int,
        action: str,
        target_type: str,
        target_id: Optional[int],
        details: dict,
        db: AsyncSession,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """记录管理员操作审计日志"""
        log = AdminLog(
            admin_id=admin_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=json.dumps(details, ensure_ascii=False),
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.add(log)
        await db.commit()

    # ==================== 订单管理 ====================
    async def get_all_orders(
        self,
        user_id: Optional[int] = None,
        status: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        min_amount: Optional[Decimal] = None,
        max_amount: Optional[Decimal] = None,
        page: int = 1,
        page_size: int = 20,
        db: AsyncSession = None
    ) -> Tuple[List[Order], int]:
        """获取全局订单列表"""
        order_repo = OrderRepository(Order, db)

        # 构建查询条件
        conditions = []

        if user_id:
            conditions.append(Order.user_id == user_id)

        if status:
            conditions.append(Order.status == status)

        if start_date:
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
            conditions.append(Order.created_at >= start_datetime)

        if end_date:
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            conditions.append(Order.created_at < end_datetime)

        if min_amount is not None:
            conditions.append(Order.total_amount >= min_amount)

        if max_amount is not None:
            conditions.append(Order.total_amount <= max_amount)

        # 查询订单
        skip = (page - 1) * page_size

        query = select(Order).join(Order.user)
        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(Order.created_at.desc()).offset(skip).limit(page_size)

        result = await db.execute(query)
        orders = result.scalars().unique().all()

        # 查询总数
        count_query = select(func.count(Order.id)).select_from(Order)
        if conditions:
            count_query = count_query.where(and_(*conditions))

        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0

        return orders, total

    async def get_order_detail_with_user(self, order_id: int, db: AsyncSession) -> Optional[Order]:
        """获取订单详情(含用户信息)"""
        order_repo = OrderRepository(Order, db)
        return await order_repo.get_by_id(order_id)

    async def update_order_status(
        self,
        order_id: int,
        status: str,
        db: AsyncSession
    ) -> Optional[Order]:
        """更新订单状态"""
        order_repo = OrderRepository(Order, db)
        return await order_repo.update_status_with_check(order_id, status)

    async def export_orders_to_csv(
        self,
        user_id: Optional[int] = None,
        status: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        db: AsyncSession = None
    ) -> str:
        """导出订单为CSV"""
        # 获取所有符合条件的订单
        orders, _ = await self.get_all_orders(
            user_id=user_id,
            status=status,
            start_date=start_date,
            end_date=end_date,
            page=1,
            page_size=10000,
            db=db
        )

        # 生成CSV
        output = io.StringIO()
        writer = csv.writer(output)

        # 写入表头
        writer.writerow([
            "订单ID", "订单号", "用户手机", "用户昵称", "商品数量",
            "总金额", "状态", "配送类型", "创建时间"
        ])

        # 写入数据
        for order in orders:
            writer.writerow([
                order.id,
                order.order_number,
                order.user.phone if order.user else "",
                order.user.nickname if order.user else "",
                len(order.order_items),
                float(order.total_amount),
                order.status,
                order.delivery_type,
                order.created_at.strftime("%Y-%m-%d %H:%M:%S")
            ])

        return output.getvalue()

    async def get_order_stats(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        db: AsyncSession = None
    ) -> dict:
        """获取订单统计"""
        # 构建日期条件
        conditions = []

        if start_date:
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
            conditions.append(Order.created_at >= start_datetime)

        if end_date:
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            conditions.append(Order.created_at < end_datetime)

        # 查询总数
        count_query = select(func.count(Order.id)).select_from(Order)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        total_result = await db.execute(count_query)
        total_orders = total_result.scalar() or 0

        # 按状态统计
        status_query = select(
            Order.status,
            func.count(Order.id)
        ).select_from(Order)
        if conditions:
            status_query = status_query.where(and_(*conditions))
        status_query = status_query.group_by(Order.status)

        status_result = await db.execute(status_query)
        status_counts = {row[0]: row[1] for row in status_result.all()}

        # 总收入和平均订单价值
        revenue_query = select(
            func.sum(Order.total_amount),
            func.avg(Order.total_amount)
        ).select_from(Order)
        if conditions:
            revenue_query = revenue_query.where(and_(*conditions))

        revenue_result = await db.execute(revenue_query)
        total_revenue, avg_order_value = revenue_result.one()

        return {
            "total_orders": total_orders,
            "status_counts": status_counts,
            "total_revenue": total_revenue or Decimal("0.00"),
            "avg_order_value": avg_order_value or Decimal("0.00")
        }

    # ==================== 统计分析 ====================
    async def get_today_stats(self, db: AsyncSession = None) -> dict:
        """获取今日统计数据"""
        now = datetime.now()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # 今日订单
        orders_query = select(Order).where(Order.created_at >= start_of_day)
        orders_result = await db.execute(orders_query)
        orders = orders_result.scalars().all()

        # 今日销售额
        total_sales = sum(order.total_amount for order in orders)

        # 今日新增用户
        users_query = select(func.count(User.id)).where(User.created_at >= start_of_day)
        users_result = await db.execute(users_query)
        new_users = users_result.scalar() or 0

        # 已支付订单数
        paid_orders = len([o for o in orders if o.status == "paid"])
        completed_orders = len([o for o in orders if o.status == "completed"])

        # 平均订单价值
        avg_order_value = total_sales / len(orders) if orders else Decimal("0.00")

        return {
            "order_count": len(orders),
            "total_sales": total_sales,
            "new_users": new_users,
            "avg_order_value": avg_order_value,
            "paid_orders": paid_orders,
            "completed_orders": completed_orders
        }

    async def get_trend_analysis(
        self,
        days: int = 7,
        db: AsyncSession = None
    ) -> List[dict]:
        """获取趋势分析"""
        trend_data = []

        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            start = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end = date.replace(hour=23, minute=59, second=59, microsecond=999999)

            # 订单统计
            orders_query = select(Order).where(
                and_(Order.created_at >= start, Order.created_at <= end)
            )
            orders_result = await db.execute(orders_query)
            orders = orders_result.scalars().all()

            # 用户统计
            users_query = select(func.count(User.id)).where(
                and_(User.created_at >= start, User.created_at <= end)
            )
            users_result = await db.execute(users_query)
            new_users = users_result.scalar() or 0

            # 销售额
            total_sales = sum(order.total_amount for order in orders)

            trend_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "orders": len(orders),
                "sales": total_sales,
                "users": new_users
            })

        return trend_data[::-1]  # 按日期正序

    async def get_hot_products(
        self,
        limit: int = 10,
        db: AsyncSession = None
    ) -> List[dict]:
        """获取热销商品Top10"""
        query = select(
            Product.id.label('product_id'),
            Product.title.label('product_name'),
            Product.local_image_path.label('product_image'),
            func.sum(OrderItem.quantity).label('total_sold'),
            func.sum(OrderItem.subtotal).label('total_revenue')
        ).join(
            OrderItem, Product.id == OrderItem.product_id
        ).join(
            Order, OrderItem.order_id == Order.id
        ).filter(
            Order.status.in_(["paid", "preparing", "ready", "completed"])
        ).group_by(
            Product.id
        ).order_by(
            func.sum(OrderItem.quantity).desc()
        ).limit(limit)

        result = await db.execute(query)
        return [
            {
                "product_id": row.product_id,
                "product_name": row.product_name,
                "product_image": row.product_image,
                "total_sold": row.total_sold,
                "total_revenue": row.total_revenue or Decimal("0.00")
            }
            for row in result.all()
        ]

    async def get_category_sales(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        db: AsyncSession = None
    ) -> List[dict]:
        """获取分类销售占比"""
        # 构建日期条件
        date_conditions = []

        if start_date:
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
            date_conditions.append(Order.created_at >= start_datetime)

        if end_date:
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            date_conditions.append(Order.created_at < end_datetime)

        # 查询各分类销售额
        query = select(
            Category.id.label('category_id'),
            Category.name.label('category_name'),
            func.count(Order.id).label('order_count'),
            func.sum(OrderItem.subtotal).label('total_revenue')
        ).join(
            Product, Category.id == Product.category_id
        ).join(
            OrderItem, Product.id == OrderItem.product_id
        ).join(
            Order, OrderItem.order_id == Order.id
        )

        if date_conditions:
            query = query.where(and_(*date_conditions))

        query = query.filter(
            Order.status.in_(["paid", "preparing", "ready", "completed"])
        ).group_by(
            Category.id
        ).order_by(
            func.sum(OrderItem.subtotal).desc()
        )

        result = await db.execute(query)

        # 计算总销售额
        total_revenue = sum(row.total_revenue or Decimal("0.00") for row in result.all())

        # 重新执行查询获取数据
        result = await db.execute(query)

        return [
            {
                "category_id": row.category_id,
                "category_name": row.category_name,
                "order_count": row.order_count,
                "total_revenue": row.total_revenue or Decimal("0.00"),
                "percentage": float((row.total_revenue or Decimal("0.00")) / total_revenue * 100) if total_revenue > 0 else 0.0
            }
            for row in result.all()
        ]

    async def get_user_growth_stats(
        self,
        days: int = 30,
        db: AsyncSession = None
    ) -> List[dict]:
        """获取用户增长统计"""
        growth_data = []

        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            start = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end = date.replace(hour=23, minute=59, second=59, microsecond=999999)

            # 新增用户数
            users_query = select(func.count(User.id)).where(
                and_(User.created_at >= start, User.created_at <= end)
            )
            users_result = await db.execute(users_query)
            new_users = users_result.scalar() or 0

            growth_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "new_users": new_users
            })

        return growth_data[::-1]

    # ==================== 用户管理 ====================
    async def get_all_users(
        self,
        keyword: Optional[str] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20,
        db: AsyncSession = None
    ) -> Tuple[List[User], int]:
        """获取用户列表"""
        user_repo = UserRepository(User, db)

        # 构建查询条件
        conditions = []

        if keyword:
            conditions.append(
                or_(
                    User.phone.like(f"%{keyword}%"),
                    User.nickname.like(f"%{keyword}%")
                )
            )

        if is_active is not None:
            conditions.append(User.is_active == is_active)

        # 查询用户
        skip = (page - 1) * page_size

        query = select(User)
        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(User.created_at.desc()).offset(skip).limit(page_size)

        result = await db.execute(query)
        users = result.scalars().all()

        # 查询总数
        count_query = select(func.count(User.id))
        if conditions:
            count_query = count_query.where(and_(*conditions))

        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0

        return users, total

    async def get_user_detail_with_stats(self, user_id: int, db: AsyncSession) -> Optional[dict]:
        """获取用户详情(含统计)"""
        user_repo = UserRepository(User, db)
        user = await user_repo.get_by_id(user_id)

        if not user:
            return None

        # 统计订单数和总消费
        orders_query = select(
            func.count(Order.id),
            func.sum(Order.total_amount)
        ).where(Order.user_id == user_id)

        orders_result = await db.execute(orders_query)
        total_orders, total_spent = orders_result.one()

        # 最后订单时间
        last_order_query = select(Order.created_at).where(
            Order.user_id == user_id
        ).order_by(Order.created_at.desc()).limit(1)

        last_order_result = await db.execute(last_order_query)
        last_order_date = last_order_result.scalar()

        return {
            "user": user,
            "total_orders": total_orders or 0,
            "total_spent": total_spent or Decimal("0.00"),
            "last_order_date": last_order_date
        }

    async def update_user_status(
        self,
        user_id: int,
        is_active: bool,
        db: AsyncSession
    ) -> Optional[User]:
        """更新用户状态"""
        user_repo = UserRepository(User, db)
        user = await user_repo.get_by_id(user_id)

        if not user:
            return None

        user.is_active = is_active
        await db.commit()
        await db.refresh(user)

        return user

    # ==================== 评价管理 ====================
    async def get_all_reviews(
        self,
        product_id: Optional[int] = None,
        rating: Optional[int] = None,
        is_visible: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20,
        db: AsyncSession = None
    ) -> Tuple[List[Review], int]:
        """获取全局评价列表"""
        review_repo = ReviewRepository(Review, db)

        # 构建查询条件
        conditions = []

        if product_id:
            conditions.append(Review.product_id == product_id)

        if rating:
            conditions.append(Review.rating == rating)

        if is_visible is not None:
            conditions.append(Review.is_visible == is_visible)

        # 查询评价
        skip = (page - 1) * page_size

        query = select(Review)
        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(Review.created_at.desc()).offset(skip).limit(page_size)

        result = await db.execute(query)
        reviews = result.scalars().all()

        # 查询总数
        count_query = select(func.count(Review.id))
        if conditions:
            count_query = count_query.where(and_(*conditions))

        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0

        return reviews, total

    async def delete_review(self, review_id: int, db: AsyncSession) -> bool:
        """删除评价"""
        review_repo = ReviewRepository(Review, db)
        return await review_repo.delete(review_id)

    async def reply_review(
        self,
        review_id: int,
        reply: str,
        db: AsyncSession
    ) -> Optional[Review]:
        """管理员回复评价"""
        review_repo = ReviewRepository(Review, db)
        review = await review_repo.get_by_id(review_id)

        if not review:
            return None

        review.admin_reply = reply
        await db.commit()
        await db.refresh(review)

        return review

    # ==================== 审计日志 ====================
    async def get_audit_logs(
        self,
        admin_id: Optional[int] = None,
        action: Optional[str] = None,
        target_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        db: AsyncSession = None
    ) -> Tuple[List[AdminLog], int]:
        """获取审计日志"""
        # 构建查询条件
        conditions = []

        if admin_id:
            conditions.append(AdminLog.admin_id == admin_id)

        if action:
            conditions.append(AdminLog.action == action)

        if target_type:
            conditions.append(AdminLog.target_type == target_type)

        if start_date:
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
            conditions.append(AdminLog.created_at >= start_datetime)

        if end_date:
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            conditions.append(AdminLog.created_at < end_datetime)

        # 查询日志
        skip = (page - 1) * page_size

        query = select(AdminLog).join(Admin)
        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(AdminLog.created_at.desc()).offset(skip).limit(page_size)

        result = await db.execute(query)
        logs = result.scalars().all()

        # 查询总数
        count_query = select(func.count(AdminLog.id))
        if conditions:
            count_query = count_query.where(and_(*conditions))

        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0

        return logs, total

    async def get_audit_log_detail(self, log_id: int, db: AsyncSession) -> Optional[AdminLog]:
        """获取审计日志详情"""
        query = select(AdminLog).where(AdminLog.id == log_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
