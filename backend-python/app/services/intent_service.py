"""意图识别服务（简化版本，修复user_id类型问题）"""

from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from collections import Counter
from app.models.question_intent import QuestionIntent
from app.services.question_classifier import QuestionClassifier
from app.services.llm_service import LLMService


class IntentRecognitionService:
    """意图识别服务"""
    
    def __init__(self, db: AsyncSession, llm_service: Optional[LLMService] = None):
        self.db = db
        self.classifier = QuestionClassifier()
        self.llm_service = llm_service
    
    def analyze_intent(self, question: str, user_id: Optional[int] = None) -> Dict[str, Any]:
        """分析意图（同步版本）"""
        classification = self.classifier.classify(question)
        
        intent_type_map = {
            "recommendation": "其他",
            "decision": "事业",
            "fortune": "财运"
        }
        intent_type = intent_type_map.get(classification.type, "其他")
        
        category = "iching"
        if any(kw in question for kw in ["塔罗", "tarot"]):
            category = "tarot"
        
        keywords = classification.keywords[:5] if classification.keywords else []
        enhanced_question = question
        
        return {
            "intent_type": intent_type,
            "confidence": int(classification.confidence * 100),
            "category": category,
            "subcategory": classification.type,
            "keywords": keywords,
            "enhanced_question": enhanced_question,
            "suggestions": [],
            "context": classification.context
        }
    
    async def save_intent(self, question: str, intent_result: Dict[str, Any], user_id: Optional[int] = None):
        """保存意图识别结果 - 修复了user_id类型转换问题"""
        # 🔧 修复：确保 user_id 是整数类型
        if user_id is not None:
            if isinstance(user_id, str):
                user_id = int(user_id)
        
        intent = QuestionIntent(
            user_id=user_id,
            original_question=question,
            intent_type=intent_result["intent_type"],
            confidence=intent_result["confidence"],
            category=intent_result["category"],
            subcategory=intent_result.get("subcategory", ""),
            enhanced_question=intent_result.get("enhanced_question", ""),
            keywords=intent_result.get("keywords", []),
            context=intent_result.get("context", {})
        )
        
        self.db.add(intent)
        await self.db.flush()
        return intent
    
    async def get_statistics(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """获取统计数据"""
        query = select(QuestionIntent)
        if user_id:
            query = query.where(QuestionIntent.user_id == user_id)
        
        result = await self.db.execute(query)
        intents = result.scalars().all()
        
        if not intents:
            return {
                "total_count": 0,
                "intent_distribution": {},
                "category_distribution": {},
                "avg_confidence": 0,
                "top_keywords": []
            }
        
        intent_types = [i.intent_type for i in intents]
        intent_distribution = dict(Counter(intent_types))
        
        categories = [i.category for i in intents]
        category_distribution = dict(Counter(categories))
        
        avg_confidence = sum(i.confidence for i in intents) / len(intents)
        
        all_keywords = []
        for i in intents:
            if i.keywords:
                all_keywords.extend(i.keywords)
        top_keywords = Counter(all_keywords).most_common(10)
        
        return {
            "total_count": len(intents),
            "intent_distribution": intent_distribution,
            "category_distribution": category_distribution,
            "avg_confidence": round(avg_confidence, 2),
            "top_keywords": top_keywords
        }
