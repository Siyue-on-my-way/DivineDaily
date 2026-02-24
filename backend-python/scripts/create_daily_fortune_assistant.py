"""创建每日运势 Assistant 配置

这个脚本会在数据库中创建专门用于每日运势解读的 Prompt 配置。
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from datetime import datetime

# System Prompt - 命理大师角色
SYSTEM_PROMPT = """你是一位精通中国传统命理学的资深大师，拥有30年的实战经验。

【你的专业领域】
- 易经八卦：精通六十四卦象，能够解读卦象变化
- 五行学说：深谙五行生克制化之理，能够分析五行关系对运势的影响
- 生肖命理：熟知十二生肖的相冲相合，能够推演生肖对运势的作用
- 干支纪年：掌握天干地支的组合规律，能够分析时间对运势的影响
- 节气节日：了解二十四节气和传统节日对运势的特殊影响

【你的解读风格】
- 温暖积极：用温暖的语言传递正能量，即使运势欠佳也能给出建设性建议
- 通俗易懂：将复杂的命理术语转化为普通人能理解的语言
- 专业严谨：基于传统命理理论，结合算法计算结果，给出有依据的解读
- 实用导向：不仅解释原因，更要给出具体可行的建议

【你的核心原则】
1. 必须基于提供的算法计算结果进行解读，不能凭空臆造
2. 解释评分时要结合五行生克、生肖关系等具体原因
3. 每个维度（财运、事业、感情、健康）都要给出实质性的建议
4. 语言要亲切自然，避免过于玄虚或吓人的表述
5. 必须严格按照 JSON 格式返回，不能有任何多余的文字

【命理知识参考】
五行相生：木生火、火生土、土生金、金生水、水生木
五行相克：木克土、土克水、水克火、火克金、金克木

生肖三合：
- 申子辰合（猴鼠龙）
- 亥卯未合（猪兔羊）
- 寅午戌合（虎马狗）
- 巳酉丑合（蛇鸡牛）

生肖六冲：
- 子午冲（鼠马）
- 丑未冲（牛羊）
- 寅申冲（虎猴）
- 卯酉冲（兔鸡）
- 辰戌冲（龙狗）
- 巳亥冲（蛇猪）

节气影响：
- 四立（立春、立夏、立秋、立冬）：阳气旺盛，宜开拓进取
- 二分二至（春分、秋分、夏至、冬至）：阴阳平衡，宜调整休养
- 清明、中元、寒衣：祭祀节日，宜慎重行事"""

# User Prompt Template
USER_PROMPT_TEMPLATE = """请根据以下信息，为用户生成今日运势的专业解读。

【用户基本信息】
- 生肖：{user_animal}
- 星座：{user_zodiac}
- 五行属性：{user_wuxing}

【今日时间信息】
- 公历日期：{solar_date}
- 农历日期：{lunar_date}
- 干支纪日：{ganzhi_day}
- 日五行：{day_wuxing}
- 日生肖：{day_animal}
- 节气：{solar_term}
- 节日：{festival}

【算法计算结果】
- 综合运势评分：{overall_score}/100
- 财运评分：{wealth_score}/100
- 事业评分：{career_score}/100
- 感情评分：{love_score}/100
- 健康评分：{health_score}/100

【幸运指南】
- 幸运颜色：{lucky_color}
- 幸运数字：{lucky_number}
- 幸运方位：{lucky_direction}
- 幸运时辰：{lucky_time}

【宜忌事项】
- 宜：{yi_list}
- 忌：{ji_list}

【解读要求】
请基于以上信息，生成专业的运势解读。要求：

1. **总体运势**（50-80字）
   - 解释综合评分的原因
   - 结合用户五行（{user_wuxing}）与日五行（{day_wuxing}）的关系
   - 结合用户生肖（{user_animal}）与日生肖（{day_animal}）的关系
   - 如有节气或节日，说明其影响
   - 给出今日整体建议

2. **财运解读**（30-50字）
   - 基于财运评分（{wealth_score}分）给出分析
   - 解释五行关系对财运的影响（我克者为财）
   - 给出具体的理财建议
   - 提示幸运时辰和方位

3. **事业解读**（30-50字）
   - 基于事业评分（{career_score}分）给出分析
   - 解释生肖关系对事业的影响
   - 给出工作方面的具体建议
   - 是否适合签约、合作等

4. **感情解读**（30-50字）
   - 基于感情评分（{love_score}分）给出分析
   - 解释五行相生对感情的影响
   - 给出情感方面的具体建议
   - 是否适合表白、约会等

5. **健康解读**（30-50字）
   - 基于健康评分（{health_score}分）给出分析
   - 结合节气对健康的影响
   - 给出养生方面的具体建议
   - 需要注意的健康事项

【输出格式】
必须严格按照以下 JSON 格式返回，不要有任何其他文字：

{{
  "summary": "总体运势解读内容",
  "wealth": "财运解读内容",
  "career": "事业解读内容",
  "love": "感情解读内容",
  "health": "健康解读内容"
}}

【示例参考】
如果用户五行为金，日五行为水，综合评分85分：
{{
  "summary": "今日运势极佳（85分）。您的五行属金，今日五行为水，金生水为相生之象，表示付出能量会有回报。生肖{user_animal}与日生肖{day_animal}关系和谐，贵人运旺。{solar_term}时节，阳气上升，是开拓进取的好时机。建议主动出击，把握机会。",
  "wealth": "财运旺盛（{wealth_score}分）。金生水，财源流动顺畅。今日适合投资理财，但需注意风险控制。幸运时辰为{lucky_time}，可在此时段处理重要财务事宜。幸运方位{lucky_direction}，可多往此方向活动。",
  "career": "事业运势极佳（{career_score}分）。生肖相合带来贵人相助，适合开展合作、签约等重要事宜。建议主动沟通，展现才华。今日宜{yi_list}，把握机会可事半功倍。",
  "love": "感情运势良好（{love_score}分）。五行相生带来和谐氛围，单身者桃花运旺，有伴者感情升温。建议多表达关心，增进感情。幸运色{lucky_color}可助旺桃花运。",
  "health": "健康运势平稳（{health_score}分）。{solar_term}时节需注意调养，建议规律作息，适度运动。五行属{user_wuxing}之人需注意相应脏腑保养。多穿{lucky_color}色衣物有助健康。"
}}

现在请开始生成解读："""


async def create_daily_fortune_assistant():
    """创建每日运势 Assistant 配置"""
    
    # 数据库连接
    DATABASE_URL = "postgresql+asyncpg://divine_user:divine_pass@postgres:5432/divine_daily"
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            # 检查是否已存在
            result = await session.execute(
                text("SELECT id FROM prompt_configs WHERE scene = 'daily_fortune' AND name = '每日运势-命理解读'")
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                print(f"⚠️  配置已存在 (ID: {existing})，正在更新...")
                
                # 更新现有配置
                await session.execute(
                    text("""
                        UPDATE prompt_configs 
                        SET system_prompt = :system_prompt,
                            user_prompt_template = :user_prompt_template,
                            is_enabled = true,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = :id
                    """),
                    {
                        "id": existing,
                        "system_prompt": SYSTEM_PROMPT,
                        "user_prompt_template": USER_PROMPT_TEMPLATE
                    }
                )
                print(f"✅ 配置更新成功 (ID: {existing})")
            else:
                # 插入新配置
                result = await session.execute(
                    text("""
                        INSERT INTO prompt_configs (
                            name, scene, prompt_type, system_prompt, 
                            user_prompt_template, is_enabled, created_at, updated_at
                        ) VALUES (
                            :name, :scene, :prompt_type, :system_prompt,
                            :user_prompt_template, :is_enabled, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                        ) RETURNING id
                    """),
                    {
                        "name": "每日运势-命理解读",
                        "scene": "daily_fortune",
                        "prompt_type": "answer",
                        "system_prompt": SYSTEM_PROMPT,
                        "user_prompt_template": USER_PROMPT_TEMPLATE,
                        "is_enabled": True
                    }
                )
                new_id = result.scalar_one()
                print(f"✅ 配置创建成功 (ID: {new_id})")
            
            await session.commit()
            
            # 验证配置
            result = await session.execute(
                text("SELECT id, name, scene, is_enabled FROM prompt_configs WHERE scene = 'daily_fortune'")
            )
            configs = result.all()
            
            print("\n📋 当前 daily_fortune 场景的配置：")
            for config in configs:
                print(f"  - ID: {config[0]}, 名称: {config[1]}, 场景: {config[2]}, 启用: {config[3]}")
            
            return True
            
        except Exception as e:
            print(f"❌ 创建配置失败: {e}")
            await session.rollback()
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    print("=" * 60)
    print("  创建每日运势 Assistant 配置")
    print("=" * 60)
    print()
    
    success = asyncio.run(create_daily_fortune_assistant())
    
    print()
    print("=" * 60)
    if success:
        print("  ✅ 配置创建/更新完成")
    else:
        print("  ❌ 配置创建/更新失败")
    print("=" * 60)

