import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import User, Birthday, Category


@pytest.fixture
def db():
    """测试数据库会话"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def user(db):
    """创建测试用户"""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="$2b$12$test"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


class TestGiftRecommender:
    """礼物推荐引擎测试"""

    def test_recommend_by_age(self):
        """基于年龄推荐"""
        from app.services.gift_recommender import GiftRecommender

        # 儿童礼物
        gifts = GiftRecommender.recommend_by_age(5)
        assert len(gifts) > 0
        assert any("玩具" in g or "绘本" in g or "乐高" in g for g in gifts)

        # 青少年礼物
        gifts = GiftRecommender.recommend_by_age(15)
        assert len(gifts) > 0

        # 成年人礼物
        gifts = GiftRecommender.recommend_by_age(30)
        assert len(gifts) > 0

        # 老年人礼物
        gifts = GiftRecommender.recommend_by_age(65)
        assert len(gifts) > 0
        assert any("健康" in g or "保健" in g or "养生" in g for g in gifts)

    def test_recommend_by_relationship(self):
        """基于关系推荐"""
        from app.services.gift_recommender import GiftRecommender

        # 家人
        gifts = GiftRecommender.recommend_by_relationship("家人")
        assert len(gifts) > 0

        # 朋友
        gifts = GiftRecommender.recommend_by_relationship("朋友")
        assert len(gifts) > 0

        # 同事
        gifts = GiftRecommender.recommend_by_relationship("同事")
        assert len(gifts) > 0

        # 恋人
        gifts = GiftRecommender.recommend_by_relationship("恋人")
        assert len(gifts) > 0

        # 未知关系返回通用礼物
        gifts = GiftRecommender.recommend_by_relationship("unknown")
        assert len(gifts) > 0

    def test_recommend_by_budget(self):
        """基于预算推荐"""
        from app.services.gift_recommender import GiftRecommender

        # 低预算
        gifts = GiftRecommender.recommend_by_budget(50)
        assert len(gifts) > 0

        # 中预算
        gifts = GiftRecommender.recommend_by_budget(200)
        assert len(gifts) > 0

        # 高预算
        gifts = GiftRecommender.recommend_by_budget(1000)
        assert len(gifts) > 0

    def test_get_price_range(self):
        """获取价位范围"""
        from app.services.gift_recommender import GiftRecommender

        low = GiftRecommender.get_price_range("low")
        mid = GiftRecommender.get_price_range("medium")
        high = GiftRecommender.get_price_range("high")

        assert low[0] < mid[0] < high[0]

    def test_get_popular_gifts(self):
        """获取热门礼物"""
        from app.services.gift_recommender import GiftRecommender

        gifts = GiftRecommender.get_popular_gifts()
        assert len(gifts) > 0


class TestSmartRecommendation:
    """智能推荐测试"""

    def test_recommend_for_birthday(self, db, user):
        """为生日生成智能推荐"""
        from app.services.gift_recommender import GiftRecommender

        birthday = Birthday(
            name="张三",
            birth_date="1990-05-15",
            is_lunar=False,
            email="zhang@example.com",
            user_id=user.id
        )
        db.add(birthday)
        db.commit()

        recommendations = GiftRecommender.recommend_for_birthday(birthday)
        assert "by_age" in recommendations
        assert "by_category" in recommendations
        assert len(recommendations["by_age"]) > 0

    def test_recommend_with_existing_ideas(self, db, user):
        """基于已有礼物想法推荐"""
        from app.services.gift_recommender import GiftRecommender

        birthday = Birthday(
            name="李四",
            birth_date="1985-03-20",
            is_lunar=False,
            email="li@example.com",
            user_id=user.id,
            gift_idea="电动牙刷"
        )
        db.add(birthday)
        db.commit()

        similar = GiftRecommender.recommend_similar(birthday.gift_idea)
        assert len(similar) > 0

    def test_recommend_with_category(self, db, user):
        """基于分类推荐"""
        from app.services.gift_recommender import GiftRecommender
        from app.models import birthday_categories
        from app.crud import create_category

        cat = create_category(db, user.id, "家人", "#FF0000")
        birthday = Birthday(
            name="王五",
            birth_date="1995-06-15",
            is_lunar=False,
            email="wang@example.com",
            user_id=user.id
        )
        db.add(birthday)
        db.commit()
        db.execute(birthday_categories.insert().values(birthday_id=birthday.id, category_id=cat.id))
        db.commit()

        recommendations = GiftRecommender.recommend_for_birthday(birthday)
        assert "by_category" in recommendations
        assert len(recommendations["by_category"]) > 0


class TestGiftCategories:
    """礼物分类测试"""

    def test_get_categories(self):
        """获取礼物分类"""
        from app.services.gift_recommender import GiftRecommender

        categories = GiftRecommender.get_gift_categories()
        assert len(categories) > 0
        # 检查分类中包含特定关键词
        all_gifts = []
        for cat in categories:
            all_gifts.extend(GiftRecommender.get_category_gifts(cat))
        assert len(all_gifts) > 10  # 至少有10个礼物

    def test_get_category_gifts(self):
        """获取分类礼物"""
        from app.services.gift_recommender import GiftRecommender

        gifts = GiftRecommender.get_category_gifts("数码产品")
        assert len(gifts) > 0


class TestGiftOccasions:
    """礼物场合测试"""

    def test_get_occasions(self):
        """获取适用场合"""
        from app.services.gift_recommender import GiftRecommender

        occasions = GiftRecommender.get_occasions()
        assert "生日" in occasions

    def test_recommend_by_occasion(self):
        """基于场合推荐"""
        from app.services.gift_recommender import GiftRecommender

        gifts = GiftRecommender.recommend_by_occasion("生日")
        assert len(gifts) > 0
