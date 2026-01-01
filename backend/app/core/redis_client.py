"""
Redis客户端和缓存管理
"""
import json
import logging
from typing import Optional, Any, List
from redis import asyncio as aioredis
from redis.asyncio import Redis, ConnectionPool

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class RedisClient:
    """Redis客户端封装"""

    def __init__(self):
        self._pool: Optional[ConnectionPool] = None
        self._redis: Optional[Redis] = None

    async def connect(self):
        """连接Redis"""
        try:
            self._pool = ConnectionPool.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            self._redis = Redis(connection_pool=self._pool)
            await self._redis.ping()
            logger.info("Redis连接成功")
        except Exception as e:
            logger.error(f"Redis连接失败: {e}")
            # 不抛出异常,允许应用在没有Redis的情况下运行

    async def close(self):
        """关闭连接"""
        if self._redis:
            await self._redis.close()
        if self._pool:
            await self._pool.disconnect()

    @property
    def redis(self) -> Redis:
        """获取Redis客户端"""
        if self._redis is None:
            raise RuntimeError("Redis未初始化,请先调用connect()")
        return self._redis

    async def get(self, key: str) -> Optional[str]:
        """获取缓存"""
        try:
            if self._redis is None:
                # Redis未初始化时,返回None(用于测试环境)
                return None
            return await self.redis.get(key)
        except Exception as e:
            logger.error(f"Redis GET失败: {e}")
            return None

    async def set(self, key: str, value: str, expire: int = None) -> bool:
        """设置缓存"""
        try:
            if self._redis is None:
                # Redis未初始化时,静默失败(用于测试环境)
                return True
            return await self.redis.set(key, value, ex=expire)
        except Exception as e:
            logger.error(f"Redis SET失败: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """删除缓存"""
        try:
            return await self.redis.delete(key) > 0
        except Exception as e:
            logger.error(f"Redis DELETE失败: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """检查key是否存在"""
        try:
            if self._redis is None:
                # Redis未初始化时,返回False(用于测试环境)
                return False
            return await self.redis.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis EXISTS失败: {e}")
            return False

    async def expire(self, key: str, seconds: int) -> bool:
        """设置过期时间"""
        try:
            return await self.redis.expire(key, seconds)
        except Exception as e:
            logger.error(f"Redis EXPIRE失败: {e}")
            return False

    async def get_json(self, key: str) -> Optional[Any]:
        """获取JSON缓存"""
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None
        return None

    async def set_json(self, key: str, value: Any, expire: int = None) -> bool:
        """设置JSON缓存"""
        try:
            json_value = json.dumps(value, ensure_ascii=False)
            return await self.set(key, json_value, expire)
        except Exception as e:
            logger.error(f"Redis SET_JSON失败: {e}")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """删除匹配模式的所有key"""
        try:
            keys = []
            async for key in self.redis.scan_iter(match=pattern):
                keys.append(key)
            if keys:
                return await self.redis.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Redis DELETE_PATTERN失败: {e}")
            return 0

    # Token黑名单相关
    async def add_to_blacklist(self, token: str, expire: int = None) -> bool:
        """添加token到黑名单"""
        key = f"blacklist:{token}"
        return await self.set(key, "1", expire)

    async def is_token_blacklisted(self, token: str) -> bool:
        """检查token是否在黑名单中"""
        key = f"blacklist:{token}"
        return await self.exists(key)

    async def remove_from_blacklist(self, token: str) -> bool:
        """从黑名单移除token"""
        key = f"blacklist:{token}"
        return await self.delete(key)

    # 缓存key生成
    @staticmethod
    def product_list_key(category_id: Optional[int] = None, page: int = 1, page_size: int = 20) -> str:
        """生成商品列表缓存key"""
        if category_id:
            return f"products:category:{category_id}:page:{page}:size:{page_size}"
        return f"products:page:{page}:size:{page_size}"

    @staticmethod
    def product_detail_key(product_id: int) -> str:
        """生成商品详情缓存key"""
        return f"product:detail:{product_id}"

    @staticmethod
    def hot_products_key(limit: int = 10) -> str:
        """生成热门商品缓存key"""
        return f"products:hot:{limit}"

    @staticmethod
    def cart_key(user_id: int) -> str:
        """生成购物车缓存key"""
        return f"cart:user:{user_id}"

    @staticmethod
    def user_info_key(user_id: int) -> str:
        """生成用户信息缓存key"""
        return f"user:info:{user_id}"

    # Pub/Sub相关
    async def publish(self, channel: str, message: Any) -> int:
        """发布消息"""
        try:
            message_str = json.dumps(message) if not isinstance(message, str) else message
            return await self.redis.publish(channel, message_str)
        except Exception as e:
            logger.error(f"Redis PUBLISH失败: {e}")
            return 0

    async def subscribe(self, channel: str):
        """订阅频道"""
        try:
            pubsub = self.redis.pubsub()
            await pubsub.subscribe(channel)
            return pubsub
        except Exception as e:
            logger.error(f"Redis SUBSCRIBE失败: {e}")
            return None

    # Session相关
    async def set_session(self, user_id: int, session_data: dict, expire: int = 86400) -> bool:
        """设置用户session"""
        key = f"session:user:{user_id}"
        return await self.set_json(key, session_data, expire)

    async def get_session(self, user_id: int) -> Optional[dict]:
        """获取用户session"""
        key = f"session:user:{user_id}"
        return await self.get_json(key)

    async def delete_session(self, user_id: int) -> bool:
        """删除用户session"""
        key = f"session:user:{user_id}"
        return await self.delete(key)

    # 统计相关
    async def increment_view_count(self, product_id: int) -> int:
        """增加商品浏览量"""
        key = f"product:views:{product_id}"
        try:
            return await self.redis.incr(key)
        except Exception as e:
            logger.error(f"Redis INCR失败: {e}")
            return 0

    async def get_view_count(self, product_id: int) -> int:
        """获取商品浏览量"""
        key = f"product:views:{product_id}"
        try:
            value = await self.redis.get(key)
            return int(value) if value else 0
        except Exception as e:
            logger.error(f"Redis GET失败: {e}")
            return 0


# 创建全局Redis客户端实例
redis_client = RedisClient()


async def init_redis():
    """初始化Redis连接"""
    await redis_client.connect()


async def close_redis():
    """关闭Redis连接"""
    await redis_client.close()
