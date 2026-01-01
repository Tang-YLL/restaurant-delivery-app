"""
文件上传API路由
"""
import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.core.security import get_current_admin
from app.models import Admin
from app.schemas import MessageResponse

router = APIRouter(prefix="/admin/uploads", tags=["管理后台-文件上传"])

# 允许的图片扩展名
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

# 上传目录
UPLOAD_DIR = "public/images/products"


@router.post("/image", response_model=dict)
async def upload_product_image(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    上传商品图片

    支持的图片格式: jpg, jpeg, png, gif, webp
    最大文件大小: 5MB
    """
    try:
        # 验证文件扩展名
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件格式。支持的格式: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        # 创建上传目录
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        # 生成唯一文件名
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)

        # 保存文件
        contents = await file.read()

        # 验证文件大小（5MB）
        if len(contents) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="文件大小不能超过5MB")

        with open(file_path, "wb") as f:
            f.write(contents)

        # 返回图片URL路径
        image_url = f"/images/products/{unique_filename}"

        return {
            "url": image_url,
            "filename": unique_filename,
            "original_filename": file.filename,
            "size": len(contents)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")


@router.post("/images", response_model=List[dict])
async def upload_product_images(
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    批量上传商品图片

    支持一次上传多张图片
    """
    try:
        if len(files) > 10:
            raise HTTPException(status_code=400, detail="最多只能上传10张图片")

        uploaded_files = []
        for file in files:
            # 验证文件扩展名
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext not in ALLOWED_EXTENSIONS:
                continue

            # 创建上传目录
            os.makedirs(UPLOAD_DIR, exist_ok=True)

            # 生成唯一文件名
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            file_path = os.path.join(UPLOAD_DIR, unique_filename)

            # 保存文件
            contents = await file.read()

            # 验证文件大小（5MB）
            if len(contents) > 5 * 1024 * 1024:
                continue

            with open(file_path, "wb") as f:
                f.write(contents)

            # 返回图片URL路径
            image_url = f"/images/products/{unique_filename}"

            uploaded_files.append({
                "url": image_url,
                "filename": unique_filename,
                "original_filename": file.filename,
                "size": len(contents)
            })

        return uploaded_files

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")
