"""
评价相关API路由
"""
import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User
from app.schemas import (
    ReviewCreate, ReviewResponse, ProductRatingSummary,
    MessageResponse
)
from app.services import ReviewService

router = APIRouter(prefix="/reviews", tags=["评价管理"])


@router.post("", response_model=ReviewResponse)
async def create_review(
    review_data: ReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    提交评价

    为已完成订单的商品提交评价
    - 只有已完成订单可以评价
    - 每个订单每个商品只能评价一次
    - 评价后自动更新商品评分
    - 支持多图上传
    """
    try:
        service = ReviewService()

        # 创建评价
        review = await service.create_review(
            user_id=current_user.id,
            product_id=review_data.product_id,
            order_id=review_data.order_id,
            rating=review_data.rating,
            content=review_data.content,
            images=review_data.images,
            db=db
        )

        # 解析图片JSON字符串
        if review.images:
            try:
                review.images = json.loads(review.images)
            except:
                review.images = None

        return ReviewResponse.model_validate(review)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=List[ReviewResponse])
async def get_user_reviews(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取用户评价列表

    返回当前用户的评价列表
    """
    try:
        service = ReviewService()
        reviews = await service.get_user_reviews(
            user_id=current_user.id,
            page=page,
            page_size=page_size,
            db=db
        )

        # 解析图片JSON
        result = []
        for review in reviews:
            if review.images:
                try:
                    review.images = json.loads(review.images)
                except:
                    review.images = None
            result.append(ReviewResponse.model_validate(review))

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review_detail(
    review_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    获取评价详情

    返回指定评价的详细信息
    """
    try:
        service = ReviewService()
        review = await service.get_review_detail(review_id, db)

        if not review:
            raise HTTPException(status_code=404, detail="评价不存在")

        # 解析图片JSON
        if review.images:
            try:
                review.images = json.loads(review.images)
            except:
                review.images = None

        return ReviewResponse.model_validate(review)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/products/{product_id}", response_model=dict)
async def get_product_reviews(
    product_id: int,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取商品评价列表

    返回指定商品的评价列表和汇总信息
    """
    try:
        service = ReviewService()

        # 获取评价列表
        reviews, total = await service.get_product_reviews(
            product_id=product_id,
            page=page,
            page_size=page_size,
            db=db
        )

        # 获取评分汇总
        rating_summary = await service.get_product_rating_summary(product_id, db)

        # 计算总页数
        total_pages = (total + page_size - 1) // page_size

        # 解析图片JSON
        reviews_data = []
        for review in reviews:
            if review.images:
                try:
                    review.images = json.loads(review.images)
                except:
                    review.images = None
            reviews_data.append(ReviewResponse.model_validate(review))

        return {
            "reviews": reviews_data,
            "summary": rating_summary,
            "pagination": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/products/{product_id}/summary", response_model=ProductRatingSummary)
async def get_product_rating_summary(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    获取商品评分汇总

    返回商品的评分汇总信息(平均评分、评价数、评分分布)
    """
    try:
        service = ReviewService()
        summary = await service.get_product_rating_summary(product_id, db)

        return ProductRatingSummary(**summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
