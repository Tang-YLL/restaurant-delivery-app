"""
管理后台商品管理API
"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pathlib import Path
import aiofiles
import uuid

from app.core.database import get_db
from app.core.security import get_current_admin
from app.models import Admin
from app.schemas import (
    AdminProductStockUpdate,
    AdminProductBatchOperation,
    MessageResponse,
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    NutritionFactsCreate,
    NutritionFactsResponse
)
from app.services import AdminService, ProductService
from app.services.product_detail_service import ProductDetailService
from app.repositories import ProductRepository
from app.models import Product
from app.utils.image_processor import ImageProcessor
from app.schemas import (
    ContentSectionCreate,
    ContentSectionUpdate,
    ContentSectionResponse,
    FullProductDetailResponse
)

router = APIRouter(prefix="/admin/products", tags=["管理后台-商品管理"])

# 图片上传目录配置
UPLOAD_DIR = Path("public/images/product_details")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.get("", response_model=dict)
async def get_products_list(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    category_id: Optional[int] = Query(None, description="分类ID"),
    is_active: Optional[bool] = Query(None, description="是否上架"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    获取商品列表（管理后台）

    支持关键词搜索、分类筛选、状态筛选、分页
    """
    try:
        from sqlalchemy import select, func, and_, or_
        from app.models import Product, Category

        skip = (page - 1) * page_size

        # 构建查询条件
        conditions = []

        if keyword:
            conditions.append(
                or_(
                    Product.title.ilike(f"%{keyword}%"),
                    Product.description.ilike(f"%{keyword}%")
                )
            )

        if category_id:
            conditions.append(Product.category_id == category_id)

        if is_active is not None:
            conditions.append(Product.is_active == is_active)

        # 查询商品列表
        query = select(Product).where(
            and_(*conditions) if conditions else True
        ).order_by(
            Product.created_at.desc()
        ).offset(skip).limit(page_size)

        result = await db.execute(query)
        products = result.scalars().all()

        # 查询总数
        count_query = select(func.count(Product.id)).where(
            and_(*conditions) if conditions else True
        )
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0

        # 构建响应数据
        products_data = []
        for product in products:
            # 获取分类信息
            category_result = await db.execute(
                select(Category).where(Category.id == product.category_id)
            )
            category = category_result.scalar_one_or_none()

            products_data.append({
                "id": product.id,
                "name": product.title,
                "title": product.title,
                "description": product.description,
                "price": float(product.price),
                "stock": product.stock,
                "sales": product.sales_count,
                "category": category.name if category else "",
                "categoryId": product.category_id,
                "image": product.local_image_path or product.image_url or "",
                "images": [product.local_image_path] if product.local_image_path else [],
                "status": "active" if product.is_active else "inactive",
                "is_active": product.is_active,
                "createdAt": product.created_at.isoformat() if product.created_at else "",
                "updatedAt": product.updated_at.isoformat() if product.updated_at else ""
            })

        # 计算总页数
        total_pages = (total + page_size - 1) // page_size

        return {
            "list": products_data,
            "total": total,
            "page": page,
            "pageSize": page_size,
            "totalPages": total_pages
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
        # 转换为字典，Product模型使用status字段，不需要is_available
        product_dict = product_data.model_dump()
        product = await product_service.create_product(
            product_data=product_dict,
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
            product_data=product_data.model_dump(exclude_unset=True),
            db=db
        )
        if not product:
            raise HTTPException(status_code=404, detail="商品不存在")
        return product
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新商品{product_id}失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"更新商品失败: {str(e)}")


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


@router.post("/{product_id}/details/images/upload")
async def upload_product_detail_image(
    product_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    上传商品详情图片

    功能：
    - 验证文件类型（只允许jpg/png）
    - 验证文件大小（最大5MB）
    - 自动压缩（质量85%，最大宽度800px）
    - 生成唯一文件名
    - 返回可访问的URL
    """
    try:
        # 验证文件类型
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="只允许上传图片文件")

        # 读取文件
        image_data = await file.read()

        # 验证大小
        if not ImageProcessor.validate_image(image_data):
            raise HTTPException(status_code=400, detail="图片大小不能超过5MB")

        # 验证格式
        img_format = ImageProcessor.get_image_format(image_data)
        if img_format not in ['jpeg', 'jpg', 'png']:
            raise HTTPException(status_code=400, detail="只支持JPG和PNG格式")

        # 处理图片（压缩、调整尺寸）
        processed_data, ext = ImageProcessor.process_uploaded_image(image_data)

        # 生成唯一文件名
        filename = f"{uuid.uuid4().hex}{ext}"
        filepath = UPLOAD_DIR / filename

        # 异步保存文件
        async with aiofiles.open(filepath, 'wb') as f:
            await f.write(processed_data)

        # 返回URL
        file_url = f"/images/product_details/{filename}"

        # 记录审计日志
        await AdminService().log_action(
            admin_id=current_admin.id,
            action="upload_product_detail_image",
            target_type="product",
            target_id=product_id,
            details={
                "filename": filename,
                "file_url": file_url,
                "original_size": len(image_data),
                "processed_size": len(processed_data),
                "format": img_format
            },
            db=db
        )

        return {
            "success": True,
            "message": "图片上传成功",
            "data": {
                "url": file_url,
                "filename": filename,
                "size": len(processed_data),
                "original_size": len(image_data),
                "compression_ratio": f"{(1 - len(processed_data) / len(image_data)) * 100:.1f}%"
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"图片上传失败: {str(e)}")


# ==================== 商品详情内容管理 ====================

detail_service = ProductDetailService()


@router.get("/{product_id}/details", response_model=FullProductDetailResponse)
async def get_product_detail_sections(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    获取商品的所有内容分区

    返回商品的所有内容分区和营养数据
    """
    try:
        # 获取完整商品详情（包含基本信息）
        full_details = await detail_service.get_full_details(product_id, db)

        # 提取管理后台需要的字段
        return FullProductDetailResponse(
            product_id=full_details["id"],
            content_sections=full_details.get("content_sections", []),
            nutrition_facts=full_details.get("nutrition_facts")
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{product_id}/details/sections", response_model=ContentSectionResponse, status_code=201)
async def create_content_section(
    product_id: int,
    section_data: ContentSectionCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    创建内容分区

    为商品创建一个新的内容分区，HTML内容会自动过滤XSS
    """
    try:
        section = await detail_service.save_content_section(product_id, section_data, db)
        return section
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{product_id}/details/sections/{section_id}", response_model=ContentSectionResponse)
async def update_content_section(
    product_id: int,
    section_id: int,
    section_data: ContentSectionUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    更新内容分区

    更新指定内容分区的内容，HTML内容会自动过滤XSS
    """
    try:
        section = await detail_service.update_content_section(section_id, section_data, db)

        if not section:
            raise HTTPException(status_code=404, detail="内容分区不存在")

        return section
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{product_id}/details/sections/{section_id}", response_model=MessageResponse)
async def delete_content_section(
    product_id: int,
    section_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    删除内容分区

    删除指定的内容分区
    """
    try:
        success = await detail_service.delete_content_section(section_id, db)

        if not success:
            raise HTTPException(status_code=404, detail="内容分区不存在")

        return MessageResponse(message="删除成功", success=True)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{product_id}/details/sections/batch")
async def batch_update_sections(
    product_id: int,
    sections: List[ContentSectionCreate],
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    批量保存多个内容分区

    删除该商品的所有旧分区，然后批量创建新的分区
    """
    try:
        created_sections = await detail_service.batch_update_sections(product_id, sections, db)

        # 记录审计日志
        await AdminService().log_action(
            admin_id=current_admin.id,
            action="batch_update_content_sections",
            target_type="product",
            target_id=product_id,
            details={
                "product_id": product_id,
                "sections_count": len(created_sections)
            },
            db=db
        )

        return {
            "success": True,
            "message": f"成功保存{len(created_sections)}个内容分区",
            "data": [ContentSectionResponse.model_validate(s) for s in created_sections]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 营养数据管理 ====================

@router.get("/{product_id}/details/nutrition")
async def get_nutrition_facts(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    获取商品营养数据

    返回指定商品的营养成分信息
    如果营养数据不存在，返回空对象而不是404错误
    """
    try:
        nutrition = await detail_service.get_nutrition_facts(product_id, db)

        if not nutrition:
            # 返回空的营养数据对象而不是404
            return {
                "product_id": product_id,
                "serving_size": None,
                "calories": 0,
                "protein": 0,
                "fat": 0,
                "carbohydrates": 0,
                "sodium": 0,
                "dietary_fiber": None,
                "sugars": None
            }

        return nutrition
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{product_id}/details/nutrition", response_model=NutritionFactsResponse)
async def create_or_update_nutrition_facts(
    product_id: int,
    nutrition_data: NutritionFactsCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    创建或更新营养数据

    如果商品已有营养数据则更新，否则创建新的
    """
    try:
        nutrition = await detail_service.create_or_update_nutrition_facts(
            product_id,
            nutrition_data,
            db
        )

        # 记录审计日志
        await AdminService().log_action(
            admin_id=current_admin.id,
            action="create_or_update_nutrition_facts",
            target_type="product",
            target_id=product_id,
            details={
                "product_id": product_id,
                "nutrition_data": nutrition_data.model_dump()
            },
            db=db
        )

        return nutrition
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{product_id}/details/nutrition", response_model=MessageResponse)
async def delete_nutrition_facts(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    删除营养数据

    删除指定商品的营养数据
    """
    try:
        success = await detail_service.delete_nutrition_facts(product_id, db)

        if not success:
            raise HTTPException(status_code=404, detail="营养数据不存在")

        # 记录审计日志
        await AdminService().log_action(
            admin_id=current_admin.id,
            action="delete_nutrition_facts",
            target_type="product",
            target_id=product_id,
            details={"product_id": product_id},
            db=db
        )

        return MessageResponse(message="营养数据已删除", success=True)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

