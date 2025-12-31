"""
管理后台评价管理API
"""
import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_admin
from app.models import Admin
from app.schemas import AdminReviewReplyRequest, MessageResponse, ReviewResponse
from app.services import AdminService

router = APIRouter(prefix="/admin/reviews", tags=["管理后台-评价管理"])


@router.get("", response_model=dict)
async def get_all_reviews(
    product_id: Optional[int] = Query(None, description="商品ID筛选"),
    rating: Optional[int] = Query(None, ge=1, le=5, description="评分筛选"),
    is_visible: Optional[bool] = Query(None, description="是否显示"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    获取全局评价列表

    管理员可以查看所有评价,支持筛选:
    - 按商品筛选
    - 按评分筛选
    - 按显示状态筛选
    - 分页查询
    """
    try:
        service = AdminService()
        reviews, total = await service.get_all_reviews(
            product_id=product_id,
            rating=rating,
            is_visible=is_visible,
            page=page,
            page_size=page_size,
            db=db
        )

        # 计算总页数
        total_pages = (total + page_size - 1) // page_size

        # 构建响应数据
        reviews_data = []
        for review in reviews:
            # 解析图片JSON
            images = None
            if review.images:
                try:
                    images = json.loads(review.images)
                except:
                    pass

            reviews_data.append({
                "id": review.id,
                "user_id": review.user_id,
                "user_phone": review.user.phone if review.user else None,
                "user_nickname": review.user.nickname if review.user else None,
                "product_id": review.product_id,
                "product_name": review.product.title if review.product else None,
                "rating": review.rating,
                "content": review.content,
                "images": images,
                "admin_reply": review.admin_reply,
                "is_visible": review.is_visible,
                "created_at": review.created_at,
                "updated_at": review.updated_at
            })

        return {
            "reviews": reviews_data,
            "pagination": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{review_id}", response_model=MessageResponse)
async def delete_review(
    review_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    删除评价

    管理员可以删除不当评价,记录操作日志
    """
    try:
        service = AdminService()

        # 查询评价信息
        from app.repositories import ReviewRepository
        from app.models import Review
        review_repo = ReviewRepository(Review, db)
        review = await review_repo.get_by_id(review_id)

        if not review:
            raise HTTPException(status_code=404, detail="评价不存在")

        # 删除评价
        success = await service.delete_review(review_id, db)

        if not success:
            raise HTTPException(status_code=404, detail="评价不存在")

        # 记录审计日志
        await service.log_action(
            admin_id=current_admin.id,
            action="delete_review",
            target_type="review",
            target_id=review_id,
            details={
                "product_id": review.product_id,
                "user_id": review.user_id,
                "rating": review.rating,
                "content": review.content
            },
            db=db
        )

        return MessageResponse(message="评价已删除", success=True)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{review_id}/reply", response_model=ReviewResponse)
async def reply_review(
    review_id: int,
    reply_request: AdminReviewReplyRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    管理员回复评价

    管理员可以对用户评价进行回复,记录操作日志
    """
    try:
        service = AdminService()

        # 查询评价信息
        from app.repositories import ReviewRepository
        from app.models import Review
        review_repo = ReviewRepository(Review, db)
        current_review = await review_repo.get_by_id(review_id)

        if not current_review:
            raise HTTPException(status_code=404, detail="评价不存在")

        # 回复评价
        review = await service.reply_review(review_id, reply_request.reply, db)

        if not review:
            raise HTTPException(status_code=404, detail="评价不存在")

        # 记录审计日志
        await service.log_action(
            admin_id=current_admin.id,
            action="reply_review",
            target_type="review",
            target_id=review_id,
            details={
                "product_id": review.product_id,
                "user_id": review.user_id,
                "reply": reply_request.reply
            },
            db=db
        )

        # 构建响应数据
        images = None
        if review.images:
            try:
                images = json.loads(review.images)
            except:
                pass

        response_data = {
            "id": review.id,
            "user_id": review.user_id,
            "product_id": review.product_id,
            "order_id": review.order_id,
            "rating": review.rating,
            "content": review.content,
            "images": images,
            "is_visible": review.is_visible,
            "created_at": review.created_at,
            "updated_at": review.updated_at,
            "user": {
                "id": review.user.id,
                "phone": review.user.phone,
                "nickname": review.user.nickname,
                "avatar": review.user.avatar,
                "is_active": review.user.is_active,
                "created_at": review.user.created_at,
                "updated_at": review.user.updated_at
            } if review.user else None
        }

        return ReviewResponse(**response_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{review_id}/visibility", response_model=MessageResponse)
async def toggle_review_visibility(
    review_id: int,
    is_visible: bool = Query(..., description="是否显示"),
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    切换评价显示状态

    管理员可以隐藏或显示评价,记录操作日志
    """
    try:
        from app.repositories import ReviewRepository
        from app.models import Review

        review_repo = ReviewRepository(Review, db)
        review = await review_repo.get_by_id(review_id)

        if not review:
            raise HTTPException(status_code=404, detail="评价不存在")

        old_visibility = review.is_visible
        review.is_visible = is_visible
        await db.commit()
        await db.refresh(review)

        # 记录审计日志
        await AdminService().log_action(
            admin_id=current_admin.id,
            action="toggle_review_visibility",
            target_type="review",
            target_id=review_id,
            details={
                "old_visibility": old_visibility,
                "new_visibility": is_visible,
                "product_id": review.product_id
            },
            db=db
        )

        action = "显示" if is_visible else "隐藏"
        return MessageResponse(message=f"评价已{action}", success=True)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
