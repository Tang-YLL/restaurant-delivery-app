"""
Pydantic Schemas定义
用于请求和响应的数据验证
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from enum import Enum


# ==================== 用户相关Schema ====================
class UserBase(BaseModel):
    """用户基础Schema"""
    phone: str = Field(..., pattern=r'^\d{11}$', description="手机号")
    nickname: Optional[str] = Field(None, max_length=100, description="昵称")


class UserCreate(UserBase):
    """用户创建Schema"""
    password: str = Field(..., min_length=6, max_length=50, description="密码")


class UserUpdate(BaseModel):
    """用户更新Schema"""
    nickname: Optional[str] = Field(None, max_length=100, description="昵称")
    avatar: Optional[str] = Field(None, max_length=500, description="头像URL")


class UserResponse(BaseModel):
    """用户响应Schema"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    phone: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ==================== 管理员相关Schema ====================
class AdminBase(BaseModel):
    """管理员基础Schema"""
    username: str = Field(..., min_length=3, max_length=100, description="用户名")
    email: Optional[str] = Field(None, description="邮箱")


class AdminCreate(AdminBase):
    """管理员创建Schema"""
    password: str = Field(..., min_length=6, max_length=50, description="密码")


class AdminResponse(BaseModel):
    """管理员响应Schema"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime


# ==================== 认证相关Schema ====================
class Token(BaseModel):
    """Token响应Schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Token负载Schema"""
    sub: int
    is_admin: bool = False
    exp: Optional[int] = None


class LoginRequest(BaseModel):
    """登录请求Schema"""
    phone: str = Field(..., description="手机号")
    password: str = Field(..., description="密码")


class RegisterRequest(UserCreate):
    """注册请求Schema"""
    pass


class AdminLoginRequest(BaseModel):
    """管理员登录请求Schema"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class RefreshTokenRequest(BaseModel):
    """刷新Token请求Schema"""
    refresh_token: str


# ==================== 分类相关Schema ====================
class CategoryBase(BaseModel):
    """分类基础Schema"""
    name: str = Field(..., max_length=100, description="分类名称")
    code: str = Field(..., max_length=50, description="分类代码")
    description: Optional[str] = Field(None, description="分类描述")
    sort_order: int = Field(0, description="排序")
    is_active: bool = Field(True, description="是否启用")


class CategoryCreate(CategoryBase):
    """分类创建Schema"""
    pass


class CategoryUpdate(BaseModel):
    """分类更新Schema"""
    name: Optional[str] = Field(None, max_length=100, description="分类名称")
    description: Optional[str] = Field(None, description="分类描述")
    sort_order: Optional[int] = Field(None, description="排序")
    is_active: Optional[bool] = Field(None, description="是否启用")


class CategoryResponse(BaseModel):
    """分类响应Schema"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: str
    description: Optional[str] = None
    sort_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ==================== 商品相关Schema ====================
class ProductStatus(str, Enum):
    """商品状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    OUT_OF_STOCK = "out_of_stock"


class ProductBase(BaseModel):
    """商品基础Schema"""
    title: str = Field(..., max_length=500, description="商品标题")
    category_id: int = Field(..., description="分类ID")
    detail_url: Optional[str] = Field(None, max_length=1000, description="详情链接")
    image_url: Optional[str] = Field(None, max_length=1000, description="图片URL")
    local_image_path: str = Field(..., max_length=1000, description="本地图片路径")
    ingredients: Optional[str] = Field(None, description="食材信息")
    description: Optional[str] = Field(None, description="商品描述")
    price: Decimal = Field(..., ge=0, description="价格")
    stock: int = Field(0, ge=0, description="库存数量")
    status: ProductStatus = Field(ProductStatus.ACTIVE, description="商品状态")
    is_active: bool = Field(True, description="是否启用")
    sort_order: int = Field(0, description="排序")


class ProductCreate(ProductBase):
    """商品创建Schema"""
    pass


class ProductUpdate(BaseModel):
    """商品更新Schema"""
    title: Optional[str] = Field(None, max_length=500, description="商品标题")
    category_id: Optional[int] = Field(None, description="分类ID")
    detail_url: Optional[str] = Field(None, max_length=1000, description="详情链接")
    image_url: Optional[str] = Field(None, max_length=1000, description="图片URL")
    local_image_path: Optional[str] = Field(None, max_length=1000, description="本地图片路径")
    ingredients: Optional[str] = Field(None, description="食材信息")
    description: Optional[str] = Field(None, description="商品描述")
    price: Optional[Decimal] = Field(None, ge=0, description="价格")
    stock: Optional[int] = Field(None, ge=0, description="库存数量")
    status: Optional[ProductStatus] = Field(None, description="商品状态")
    is_active: Optional[bool] = Field(None, description="是否启用")
    sort_order: Optional[int] = Field(None, description="排序")


class ProductResponse(BaseModel):
    """商品响应Schema"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    category_id: int
    detail_url: Optional[str] = None
    image_url: Optional[str] = None
    local_image_path: str
    ingredients: Optional[str] = None
    description: Optional[str] = None
    price: Decimal
    stock: int
    sales_count: int
    views: int
    favorites: int
    status: str
    is_active: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryResponse] = None


# ==================== 购物车相关Schema ====================
class CartItemBase(BaseModel):
    """购物车基础Schema"""
    product_id: int = Field(..., description="商品ID")
    quantity: int = Field(1, ge=1, description="数量")


class CartItemCreate(CartItemBase):
    """购物车创建Schema"""
    pass


class CartItemUpdate(BaseModel):
    """购物车更新Schema"""
    quantity: int = Field(..., ge=1, description="数量")


class CartItemResponse(BaseModel):
    """购物车响应Schema"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    product_id: int
    quantity: int
    created_at: datetime
    product: Optional[ProductResponse] = None


# ==================== 订单相关Schema ====================
class DeliveryType(str, Enum):
    """配送类型枚举"""
    DELIVERY = "delivery"
    PICKUP = "pickup"


class OrderStatus(str, Enum):
    """订单状态枚举"""
    PENDING = "pending"
    PAID = "paid"
    PREPARING = "preparing"
    READY = "ready"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class OrderItemBase(BaseModel):
    """订单商品基础Schema"""
    product_id: int = Field(..., description="商品ID")
    quantity: int = Field(..., ge=1, description="数量")


class OrderItemResponse(BaseModel):
    """订单商品响应Schema"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    product_id: int
    product_name: str
    product_image: Optional[str] = None
    quantity: int
    price: Decimal
    subtotal: Decimal
    created_at: datetime


class OrderCreate(BaseModel):
    """订单创建Schema"""
    delivery_type: DeliveryType = Field(DeliveryType.PICKUP, description="配送类型")
    delivery_address: Optional[str] = Field(None, max_length=500, description="配送地址")
    pickup_name: Optional[str] = Field(None, max_length=100, description="自提人姓名")
    pickup_phone: Optional[str] = Field(None, max_length=20, description="自提人电话")
    remark: Optional[str] = Field(None, description="备注")


class OrderUpdate(BaseModel):
    """订单更新Schema"""
    status: OrderStatus = Field(..., description="订单状态")
    remark: Optional[str] = Field(None, description="备注")


class OrderResponse(BaseModel):
    """订单响应Schema"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_number: str
    user_id: int
    total_amount: Decimal
    status: str
    delivery_type: str
    delivery_address: Optional[str] = None
    delivery_fee: Decimal
    pickup_name: Optional[str] = None
    pickup_phone: Optional[str] = None
    remark: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    order_items: List[OrderItemResponse] = []


class OrderAmountBreakdown(BaseModel):
    """订单金额明细Schema"""
    subtotal: Decimal = Field(..., description="商品小计")
    delivery_fee: Decimal = Field(..., description="配送费")
    discount: Decimal = Field(..., description="优惠金额")
    total: Decimal = Field(..., description="总金额")


# ==================== 评价相关Schema ====================
class ReviewBase(BaseModel):
    """评价基础Schema"""
    product_id: int = Field(..., description="商品ID")
    order_id: int = Field(..., description="订单ID")
    rating: int = Field(..., ge=1, le=5, description="评分 1-5")
    content: Optional[str] = Field(None, description="评价内容")
    images: Optional[List[str]] = Field(None, description="评价图片URL列表")


class ReviewCreate(ReviewBase):
    """评价创建Schema"""
    pass


class ReviewUpdate(BaseModel):
    """评价更新Schema"""
    rating: Optional[int] = Field(None, ge=1, le=5, description="评分 1-5")
    content: Optional[str] = Field(None, description="评价内容")
    is_visible: Optional[bool] = Field(None, description="是否显示")


class ReviewResponse(BaseModel):
    """评价响应Schema"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    product_id: int
    order_id: Optional[int] = None
    rating: int
    content: Optional[str] = None
    images: Optional[List[str]] = None
    is_visible: bool
    created_at: datetime
    updated_at: datetime
    user: Optional[UserResponse] = None


class ProductRatingSummary(BaseModel):
    """商品评分汇总Schema"""
    product_id: int
    average_rating: float
    review_count: int
    rating_distribution: dict


# ==================== 分页Schema ====================
class PaginationParams(BaseModel):
    """分页参数Schema"""
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")


class PaginatedResponse(BaseModel):
    """分页响应Schema"""
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")


# ==================== 通用响应Schema ====================
class MessageResponse(BaseModel):
    """消息响应Schema"""
    message: str
    success: bool = True


class HealthResponse(BaseModel):
    """健康检查响应Schema"""
    status: str
    database: str
    redis: str


# ==================== 管理后台相关Schema ====================
class AdminOrderListQuery(BaseModel):
    """管理后台订单列表查询Schema"""
    user_id: Optional[int] = Field(None, description="用户ID筛选")
    status: Optional[str] = Field(None, description="订单状态筛选")
    start_date: Optional[str] = Field(None, description="开始日期(YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="结束日期(YYYY-MM-DD)")
    min_amount: Optional[Decimal] = Field(None, ge=0, description="最小金额")
    max_amount: Optional[Decimal] = Field(None, ge=0, description="最大金额")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")


class AdminOrderDetailResponse(BaseModel):
    """管理后台订单详情响应Schema"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_number: str
    user_id: int
    user_phone: Optional[str] = None
    user_nickname: Optional[str] = None
    total_amount: Decimal
    status: str
    delivery_type: str
    delivery_address: Optional[str] = None
    delivery_fee: Decimal
    pickup_name: Optional[str] = None
    pickup_phone: Optional[str] = None
    remark: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    order_items: List[OrderItemResponse] = []


class AdminOrderStatsResponse(BaseModel):
    """管理后台订单统计响应Schema"""
    total_orders: int
    status_counts: dict
    total_revenue: Decimal
    avg_order_value: Decimal


class AdminProductStockUpdate(BaseModel):
    """管理后台商品库存更新Schema"""
    stock_adjustment: int = Field(..., description="库存调整量(正数增加,负数减少)")


class AdminProductBatchOperation(BaseModel):
    """管理后台商品批量操作Schema"""
    product_ids: List[int] = Field(..., description="商品ID列表")
    operation: str = Field(..., description="操作类型: activate/deactivate/delete")
    reason: Optional[str] = Field(None, description="操作原因")


class AdminTodayStatsResponse(BaseModel):
    """管理后台今日统计响应Schema"""
    order_count: int
    total_sales: Decimal
    new_users: int
    avg_order_value: Decimal
    paid_orders: int
    completed_orders: int


class AdminTrendDataPoint(BaseModel):
    """管理后台趋势数据点Schema"""
    date: str
    orders: int
    sales: Decimal
    users: int


class AdminTrendResponse(BaseModel):
    """管理后台趋势响应Schema"""
    trend: List[AdminTrendDataPoint]
    summary: dict


class AdminHotProductResponse(BaseModel):
    """管理后台热销商品响应Schema"""
    product_id: int
    product_name: str
    product_image: Optional[str] = None
    total_sold: int
    total_revenue: Decimal


class AdminCategorySalesResponse(BaseModel):
    """管理后台分类销售响应Schema"""
    category_id: int
    category_name: str
    order_count: int
    total_revenue: Decimal
    percentage: float


class AdminUserListQuery(BaseModel):
    """管理后台用户列表查询Schema"""
    keyword: Optional[str] = Field(None, description="搜索关键词(手机号/昵称)")
    is_active: Optional[bool] = Field(None, description="是否激活")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")


class AdminUserDetailResponse(BaseModel):
    """管理后台用户详情响应Schema"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    phone: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    is_active: bool
    created_at: datetime
    total_orders: int
    total_spent: Decimal
    last_order_date: Optional[datetime] = None


class AdminUserStatusUpdate(BaseModel):
    """管理后台用户状态更新Schema"""
    is_active: bool = Field(..., description="是否激活")


class AdminReviewListQuery(BaseModel):
    """管理后台评价列表查询Schema"""
    product_id: Optional[int] = Field(None, description="商品ID筛选")
    rating: Optional[int] = Field(None, ge=1, le=5, description="评分筛选")
    is_visible: Optional[bool] = Field(None, description="是否显示")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")


class AdminReviewReplyRequest(BaseModel):
    """管理后台评价回复请求Schema"""
    reply: str = Field(..., min_length=1, max_length=500, description="回复内容")


class AdminAuditLogQuery(BaseModel):
    """管理后台审计日志查询Schema"""
    admin_id: Optional[int] = Field(None, description="管理员ID筛选")
    action: Optional[str] = Field(None, description="操作类型筛选")
    target_type: Optional[str] = Field(None, description="目标类型筛选")
    start_date: Optional[str] = Field(None, description="开始日期(YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="结束日期(YYYY-MM-DD)")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")


class AdminAuditLogResponse(BaseModel):
    """管理后台审计日志响应Schema"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    admin_id: int
    admin_username: Optional[str] = None
    action: str
    target_type: str
    target_id: Optional[int] = None
    details: Optional[dict] = None
    ip_address: Optional[str] = None
    created_at: datetime
