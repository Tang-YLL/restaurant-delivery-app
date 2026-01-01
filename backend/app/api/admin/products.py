"""
管理后台商品管理API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.core.security import get_current_admin
from app.models import Admin
from app.schemas import (
    AdminProductStockUpdate,
    AdminProductBatchOperation,
    MessageResponse,
    ProductCreate,
    ProductUpdate,
    ProductResponse
)
from app.services import AdminService, ProductService
from app.repositories import ProductRepository
from app.models import Product

router = APIRouter(prefix="/admin/products", tags=["管理后台-商品管理"])


@router.post("", response_model=ProductResponse, status_code=201)
async def create_product(
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    创建商品

    管理员创建新商品
    """
    try:
        product_service = ProductService()
        product = await product_service.create_product(
            name=product_data.name,
            description=product_data.description,
            price=product_data.price,
            category_id=product_data.category_id,
            image_url=product_data.image_url,
            is_available=product_data.is_available,
            is_hot=product_data.is_hot,
            db=db
        )
        return product
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    更新商品信息

    管理员更新商品的基本信息
    """
    try:
        product_service = ProductService()
        product = await product_service.update_product(
            product_id=product_id,
            **product_data.model_dump(exclude_unset=True),
            db=db
        )
        return product
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=404, detail="商品不存在")


@router.delete("/{product_id}", response_model=MessageResponse)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    删除商品

    管理员删除商品(软删除)
    """
    try:
        product_service = ProductService()
        await product_service.delete_product(product_id=product_id, db=db)
        return {"message": "商品删除成功", "success": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=404, detail="商品不存在")


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    获取商品详情

    管理员查看商品详细信息
    """
    product_repo = ProductRepository(Product, db)
    product = await product_repo.get_by_id(product_id)

    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    return product


@router.put("/{product_id}/stock", response_model=MessageResponse)
@router.patch("/{product_id}/stock", response_model=MessageResponse)
async def update_product_stock(
    product_id: int,
    stock_update: AdminProductStockUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    调整商品库存

    管理员可以增加或减少商品库存,记录操作日志
    - 正数:增加库存
    - 负数:减少库存
    """
    try:
        product_repo = ProductRepository(Product, db)
        product = await product_repo.get_by_id(product_id)

        if not product:
            raise HTTPException(status_code=404, detail="商品不存在")

        old_stock = product.stock
        adjustment = stock_update.stock_adjustment
        new_stock = old_stock + adjustment

        if new_stock < 0:
            raise HTTPException(status_code=400, detail="库存不能为负数")

        # 更新库存
        product.stock = new_stock
        await db.commit()
        await db.refresh(product)

        # 记录审计日志
        await AdminService().log_action(
            admin_id=current_admin.id,
            action="update_product_stock",
            target_type="product",
            target_id=product_id,
            details={
                "old_stock": old_stock,
                "adjustment": adjustment,
                "new_stock": new_stock,
                "product_name": product.title
            },
            db=db
        )

        # 清除缓存
        from app.core.redis_client import redis_client
        await redis_client.delete_pattern("products:*")

        action = "增加" if adjustment > 0 else "减少"
        return MessageResponse(
            message=f"库存已{action},从{old_stock}调整为{new_stock}",
            success=True
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch", response_model=MessageResponse)
async def batch_product_operation(
    batch_op: AdminProductBatchOperation,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    批量操作商品

    管理员可以对多个商品执行批量操作:
    - activate: 批量上架
    - deactivate: 批量下架
    - delete: 批量删除
    """
    try:
        product_repo = ProductRepository(Product, db)
        service = ProductService()

        if batch_op.operation not in ["activate", "deactivate", "delete"]:
            raise HTTPException(status_code=400, detail="无效的操作类型")

        success_count = 0
        failed_products = []

        for product_id in batch_op.product_ids:
            try:
                product = await product_repo.get_by_id(product_id)

                if not product:
                    failed_products.append({
                        "product_id": product_id,
                        "reason": "商品不存在"
                    })
                    continue

                if batch_op.operation == "activate":
                    product.is_active = True
                    await db.commit()

                elif batch_op.operation == "deactivate":
                    product.is_active = False
                    await db.commit()

                elif batch_op.operation == "delete":
                    await service.delete_product(product_id, db)

                success_count += 1

            except Exception as e:
                failed_products.append({
                    "product_id": product_id,
                    "reason": str(e)
                })

        # 清除缓存
        from app.core.redis_client import redis_client
        await redis_client.delete_pattern("products:*")

        # 记录审计日志
        await AdminService().log_action(
            admin_id=current_admin.id,
            action=f"batch_{batch_op.operation}_products",
            target_type="product",
            target_id=None,
            details={
                "operation": batch_op.operation,
                "product_ids": batch_op.product_ids,
                "success_count": success_count,
                "failed_count": len(failed_products),
                "reason": batch_op.reason
            },
            db=db
        )

        operation_names = {
            "activate": "上架",
            "deactivate": "下架",
            "delete": "删除"
        }

        message = f"批量{operation_names[batch_op.operation]}完成:成功{success_count}个"
        if failed_products:
            message += f",失败{len(failed_products)}个"

        return MessageResponse(
            message=message,
            success=True
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stock/low")
async def get_low_stock_products(
    threshold: int = Query(10, ge=0, description="库存阈值"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    获取低库存商品列表

    返回库存低于指定阈值的商品
    """
    try:
        from sqlalchemy import select

        skip = (page - 1) * page_size

        query = select(Product).where(
            Product.stock < threshold
        ).order_by(
            Product.stock.asc()
        ).offset(skip).limit(page_size)

        result = await db.execute(query)
        products = result.scalars().all()

        # 查询总数
        from sqlalchemy import func
        count_query = select(func.count(Product.id)).where(
            Product.stock < threshold
        )
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0

        # 计算总页数
        total_pages = (total + page_size - 1) // page_size

        # 构建响应数据
        products_data = []
        for product in products:
            products_data.append({
                "id": product.id,
                "title": product.title,
                "stock": product.stock,
                "price": float(product.price),
                "sales_count": product.sales_count,
                "local_image_path": product.local_image_path,
                "category_id": product.category_id,
                "is_active": product.is_active
            })

        return {
            "products": products_data,
            "threshold": threshold,
            "pagination": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/summary")
async def get_product_stats(
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    获取商品统计

    返回商品相关的统计数据:
    - 商品总数
    - 在售商品数
    - 下架商品数
    - 低库存商品数
    - 总库存数
    """
    try:
        from sqlalchemy import select, func, and_
        from app.models import Product

        # 商品总数
        total_result = await db.execute(select(func.count(Product.id)))
        total_products = total_result.scalar() or 0

        # 在售商品数
        active_result = await db.execute(
            select(func.count(Product.id)).where(Product.is_active == True)
        )
        active_products = active_result.scalar() or 0

        # 下架商品数
        inactive_result = await db.execute(
            select(func.count(Product.id)).where(Product.is_active == False)
        )
        inactive_products = inactive_result.scalar() or 0

        # 低库存商品数(库存<10)
        low_stock_result = await db.execute(
            select(func.count(Product.id)).where(Product.stock < 10)
        )
        low_stock_products = low_stock_result.scalar() or 0

        # 总库存数
        total_stock_result = await db.execute(select(func.sum(Product.stock)))
        total_stock = total_stock_result.scalar() or 0

        # 总销量
        total_sales_result = await db.execute(select(func.sum(Product.sales_count)))
        total_sales = total_sales_result.scalar() or 0

        return {
            "total_products": total_products,
            "active_products": active_products,
            "inactive_products": inactive_products,
            "low_stock_products": low_stock_products,
            "total_stock": total_stock,
            "total_sales": total_sales
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
