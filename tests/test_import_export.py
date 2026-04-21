import pytest
import csv
import io
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


class TestCSVExport:
    """CSV 导出测试"""

    def test_export_empty_birthdays(self, db, user):
        """导出空列表"""
        from app.services.import_export import export_birthdays_to_csv

        csv_data = export_birthdays_to_csv(db, user.id)
        lines = csv_data.strip().split('\n')

        # 只有标题行
        assert len(lines) == 1
        assert "name" in lines[0].lower()
        assert "birth_date" in lines[0].lower()

    def test_export_birthdays_with_headers(self, db, user):
        """导出包含数据"""
        from app.services.import_export import export_birthdays_to_csv
        from app.crud import create_birthday
        from app.schemas import BirthdayCreate

        create_birthday(db, BirthdayCreate(
            name="张三",
            birth_date="1990-05-15",
            is_lunar=False,
            email="zhang@example.com"
        ), user_id=user.id)

        create_birthday(db, BirthdayCreate(
            name="李四",
            birth_date="1985-03-20",
            is_lunar=True,
            email="li@example.com"
        ), user_id=user.id)

        csv_data = export_birthdays_to_csv(db, user.id)
        lines = csv_data.strip().split('\n')

        assert len(lines) == 3  # 标题 + 2条数据

    def test_export_only_user_birthdays(self, db, user):
        """只导出当前用户的数据"""
        from app.services.import_export import export_birthdays_to_csv
        from app.crud import create_birthday
        from app.schemas import BirthdayCreate

        # 当前用户
        create_birthday(db, BirthdayCreate(
            name="张三", birth_date="1990-01-01", is_lunar=False, email="zhang@example.com"
        ), user_id=user.id)

        # 另一个用户
        other_user = User(username="other", email="other@example.com", password_hash="hash")
        db.add(other_user)
        db.commit()
        create_birthday(db, BirthdayCreate(
            name="其他人", birth_date="1988-01-01", is_lunar=False, email="other@example.com"
        ), user_id=other_user.id)

        csv_data = export_birthdays_to_csv(db, user.id)
        assert "张三" in csv_data
        assert "其他人" not in csv_data


class TestCSVImport:
    """CSV 导入测试"""

    def test_import_valid_csv(self, db, user):
        """导入有效 CSV"""
        from app.services.import_export import import_birthdays_from_csv
        from app.schemas import BirthdayCreate

        csv_content = """name,birth_date,is_lunar,email
王五,1992-06-15,false,wang@example.com
赵六,1988-03-20,true,zhao@example.com"""

        count = import_birthdays_from_csv(db, user.id, csv_content)
        assert count == 2

        birthdays = db.query(Birthday).filter(Birthday.user_id == user.id).all()
        assert len(birthdays) == 2

    def test_import_with_category(self, db, user):
        """导入时创建分类"""
        from app.services.import_export import import_birthdays_from_csv
        from app.crud import create_category

        cat = create_category(db, user.id, "家人", "#FF0000")

        csv_content = """name,birth_date,is_lunar,email,category
张三,1990-01-01,false,zhang@example.com,家人"""

        count = import_birthdays_from_csv(db, user.id, csv_content)
        assert count == 1

        birthday = db.query(Birthday).filter(Birthday.name == "张三").first()
        assert birthday is not None
        assert cat in birthday.categories

    def test_import_creates_category_if_not_exists(self, db, user):
        """导入时自动创建不存在的分类"""
        from app.services.import_export import import_birthdays_from_csv

        csv_content = """name,birth_date,is_lunar,email,category
张三,1990-01-01,false,zhang@example.com,新分类"""

        count = import_birthdays_from_csv(db, user.id, csv_content)
        assert count == 1

        # 验证分类被创建
        cat = db.query(Category).filter(
            Category.name == "新分类",
            Category.user_id == user.id
        ).first()
        assert cat is not None

    def test_import_invalid_date_skipped(self, db, user):
        """无效日期行被跳过"""
        from app.services.import_export import import_birthdays_from_csv

        csv_content = """name,birth_date,is_lunar,email
张三,1990-05-15,false,zhang@example.com
无效,not-a-date,false,bad@example.com
李四,1985-03-20,true,li@example.com"""

        count = import_birthdays_from_csv(db, user.id, csv_content)
        assert count == 2  # 只有有效的被导入

    def test_import_empty_csv(self, db, user):
        """空 CSV 导入"""
        from app.services.import_export import import_birthdays_from_csv

        csv_content = """name,birth_date,is_lunar,email"""

        count = import_birthdays_from_csv(db, user.id, csv_content)
        assert count == 0


class TestVCardImport:
    """vCard 导入测试"""

    def test_parse_vcard_simple(self, db, user):
        """解析简单 vCard"""
        from app.services.import_export import parse_vcard

        vcard_content = """BEGIN:VCARD
VERSION:3.0
FN:张三
BDAY:1990-05-15
EMAIL:zhang@example.com
END:VCARD"""

        contacts = list(parse_vcard(vcard_content))
        assert len(contacts) == 1
        assert contacts[0]["name"] == "张三"
        assert contacts[0]["birth_date"] == "1990-05-15"
        assert contacts[0]["email"] == "zhang@example.com"

    def test_parse_vcard_multiple(self, db, user):
        """解析多个 vCard"""
        from app.services.import_export import parse_vcard

        vcard_content = """BEGIN:VCARD
VERSION:3.0
FN:张三
BDAY:1990-05-15
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:李四
BDAY:1985-03-20
END:VCARD"""

        contacts = list(parse_vcard(vcard_content))
        assert len(contacts) == 2

    def test_import_vcard_to_birthdays(self, db, user):
        """导入 vCard 到生日"""
        from app.services.import_export import parse_vcard, import_birthdays_from_contacts

        vcard_content = """BEGIN:VCARD
VERSION:3.0
FN:王五
BDAY:1992-06-15
EMAIL:wang@example.com
END:VCARD"""

        contacts = list(parse_vcard(vcard_content))
        count = import_birthdays_from_contacts(db, user.id, contacts)
        assert count == 1
