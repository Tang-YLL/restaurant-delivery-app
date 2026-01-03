"""
地址管理API路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User

router = APIRouter(prefix="/addresses", tags=["地址管理"])


class AddressCreate(BaseModel):
    """创建地址请求"""
    contact_name: str = Field(..., description="联系人姓名")
    contact_phone: str = Field(..., description="联系电话")
    province: str = Field(..., description="省份")
    city: str = Field(..., description="城市")
    district: str = Field(..., description="区县")
    detail_address: str = Field(..., description="详细地址")
    is_default: bool = Field(False, description="是否默认地址")
    address_type: str = Field("other", description="地址类型: home, company, other")


class AddressUpdate(BaseModel):
    """更新地址请求"""
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    detail_address: Optional[str] = None
    is_default: Optional[bool] = None
    address_type: Optional[str] = None


class AddressResponse(BaseModel):
    """地址响应"""
    id: str
    user_id: str
    contact_name: str
    contact_phone: str
    province: str
    city: str
    district: str
    detail_address: str
    is_default: bool
    address_type: str
    full_address: str

    class Config:
        from_attributes = True


@router.get("", response_model=List[AddressResponse])
async def get_addresses(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户地址列表

    返回当前用户的所有地址，按创建时间倒序
    """
    # TODO: 实现地址数据库模型和查询
    # 目前返回空列表，前端使用本地Hive存储
    return []


@router.post("", response_model=AddressResponse)
async def create_address(
    address_data: AddressCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    创建新地址

    保存用户地址，如果设置为默认地址，则取消其他默认地址
    """
    # TODO: 实现地址数据库模型和创建
    raise HTTPException(status_code=501, detail="地址功能暂未实现，请使用本地存储")


@router.put("/{address_id}", response_model=AddressResponse)
async def update_address(
    address_id: str,
    address_data: AddressUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新地址信息

    只能更新自己的地址
    """
    # TODO: 实现地址数据库模型和更新
    raise HTTPException(status_code=501, detail="地址功能暂未实现，请使用本地存储")


@router.delete("/{address_id}")
async def delete_address(
    address_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    删除地址

    只能删除自己的地址
    """
    # TODO: 实现地址数据库模型和删除
    raise HTTPException(status_code=501, detail="地址功能暂未实现，请使用本地存储")


@router.post("/{address_id}/default")
async def set_default_address(
    address_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    设置默认地址

    将指定地址设置为默认地址，取消其他默认地址
    """
    # TODO: 实现地址数据库模型和设置默认
    raise HTTPException(status_code=501, detail="地址功能暂未实现，请使用本地存储")
