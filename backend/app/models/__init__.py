from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Boolean, Enum, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class ProductStatus(str, enum.Enum):
    """商品状态"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    OUT_OF_STOCK = "out_of_stock"


class OrderStatus(str, enum.Enum):
    """订单状态"""
    PENDING = "pending"           # 待付款
    PAID = "paid"                # 已付款
    PREPARING = "preparing"       # 制作中
    READY = "ready"              # 待取餐/配送中
    COMPLETED = "completed"       # 已完成
    CANCELLED = "cancelled"       # 已取消


class DeliveryType(str, enum.Enum):
    """配送类型"""
    DELIVERY = "delivery"         # 外卖配送
    PICKUP = "pickup"             # 到店自取


class Category(Base):
    """商品分类表"""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, comment="分类名称")
    code = Column(String(50), unique=True, nullable=False, comment="分类代码")
    description = Column(Text, nullable=True, comment="分类描述")
    sort_order = Column(Integer, default=0, comment="排序")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关联商品
    products = relationship("Product", back_populates="category", cascade="all, delete-orphan")


class Product(Base):
    """商品表"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, comment="商品标题")
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, comment="分类ID")
    detail_url = Column(String(1000), nullable=True, comment="详情链接")
    image_url = Column(String(1000), nullable=True, comment="原始图片URL")
    local_image_path = Column(String(1000), nullable=False, comment="本地图片路径")
    ingredients = Column(Text, nullable=True, comment="食材信息")
    description = Column(Text, nullable=True, comment="商品描述")
    price = Column(Numeric(10, 2), nullable=False, default=0.00, comment="价格")
    stock = Column(Integer, default=0, comment="库存数量")
    sales_count = Column(Integer, default=0, comment="销量")
    views = Column(Integer, default=0, comment="浏览量")
    favorites = Column(Integer, default=0, comment="收藏量")
    status = Column(Enum(ProductStatus), default=ProductStatus.ACTIVE, comment="商品状态")
    is_active = Column(Boolean, default=True, comment="是否启用")
    sort_order = Column(Integer, default=0, comment="排序")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关联分类
    category = relationship("Category", back_populates="products")


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(20), unique=True, nullable=False, index=True, comment="手机号")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    nickname = Column(String(100), nullable=True, comment="昵称")
    avatar = Column(String(500), nullable=True, comment="头像URL")
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关联购物车
    cart_items = relationship("CartItem", back_populates="user", cascade="all, delete-orphan")
    # 关联订单
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    # 关联评价
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")


class Admin(Base):
    """管理员表"""
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True, comment="用户名")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    email = Column(String(255), nullable=True, comment="邮箱")
    role = Column(String(50), default="admin", comment="角色")
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")


class CartItem(Base):
    """购物车表"""
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, comment="商品ID")
    quantity = Column(Integer, default=1, nullable=False, comment="数量")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关联用户
    user = relationship("User", back_populates="cart_items")
    # 关联商品
    product = relationship("Product")


class Order(Base):
    """订单表"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(100), unique=True, nullable=False, index=True, comment="订单号")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    total_amount = Column(Numeric(10, 2), nullable=False, comment="总金额")
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, comment="订单状态")
    delivery_type = Column(Enum(DeliveryType), default=DeliveryType.PICKUP, comment="配送类型")
    delivery_address = Column(String(500), nullable=True, comment="配送地址")
    delivery_fee = Column(Numeric(10, 2), default=0.00, comment="配送费")
    pickup_name = Column(String(100), nullable=True, comment="自提人姓名")
    pickup_phone = Column(String(20), nullable=True, comment="自提人电话")
    remark = Column(Text, nullable=True, comment="备注")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关联用户
    user = relationship("User", back_populates="orders")
    # 关联订单商品
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    """订单商品表"""
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, comment="订单ID")
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, comment="商品ID")
    product_name = Column(String(500), nullable=False, comment="商品名称")
    product_image = Column(String(1000), nullable=True, comment="商品图片")
    quantity = Column(Integer, nullable=False, comment="数量")
    price = Column(Numeric(10, 2), nullable=False, comment="单价")
    subtotal = Column(Numeric(10, 2), nullable=False, comment="小计")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    # 关联订单
    order = relationship("Order", back_populates="order_items")
    # 关联商品
    product = relationship("Product")


class Review(Base):
    """评价表"""
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, comment="商品ID")
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True, comment="订单ID")
    rating = Column(Integer, nullable=False, comment="评分 1-5")
    content = Column(Text, nullable=True, comment="评价内容")
    images = Column(Text, nullable=True, comment="评价图片URL列表(JSON)")
    admin_reply = Column(Text, nullable=True, comment="管理员回复")
    is_visible = Column(Boolean, default=True, comment="是否显示")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关联用户
    user = relationship("User", back_populates="reviews")
    # 关联商品
    product = relationship("Product")


class AdminLog(Base):
    """管理员操作审计日志表"""
    __tablename__ = "admin_logs"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("admins.id"), nullable=False, comment="管理员ID")
    action = Column(String(100), nullable=False, index=True, comment="操作类型")
    target_type = Column(String(50), nullable=False, comment="目标类型(order/product/user/review)")
    target_id = Column(Integer, nullable=True, comment="目标ID")
    details = Column(Text, nullable=True, comment="操作详情(JSON)")
    ip_address = Column(String(50), nullable=True, comment="IP地址")
    user_agent = Column(String(500), nullable=True, comment="用户代理")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    # 关联管理员
    admin = relationship("Admin")
