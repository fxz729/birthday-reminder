"""
礼物推荐引擎

基于以下维度提供礼物推荐：
- 年龄段
- 关系（家人/朋友/同事/客户）
- 预算
- 分类
- 场合
"""
from typing import List, Dict, Optional
from datetime import date


class GiftRecommender:
    """礼物推荐引擎"""

    # 礼物数据库
    GIFTS = {
        # 儿童礼物 (0-12岁)
        "儿童玩具": [
            "乐高 LEGO", "儿童绘本", "遥控汽车", "毛绒玩具",
            "儿童滑板车", "拼图", "儿童画板", "儿童乐器"
        ],
        "儿童用品": [
            "儿童书包", "儿童水杯", "护眼台灯", "儿童手表"
        ],
        # 青少年礼物 (13-18岁)
        "青少年数码": [
            "蓝牙耳机", "机械键盘", "游戏手柄", "平板电脑",
            "智能手表", "移动电源"
        ],
        "青少年潮流": [
            "潮牌服装", "运动鞋", "背包", "手办",
            "潮流配饰", "书籍"
        ],
        # 青年礼物 (19-35岁)
        "数码产品": [
            "无线蓝牙耳机", "智能手环", "便携音箱", "移动硬盘",
            "机械键盘", "无线充电器", "无人机", "电子书阅读器"
        ],
        "生活品质": [
            "香薰蜡烛", "咖啡机", "空气净化器", "颈椎按摩仪",
            "眼部按摩仪", "筋膜枪", "电动牙刷", "养生壶"
        ],
        "时尚配饰": [
            "手表", "钱包", "皮带", "丝巾", "围巾", "太阳镜", "首饰"
        ],
        "兴趣爱好": [
            "画材套装", "吉他/尤克里里", "摄影配件", "健身卡",
            "游戏卡带", "模型手办", "园艺工具", "烹饪器具"
        ],
        # 中年礼物 (36-55岁)
        "健康养生": [
            "按摩椅垫", "足浴盆", "燕窝", "人参", "阿胶",
            "破壁机", "净水器", "体检套餐"
        ],
        "品质生活": [
            "茶叶礼盒", "红酒", "丝巾", "皮具", "家用电器",
            "旅游套餐", "高尔夫体验", "SPA套餐"
        ],
        # 老年礼物 (55岁以上)
        "老年人健康": [
            "血压计", "血糖仪", "按摩仪", "助眠枕", "护膝",
            "钙片", "蛋白粉", "养生书籍"
        ],
        "老年人实用": [
            "老花镜", "放大镜", "助听器电池", "保暖内衣",
            "老人手机", "拐杖", "洗脚盆"
        ],
        # 通用礼物
        "水果礼盒": [
            "车厘子礼盒", "阳光玫瑰葡萄", "有机苹果礼盒",
            "榴莲", "进口水果篮"
        ],
        "鲜花": [
            "玫瑰花束", "百合花束", "向日葵花束", "永生花",
            "花篮", "蝴蝶兰"
        ],
        "食品礼盒": [
            "坚果礼盒", "巧克力礼盒", "蜂蜜礼盒", "零食大礼包",
            "月饼礼盒", "粽子礼盒", "腊味礼盒"
        ],
    }

    # 关系推荐
    RELATIONSHIP_RECOMMENDATIONS = {
        "家人": ["健康养生", "品质生活", "水果礼盒", "食品礼盒", "老年人健康"],
        "父母": ["健康养生", "品质生活", "老年人健康", "按摩仪", "体检套餐"],
        "配偶": ["时尚配饰", "鲜花", "数码产品", "生活品质", "浪漫晚餐"],
        "恋人": ["时尚配饰", "鲜花", "生活品质", "浪漫礼物", "兴趣爱好"],
        "朋友": ["兴趣爱好", "数码产品", "生活品质", "游戏相关", "潮流配饰"],
        "同事": ["食品礼盒", "办公用品", "茶叶", "咖啡", "坚果礼盒"],
        "客户": ["茶叶礼盒", "红酒", "皮具", "高档食品", "品质生活"],
        "老师": ["鲜花", "兴趣爱好", "时尚配饰", "茶叶", "生活品质"],
        "领导": ["皮具", "茶叶", "红酒", "高档食品", "品质生活"],
    }

    # 价格区间
    PRICE_RANGES = {
        "low": (0, 100),
        "medium": (100, 500),
        "high": (500, 2000),
        "luxury": (2000, 10000),
    }

    # 场合
    OCCASIONS = ["生日", "春节", "中秋", "情人节", "母亲节", "父亲节", "结婚纪念日", "升职", "毕业"]

    @classmethod
    def get_gift_categories(cls) -> List[str]:
        """获取礼物分类列表"""
        return list(cls.GIFTS.keys())

    @classmethod
    def get_category_gifts(cls, category: str) -> List[str]:
        """获取分类下的礼物"""
        return cls.GIFTS.get(category, [])

    @classmethod
    def get_occasions(cls) -> List[str]:
        """获取适用场合"""
        return cls.OCCASIONS

    @classmethod
    def get_price_range(cls, level: str) -> tuple:
        """获取价位范围"""
        return cls.PRICE_RANGES.get(level, (0, 500))

    @classmethod
    def recommend_by_age(cls, age: int) -> List[str]:
        """基于年龄推荐礼物"""
        if age < 0 or age > 120:
            return []

        if age <= 5:
            return cls._filter_by_price(cls.GIFTS.get("儿童玩具", []) + cls.GIFTS.get("儿童用品", []))
        elif age <= 12:
            return cls._filter_by_price(cls.GIFTS.get("儿童玩具", []) + cls.GIFTS.get("儿童用品", []))
        elif age <= 18:
            return cls._filter_by_price(cls.GIFTS.get("青少年数码", []) + cls.GIFTS.get("青少年潮流", []))
        elif age <= 35:
            return cls._filter_by_price(
                cls.GIFTS.get("数码产品", []) +
                cls.GIFTS.get("生活品质", []) +
                cls.GIFTS.get("时尚配饰", []) +
                cls.GIFTS.get("兴趣爱好", [])
            )
        elif age <= 55:
            return cls._filter_by_price(
                cls.GIFTS.get("健康养生", []) +
                cls.GIFTS.get("品质生活", []) +
                cls.GIFTS.get("数码产品", []) +
                cls.GIFTS.get("时尚配饰", [])
            )
        else:
            return cls._filter_by_price(
                cls.GIFTS.get("老年人健康", []) +
                cls.GIFTS.get("老年人实用", []) +
                cls.GIFTS.get("健康养生", [])
            )

    @classmethod
    def recommend_by_relationship(cls, relationship: str) -> List[str]:
        """基于关系推荐礼物"""
        categories = cls.RELATIONSHIP_RECOMMENDATIONS.get(relationship, ["食品礼盒", "水果礼盒"])
        gifts = []
        for cat in categories:
            gifts.extend(cls.GIFTS.get(cat, []))
        return list(set(gifts))  # 去重

    @classmethod
    def recommend_by_budget(cls, budget: float) -> List[str]:
        """基于预算推荐礼物"""
        gifts = []
        for category, items in cls.GIFTS.items():
            gifts.extend(items)
        return cls._filter_by_price(gifts)

    @classmethod
    def recommend_by_occasion(cls, occasion: str) -> List[str]:
        """基于场合推荐礼物"""
        if occasion == "生日":
            return cls.GIFTS.get("数码产品", []) + cls.GIFTS.get("生活品质", []) + cls.GIFTS.get("时尚配饰", [])
        elif occasion in ["春节", "中秋"]:
            return cls.GIFTS.get("食品礼盒", []) + cls.GIFTS.get("水果礼盒", []) + ["红包"]
        elif occasion == "情人节":
            return cls.GIFTS.get("鲜花", []) + ["首饰", "巧克力", "浪漫晚餐", "香水"]
        elif occasion in ["母亲节", "父亲节"]:
            return cls.GIFTS.get("健康养生", []) + cls.GIFTS.get("老年人健康", []) + ["鲜花"]
        else:
            return list(set([gift for gifts in cls.GIFTS.values() for gift in gifts]))

    @classmethod
    def get_popular_gifts(cls) -> List[str]:
        """获取热门礼物"""
        popular = []
        for cat in ["数码产品", "生活品质", "健康养生", "鲜花", "水果礼盒"]:
            popular.extend(cls.GIFTS.get(cat, [])[:3])
        return popular

    @classmethod
    def recommend_similar(cls, gift_idea: str, limit: int = 5) -> List[str]:
        """基于已有礼物想法推荐相似礼物"""
        if not gift_idea:
            return []

        # 关键词匹配
        keywords = {
            "电动": ["电动牙刷", "电动剃须刀", "电动按摩仪"],
            "按摩": ["按摩椅垫", "眼部按摩仪", "颈椎按摩仪", "筋膜枪"],
            "保健": ["燕窝", "人参", "阿胶", "蛋白粉", "钙片"],
            "数码": ["蓝牙耳机", "智能手表", "移动电源", "平板电脑"],
            "护肤": ["护肤品套装", "面膜", "美容仪", "香水"],
            "厨": ["破壁机", "空气炸锅", "咖啡机", "养生壶"],
            "运动": ["跑步机", "瑜伽垫", "哑铃", "健身卡"],
            "儿童": ["乐高", "绘本", "儿童手表", "遥控汽车"],
            "读书": ["电子书阅读器", "书籍", "Kindle", "书架"],
            "音乐": ["蓝牙音箱", "耳机", "吉他", "尤克里里"],
        }

        suggestions = []
        for keyword, items in keywords.items():
            if keyword in gift_idea:
                suggestions.extend(items)

        # 如果没有匹配，返回通用推荐
        if not suggestions:
            suggestions = cls.get_popular_gifts()

        return list(set(suggestions))[:limit]

    @classmethod
    def recommend_for_birthday(cls, birthday) -> Dict[str, List[str]]:
        """为生日生成综合推荐"""
        from datetime import date

        recommendations = {
            "by_age": [],
            "by_category": [],
            "popular": [],
            "similar": [],
        }

        # 计算年龄
        try:
            birth_date = date.fromisoformat(birthday.birth_date)
            age = date.today().year - birth_date.year
            if (date.today().month, date.today().day) < (birth_date.month, birth_date.day):
                age -= 1
        except (ValueError, TypeError):
            age = 30  # 默认

        # 年龄推荐
        recommendations["by_age"] = cls.recommend_by_age(age)

        # 分类推荐（如果有分类）
        if birthday.categories:
            for cat in birthday.categories:
                recommendations["by_category"].extend(
                    cls.recommend_by_relationship(cat.name)
                )

        # 热门推荐
        recommendations["popular"] = cls.get_popular_gifts()

        # 相似推荐（如果有已有想法）
        if birthday.gift_idea:
            recommendations["similar"] = cls.recommend_similar(birthday.gift_idea)

        # 去重
        for key in recommendations:
            recommendations[key] = list(set(recommendations[key]))[:10]

        return recommendations

    @classmethod
    def _filter_by_price(cls, gifts: List[str]) -> List[str]:
        """简单价格过滤（实际可对接电商API）"""
        # 这里简化处理，返回所有礼物
        # 实际实现可以对接京东/淘宝API获取实时价格
        return gifts

    @classmethod
    def get_gift_suggestions(cls, age: int, relationship: str = None, budget: float = None) -> Dict:
        """综合礼物建议"""
        suggestions = {
            "age_recommendations": cls.recommend_by_age(age),
            "relationship_recommendations": cls.recommend_by_relationship(relationship) if relationship else [],
            "popular": cls.get_popular_gifts(),
            "budget_options": {
                "low": cls.recommend_by_budget(100),
                "medium": cls.recommend_by_budget(500),
                "high": cls.recommend_by_budget(2000),
            }
        }
        return suggestions
