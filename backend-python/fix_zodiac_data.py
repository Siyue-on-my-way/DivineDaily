"""修复数据库中所有用户的生肖和农历信息"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import select
from app.core.database import async_session_maker
from app.models.user_profile import UserProfile
from app.utils.calendar import CalendarConverter


async def fix_user_zodiac():
    """修复所有用户的生肖和农历信息"""
    async with async_session_maker() as session:
        # 查询所有有出生日期的用户档案
        result = await session.execute(
            select(UserProfile).where(
                UserProfile.birth_date.isnot(None)
            )
        )
        profiles = result.scalars().all()
        
        print(f"找到 {len(profiles)} 个需要修复的用户档案")
        
        updated_count = 0
        error_count = 0
        
        for profile in profiles:
            try:
                birth_date = profile.birth_date
                
                # 重新计算农历信息
                lunar_info = CalendarConverter.solar_to_lunar(
                    birth_date.year,
                    birth_date.month,
                    birth_date.day
                )
                
                old_animal = profile.animal
                new_animal = lunar_info['animal']
                
                # 构建农历生日字符串
                lunar_birth_str = f"{lunar_info['lunar_year']}年{lunar_info['lunar_month_cn']}{lunar_info['lunar_day_cn']}"
                
                # 构建八字字符串
                bazi_str = f"{lunar_info['ganzhi_year']}年 {lunar_info['ganzhi_month']}月 {lunar_info['ganzhi_day']}日"
                
                # 更新用户档案信息
                profile.lunar_birth = lunar_birth_str
                profile.animal = new_animal
                profile.zodiac_sign = lunar_info['astro']
                profile.bazi = bazi_str
                
                if old_animal != new_animal:
                    print(f"用户 {profile.user_id}: "
                          f"{birth_date} "
                          f"生肖从 '{old_animal}' 修正为 '{new_animal}' "
                          f"(农历{lunar_info['lunar_year']}年)")
                    updated_count += 1
                else:
                    print(f"用户 {profile.user_id}: 生肖正确 ({new_animal})")
                
            except Exception as e:
                print(f"处理用户档案 {profile.user_id} 时出错: {e}")
                error_count += 1
                continue
        
        # 提交更改
        await session.commit()
        
        print(f"\n修复完成:")
        print(f"  总档案数: {len(profiles)}")
        print(f"  已修正: {updated_count}")
        print(f"  无需修正: {len(profiles) - updated_count - error_count}")
        print(f"  错误: {error_count}")


if __name__ == "__main__":
    print("开始修复用户生肖数据...")
    asyncio.run(fix_user_zodiac())
    print("修复完成！")
