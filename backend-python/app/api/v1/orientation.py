"""方位推荐API路由"""

from fastapi import APIRouter, HTTPException
from app.services.orientation_service import (
    OrientationService,
    OrientationRecommendRequest,
    OrientationRecommendResponse
)

router = APIRouter()


@router.post("/recommend", response_model=OrientationRecommendResponse)
async def recommend_orientation(request: OrientationRecommendRequest):
    """
    推荐方位
    
    根据问题类型和内容，推荐最适合的方位。
    
    - **version**: CN（中国版-八卦）或 Global（国际版-塔罗）
    - **event_type**: 事件类型（decision/career/relationship/fortune/knowledge）
    - **question**: 用户问题
    - **user_id**: 用户ID（可选）
    """
    try:
        response = OrientationService.recommend_orientation(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to recommend orientation: {str(e)}")


@router.get("/detail/{key}")
async def get_orientation_detail(key: str, version: str = "CN"):
    """
    获取方位详细信息
    
    - **key**: 方位键（E/SE/S/SW/W/NW/N/NE）
    - **version**: CN（中国版）或 Global（国际版）
    """
    try:
        detail = OrientationService.get_orientation_detail(key, version)
        if not detail:
            raise HTTPException(status_code=404, detail="Orientation not found")
        return detail
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get orientation detail: {str(e)}")


@router.get("/all")
async def get_all_orientations(version: str = "CN"):
    """
    获取所有方位信息
    
    - **version**: CN（中国版-八卦）或 Global（国际版-塔罗）
    """
    try:
        orientations = OrientationService.get_all_orientations(version)
        return {
            "version": version,
            "orientations": orientations,
            "count": len(orientations)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get orientations: {str(e)}")

