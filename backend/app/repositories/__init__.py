"""
Repository层 - 数据访问层
负责与数据库交互,提供CRUD操作
"""
from typing import List, Optional, TypeVar, Generic, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload
from app.models import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """基础Repository"""

    def __init__(self, model: type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """根据ID获取"""
        result = await self.db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        **filters
    ) -> List[ModelType]:
        """获取所有记录"""
        query = select(self.model)
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, obj: dict) -> ModelType:
        """创建记录"""
        db_obj = self.model(**obj)
        self.db.add(db_obj)
        # flush以生成ID,但不提交事务
        await self.db.flush()
        return db_obj

    async def update(self, id: int, obj: dict) -> Optional[ModelType]:
        """更新记录"""
        query = update(self.model).where(self.model.id == id).values(**obj)
        await self.db.execute(query)
        # 移除commit - 由外层事务管理
        # await self.db.commit()
        return await self.get_by_id(id)

    async def delete(self, id: int) -> bool:
        """删除记录"""
        query = delete(self.model).where(self.model.id == id)
        result = await self.db.execute(query)
        # 移除commit - 由外层事务管理
        # await self.db.commit()
        return result.rowcount > 0

    async def count(self, **filters) -> int:
        """统计数量"""
        query = select(func.count(self.model.id))
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)
        result = await self.db.execute(query)
        return result.scalar()


class UserRepository(BaseRepository):
    """用户Repository"""

    async def get_by_phone(self, phone: str) -> Optional[ModelType]:
        """根据手机号获取用户"""
        result = await self.db.execute(
            select(self.model).where(self.model.phone == phone)
        )
        return result.scalar_one_or_none()

    async def create_user(self, phone: str, password_hash: str, **kwargs) -> ModelType:
        """创建用户"""
        user_data = {
            "phone": phone,
            "password_hash": password_hash,
            **kwargs
        }
        return await self.create(user_data)


class AdminRepository(BaseRepository):
    """管理员Repository"""

    async def get_by_username(self, username: str) -> Optional[ModelType]:
        """根据用户名获取管理员"""
        result = await self.db.execute(
            select(self.model).where(self.model.username == username)
        )
        return result.scalar_one_or_none()


class CategoryRepository(BaseRepository):
    """分类Repository"""

    async def get_active_categories(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """获取启用的分类列表"""
        query = select(self.model).where(
            self.model.is_active == True
        ).order_by(
            self.model.sort_order,
            self.model.created_at
        ).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_code(self, code: str) -> Optional[ModelType]:
        """根据代码获取分类"""
        result = await self.db.execute(
            select(self.model).where(self.model.code == code)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[ModelType]:
        """根据名称获取分类"""
        result = await self.db.execute(
            select(self.model).where(self.model.name == name)
        )
        return result.scalar_one_or_none()


class ProductRepository(BaseRepository):
    """商品Repository"""

    async def get_by_category(
        self,
        category_id: int,
        skip: int = 0,
        limit: int = 100,
        status: str = "active"
    ) -> List[ModelType]:
        """根据分类获取商品"""
        query = select(self.model).where(
            self.model.category_id == category_id,
            self.model.status == status
        )
        query = query.order_by(self.model.sort_order).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_hot_products(self, limit: int = 10) -> List[ModelType]:
        """获取热销商品(按销量排序)"""
        query = select(self.model).where(
            self.model.is_active == True,
            self.model.status == "active"
        ).order_by(
            self.model.sales_count.desc(),
            self.model.views.desc()
        ).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def increment_views(self, product_id: int) -> bool:
        """增加浏览量"""
        query = update(self.model).where(
            self.model.id == product_id
        ).values(views=self.model.views + 1)
        await self.db.execute(query)
        # 移除commit - 由外层事务管理
        # await self.db.commit()
        return True

    async def search_products(
        self,
        keyword: str,
        skip: int = 0,
        limit: int = 100,
        sort_by: str = "created_at"
    ) -> List[ModelType]:
        """搜索商品(模糊匹配标题和描述)"""
        from sqlalchemy import or_

        query = select(self.model).where(
            self.model.is_active == True,
            self.model.status == "active"
        )

        if keyword:
            query = query.where(
                or_(
                    self.model.title.ilike(f"%{keyword}%"),
                    self.model.description.ilike(f"%{keyword}%")
                )
            )

        # 排序
        if sort_by == "price_asc":
            query = query.order_by(self.model.price.asc())
        elif sort_by == "price_desc":
            query = query.order_by(self.model.price.desc())
        elif sort_by == "sales":
            query = query.order_by(self.model.sales_count.desc())
        elif sort_by == "views":
            query = query.order_by(self.model.views.desc())
        else:  # created_at
            query = query.order_by(self.model.created_at.desc())

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_products_with_filter(
        self,
        category_id: Optional[int] = None,
        keyword: Optional[str] = None,
        sort_by: str = "created_at",
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[ModelType], int]:
        """获取带筛选的商品列表"""
        from sqlalchemy import or_

        # 构建查询
        query = select(self.model).where(
            self.model.is_active == True,
            self.model.status == "active"
        )

        # 分类筛选
        if category_id:
            query = query.where(self.model.category_id == category_id)

        # 关键词搜索
        if keyword:
            query = query.where(
                or_(
                    self.model.title.ilike(f"%{keyword}%"),
                    self.model.description.ilike(f"%{keyword}%")
                )
            )

        # 排序
        if sort_by == "price_asc":
            query = query.order_by(self.model.price.asc())
        elif sort_by == "price_desc":
            query = query.order_by(self.model.price.desc())
        elif sort_by == "sales":
            query = query.order_by(self.model.sales_count.desc())
        elif sort_by == "views":
            query = query.order_by(self.model.views.desc())
        else:  # created_at
            query = query.order_by(self.model.created_at.desc())

        # 获取总数
        count_query = select(func.count(self.model.id))
        if category_id:
            count_query = count_query.where(self.model.category_id == category_id)
        if keyword:
            count_query = count_query.where(
                or_(
                    self.model.title.ilike(f"%{keyword}%"),
                    self.model.description.ilike(f"%{keyword}%")
                )
            )
        count_query = count_query.where(
            self.model.is_active == True,
            self.model.status == "active"
        )

        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # 分页
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)

        return list(result.scalars().all()), total

    async def lock_stock(self, product_id: int, quantity: int) -> ModelType:
        """锁定库存(移除FOR UPDATE避免事务冲突)"""
        # 使用普通查询，避免FOR UPDATE导致的事务问题
        result = await self.db.execute(
            select(self.model).where(self.model.id == product_id)
        )
        product = result.scalar_one_or_none()

        if not product:
            raise ValueError("商品不存在")

        if product.stock < quantity:
            raise ValueError(f"库存不足,当前库存: {product.stock}")

        product.stock -= quantity
        return product

    async def release_stock(self, product_id: int, quantity: int) -> ModelType:
        """释放库存(取消订单时)"""
        result = await self.db.execute(
            select(self.model)
            .where(self.model.id == product_id)
            .with_for_update()  # 行级锁
        )
        product = result.scalar_one_or_none()

        if not product:
            raise ValueError("商品不存在")

        product.stock += quantity
        # 移除commit和refresh - 由外层事务管理
        # await self.db.commit()
        # await self.db.refresh(product)
        return product

    async def update_rating(self, product_id: int) -> ModelType:
        """更新商品评分(根据评价计算)"""
        from app.models import Review

        # 计算平均评分
        avg_rating = await self.db.execute(
            select(func.avg(Review.rating)).where(
                Review.product_id == product_id,
                Review.is_visible == True
            )
        )
        avg_rating = avg_rating.scalar() or 0

        # 计算评价数
        review_count = await self.db.execute(
            select(func.count(Review.id)).where(
                Review.product_id == product_id,
                Review.is_visible == True
            )
        )
        review_count = review_count.scalar() or 0

        # 这里可以添加rating字段到Product模型,暂时跳过
        # await self.db.execute(
        #     update(self.model)
        #     .where(self.model.id == product_id)
        #     .values(rating=avg_rating, review_count=review_count)
        # )
        # await self.db.commit()

        return await self.get_by_id(product_id)

    async def validate_stock(self, product_id: int, quantity: int) -> bool:
        """验证库存是否充足"""
        product = await self.get_by_id(product_id)
        if not product:
            return False
        return product.stock >= quantity


class CartRepository(BaseRepository):
    """购物车Repository"""

    async def get_user_cart(self, user_id: int) -> List[ModelType]:
        """获取用户购物车"""
        # 移除selectinload，使用join一次性获取所有数据，避免事务问题
        from app.models import Product

        query = select(
            self.model.id,
            self.model.user_id,
            self.model.product_id,
            self.model.quantity,
            self.model.created_at,
            self.model.updated_at,
            Product
        ).join(
            Product, self.model.product_id == Product.id
        ).where(
            self.model.user_id == user_id
        )

        result = await self.db.execute(query)
        rows = result.all()

        # 手动构建CartItem对象，避免lazy loading
        cart_items = []
        for row in rows:
            cart_item = self.model(
                id=row[0],
                user_id=row[1],
                product_id=row[2],
                quantity=row[3],
                created_at=row[4],
                updated_at=row[5]
            )
            # 手动设置product关系
            cart_item.product = row[6]
            cart_items.append(cart_item)

        return cart_items

    async def get_cart_item(self, user_id: int, product_id: int) -> Optional[ModelType]:
        """获取购物车商品"""
        query = select(self.model).where(
            self.model.user_id == user_id,
            self.model.product_id == product_id
        ).options(selectinload(self.model.product))  # 添加预加载
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def add_or_update_item(
        self,
        user_id: int,
        product_id: int,
        quantity: int
    ) -> ModelType:
        """添加或更新购物车商品"""
        cart_item = await self.get_cart_item(user_id, product_id)
        if cart_item:
            cart_item.quantity += quantity
            # 移除commit和refresh - 由外层事务管理
            # await self.db.commit()
            # await self.db.refresh(cart_item)
            return cart_item
        else:
            return await self.create({
                "user_id": user_id,
                "product_id": product_id,
                "quantity": quantity
            })

    async def remove_item(self, user_id: int, product_id: int) -> bool:
        """删除购物车商品"""
        query = delete(self.model).where(
            self.model.user_id == user_id,
            self.model.product_id == product_id
        )
        result = await self.db.execute(query)
        # 移除commit - 由外层事务管理
        # await self.db.commit()
        return result.rowcount > 0

    async def clear_cart(self, user_id: int) -> bool:
        """清空购物车"""
        query = delete(self.model).where(self.model.user_id == user_id)
        result = await self.db.execute(query)
        # 移除commit - 由外层事务管理
        # await self.db.commit()
        return result.rowcount > 0


class OrderRepository(BaseRepository):
    """订单Repository"""

    # 订单状态转换规则
    ALLOWED_TRANSITIONS = {
        "pending": ["paid", "preparing", "cancelled"],  # 支付后可直接进入制作中
        "paid": ["preparing", "cancelled"],
        "preparing": ["ready", "cancelled"],  # 制作中可取消
        "ready": ["completed", "cancelled"],  # 待取餐可取消
        "completed": [],
        "cancelled": [],
    }

    async def get_by_order_number(self, order_number: str) -> Optional[ModelType]:
        """根据订单号获取订单"""
        result = await self.db.execute(
            select(self.model).options(
                selectinload(self.model.order_items)
            ).where(self.model.order_number == order_number)
        )
        return result.scalar_one_or_none()

    async def get_user_orders(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[ModelType]:
        """获取用户订单"""
        query = select(self.model).where(self.model.user_id == user_id)

        if status:
            query = query.where(self.model.status == status)

        query = query.options(
            selectinload(self.model.order_items)
        ).order_by(
            self.model.created_at.desc()
        ).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_user_orders_count(self, user_id: int, status: Optional[str] = None) -> int:
        """获取用户订单数量"""
        query = select(func.count(self.model.id)).where(self.model.user_id == user_id)
        if status:
            query = query.where(self.model.status == status)
        result = await self.db.execute(query)
        return result.scalar()

    async def create_order(self, order_data: dict, items_data: List[dict]) -> ModelType:
        """创建订单和订单商品"""
        from app.models import OrderItem

        # 创建订单
        order = await self.create(order_data)

        # 创建订单商品
        for item_data in items_data:
            item_data["order_id"] = order.id
            order_item = OrderItem(**item_data)
            self.db.add(order_item)

        # 移除commit和refresh - 由外层事务管理
        # await self.db.commit()
        # await self.db.refresh(order)
        return order

    async def update_order_status(self, order_id: int, status: str) -> Optional[ModelType]:
        """更新订单状态"""
        query = update(self.model).where(
            self.model.id == order_id
        ).values(status=status)
        await self.db.execute(query)
        # 移除commit - 由外层事务管理
        # await self.db.commit()
        return await self.get_by_id(order_id)

    async def can_transition_status(self, current_status: str, new_status: str) -> bool:
        """检查状态转换是否允许"""
        allowed = self.ALLOWED_TRANSITIONS.get(current_status, [])
        return new_status in allowed

    async def update_status_with_check(self, order_id: int, new_status: str) -> Optional[ModelType]:
        """更新订单状态(带状态检查)"""
        order = await self.get_by_id(order_id)
        if not order:
            raise ValueError("订单不存在")

        if not await self.can_transition_status(order.status, new_status):
            raise ValueError(
                f"状态转换不允许: {order.status} -> {new_status}"
            )

        return await self.update_order_status(order_id, new_status)


class ReviewRepository(BaseRepository):
    """评价Repository"""

    async def get_product_reviews(
        self,
        product_id: int,
        skip: int = 0,
        limit: int = 100,
        visible_only: bool = True
    ) -> List[ModelType]:
        """获取商品评价"""
        query = select(self.model).where(self.model.product_id == product_id)
        if visible_only:
            query = query.where(self.model.is_visible == True)
        query = query.order_by(
            self.model.created_at.desc()
        ).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_user_reviews(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """获取用户评价"""
        query = select(self.model).where(
            self.model.user_id == user_id
        ).order_by(
            self.model.created_at.desc()
        ).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_average_rating(self, product_id: int) -> float:
        """获取商品平均评分"""
        query = select(func.avg(self.model.rating)).where(
            self.model.product_id == product_id,
            self.model.is_visible == True
        )
        result = await self.db.execute(query)
        return result.scalar() or 0.0

    async def get_review_count(self, product_id: int) -> int:
        """获取商品评价数量"""
        query = select(func.count(self.model.id)).where(
            self.model.product_id == product_id,
            self.model.is_visible == True
        )
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def get_rating_distribution(self, product_id: int) -> dict:
        """获取商品评分分布"""
        query = select(
            self.model.rating,
            func.count(self.model.id)
        ).where(
            self.model.product_id == product_id,
            self.model.is_visible == True
        ).group_by(self.model.rating)

        result = await self.db.execute(query)
        distribution = {i: 0 for i in range(1, 6)}
        for rating, count in result:
            distribution[rating] = count

        return distribution

    async def check_user_reviewed(
        self,
        user_id: int,
        product_id: int,
        order_id: int
    ) -> bool:
        """检查用户是否已评价该商品"""
        result = await self.db.execute(
            select(self.model).where(
                self.model.user_id == user_id,
                self.model.product_id == product_id,
                self.model.order_id == order_id
            )
        )
        return result.scalar_one_or_none() is not None
