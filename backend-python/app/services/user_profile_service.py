"""用户档案服务"""

from datetime import datetime, date
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user_profile import UserProfile
from app.schemas.user_profile import UserProfileCreate, UserProfileUpdate
from app.services.time_convert_service import TimeConvertService
from app.core.exceptions import NotFoundError, BadRequestError


class UserProfileService:
    """用户档案服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.time_service = TimeConvertService()
    
    async def get_profile(self, user_id: int) -> Optional[UserProfile]:
        """获取用户档案"""
        result = await self.db.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def create_profile(
        self,
        user_id: int,
        profile_data: UserProfileCreate
    ) -> UserProfile:
        """创建用户档案"""
        # 检查是否已存在
        existing = await self.get_profile(user_id)
        if existing:
            raise BadRequestError("用户档案已存在")
        
        # 创建档案
        profile = UserProfile(
            user_id=user_id,
            nickname=profile_data.nickname or '',
            avatar=profile_data.avatar or '',
            gender=profile_data.gender or '未知',
            birth_date=profile_data.birth_date,
            birth_time=profile_data.birth_time or '',
            birth_place=profile_data.birth_place or '',
            preferred_divination=profile_data.preferred_divination or 'iching',
            notification_enabled=profile_data.notification_enabled if profile_data.notification_enabled is not None else True,
            notification_time=profile_data.notification_time or '08:00',
            bio=profile_data.bio or '',
            interests=profile_data.interests or '',
        )
        
        # 计算命理信息
        if profile_data.birth_date:
            self._calculate_destiny_info(profile, profile_data.birth_date)
        
        self.db.add(profile)
        await self.db.flush()
        await self.db.refresh(profile)
        
        return profile
    
    async def update_profile(
        self,
        user_id: int,
        profile_data: UserProfileUpdate
    ) -> UserProfile:
        """更新用户档案"""
        profile = await self.get_profile(user_id)
        if not profile:
            raise NotFoundError("用户档案不存在")
        
        # 更新字段
        update_data = profile_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            if value is not None:
                setattr(profile, field, value)
        
        # 如果生日更新，重新计算命理信息
        if 'birth_date' in update_data and update_data['birth_date']:
            self._calculate_destiny_info(profile, update_data['birth_date'])
        
        await self.db.flush()
        await self.db.refresh(profile)
        
        return profile
    
    async def delete_profile(self, user_id: int) -> bool:
        """删除用户档案"""
        profile = await self.get_profile(user_id)
        if not profile:
            return False
        
        await self.db.delete(profile)
        await self.db.flush()
        return True
    
    def _calculate_destiny_info(self, profile: UserProfile, birth_date: date):
        """计算命理信息"""
        # 转换为农历 - 修复：传入year, month, day三个参数
        lunar_info = self.time_service.solar_to_lunar(birth_date.year, birth_date.month, birth_date.day)
        
        # 设置农历生日
        profile.lunar_birth = f"{lunar_info['lunar_year']}年{lunar_info['lunar_month_cn']}{lunar_info['lunar_day_cn']}"
        
        # 设置生肖
        profile.animal = lunar_info['animal']
        
        # 设置星座
        profile.zodiac_sign = lunar_info['astro']
        
        # 计算八字（简化版）
        profile.bazi = self._calculate_bazi(birth_date, profile.birth_time)
    
    def _calculate_bazi(self, birth_date: date, birth_time: str) -> str:
        """计算八字（简化版）"""
        # 天干地支
        tian_gan = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
        di_zhi = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        
        # 年柱（简化算法）
        year_offset = (birth_date.year - 1864) % 60
        year_gan = tian_gan[year_offset % 10]
        year_zhi = di_zhi[year_offset % 12]
        
        # 月柱（简化算法）
        month_offset = (birth_date.month - 1 + year_offset * 2) % 60
        month_gan = tian_gan[month_offset % 10]
        month_zhi = di_zhi[(birth_date.month + 1) % 12]
        
        # 日柱（简化算法）
        day_offset = (birth_date.toordinal() - date(1900, 1, 1).toordinal()) % 60
        day_gan = tian_gan[day_offset % 10]
        day_zhi = di_zhi[day_offset % 12]
        
        # 时柱（简化算法）
        if birth_time:
            try:
                hour = int(birth_time.split(':')[0])
                hour_zhi_index = (hour + 1) // 2 % 12
                hour_zhi = di_zhi[hour_zhi_index]
                hour_gan_offset = (day_offset * 2 + hour_zhi_index) % 10
                hour_gan = tian_gan[hour_gan_offset]
                
                return f"{year_gan}{year_zhi} {month_gan}{month_zhi} {day_gan}{day_zhi} {hour_gan}{hour_zhi}"
            except:
                pass
        
        return f"{year_gan}{year_zhi} {month_gan}{month_zhi} {day_gan}{day_zhi}"
    
    async def get_profile_summary(self, user_id: int) -> Dict[str, Any]:
        """获取用户档案摘要（用于运势生成）"""
        profile = await self.get_profile(user_id)
        
        if not profile:
            return {
                'animal': '',
                'zodiac_sign': '',
                'gender': '未知',
                'bazi': '',
            }
        
        return {
            'animal': profile.animal,
            'zodiac_sign': profile.zodiac_sign,
            'gender': profile.gender,
            'bazi': profile.bazi,
            'birth_date': profile.birth_date,
            'lunar_birth': profile.lunar_birth,
        }
