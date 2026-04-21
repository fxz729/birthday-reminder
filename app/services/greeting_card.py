"""
贺卡生成服务

使用 Pillow 生成精美的生日贺卡图片，支持：
- 多种模板风格
- 多种配色方案
- 生肖/星座显示
- 自定义文字
"""
from io import BytesIO
from typing import Optional, Dict, List
from PIL import Image, ImageDraw, ImageFont
import os


class GreetingCardGenerator:
    """贺卡生成器"""

    # 可用模板
    TEMPLATES = {
        "classic": {"name": "经典风格", "width": 800, "height": 600},
        "modern": {"name": "现代风格", "width": 900, "height": 500},
        "simple": {"name": "简约风格", "width": 700, "height": 500},
    }

    # 配色方案
    COLOR_SCHEMES = {
        "default": {
            "bg_gradient_start": (102, 126, 234),  # #667eea
            "bg_gradient_end": (118, 75, 162),      # #764ba2
            "text_primary": (255, 255, 255),
            "text_secondary": (255, 255, 255, 180),
            "accent": (255, 215, 0),  # 金色
        },
        "pink": {
            "bg_gradient_start": (255, 105, 180),  # HotPink
            "bg_gradient_end": (255, 20, 147),        # DeepPink
            "text_primary": (255, 255, 255),
            "text_secondary": (255, 255, 255, 200),
            "accent": (255, 255, 255),
        },
        "blue": {
            "bg_gradient_start": (30, 144, 255),  # DodgerBlue
            "bg_gradient_end": (0, 191, 255),        # DeepSkyBlue
            "text_primary": (255, 255, 255),
            "text_secondary": (255, 255, 255, 200),
            "accent": (255, 255, 255),
        },
        "gold": {
            "bg_gradient_start": (255, 215, 0),  # Gold
            "bg_gradient_end": (255, 165, 0),      # Orange
            "text_primary": (139, 69, 19),
            "text_secondary": (139, 69, 19, 180),
            "accent": (255, 255, 255),
        },
        "green": {
            "bg_gradient_start": (46, 204, 113),  # Emerald
            "bg_gradient_end": (26, 188, 156),      # Turquoise
            "text_primary": (255, 255, 255),
            "text_secondary": (255, 255, 255, 200),
            "accent": (255, 255, 255),
        },
    }

    # 生肖 emoji/符号
    ZODIAC_MAP = {
        "鼠": "🐭", "牛": "🐮", "虎": "🐯", "兔": "🐰",
        "龙": "🐲", "蛇": "🐍", "马": "🐴", "羊": "🐑",
        "猴": "🐵", "鸡": "🐔", "狗": "🐶", "猪": "🐷",
    }

    # 星座 emoji
    CONSTELLATION_MAP = {
        "白羊座": "♈", "金牛座": "♉", "双子座": "♊",
        "巨蟹座": "♋", "狮子座": "♌", "处女座": "♍",
        "天秤座": "♎", "天蝎座": "♏", "射手座": "♐",
        "摩羯座": "♑", "水瓶座": "♒", "双鱼座": "♓",
    }

    def __init__(self):
        self._image: Optional[Image.Image] = None
        self._image_bytes: Optional[bytes] = None

    @classmethod
    def get_available_templates(cls) -> List[str]:
        """获取可用模板列表"""
        return list(cls.TEMPLATES.keys())

    @classmethod
    def get_color_schemes(cls) -> List[str]:
        """获取可用配色方案"""
        return list(cls.COLOR_SCHEMES.keys())

    @classmethod
    def template_exists(cls, template: str) -> bool:
        """检查模板是否存在"""
        return template in cls.TEMPLATES

    def create(
        self,
        name: str,
        age: int,
        template: str = "classic",
        color_scheme: str = "default",
        zodiac: str = None,
        constellation: str = None,
        output_path: str = None,
    ) -> Optional[str]:
        """创建贺卡

        Args:
            name: 生日人姓名
            age: 年龄
            template: 模板名称
            color_scheme: 配色方案
            zodiac: 生肖
            constellation: 星座
            output_path: 输出路径（None 则返回 bytes）

        Returns:
            输出路径或 None
        """
        if template not in self.TEMPLATES:
            template = "classic"

        if color_scheme not in self.COLOR_SCHEMES:
            color_scheme = "default"

        template_config = self.TEMPLATES[template]
        colors = self.COLOR_SCHEMES[color_scheme]

        width, height = template_config["width"], template_config["height"]

        # 创建渐变背景
        img = self._create_gradient_background(width, height, colors)
        self._image = img

        draw = ImageDraw.Draw(img)

        # 加载字体
        try:
            font_large = ImageFont.truetype("arial.ttf", 72)
            font_medium = ImageFont.truetype("arial.ttf", 48)
            font_small = ImageFont.truetype("arial.ttf", 28)
            font_tiny = ImageFont.truetype("arial.ttf", 20)
        except Exception:
            # 使用默认字体
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
            font_tiny = ImageFont.load_default()

        # 绘制装饰圆
        self._draw_decorations(draw, width, height, colors)

        # 绘制标题
        title = "🎂 生日快乐 🎂"
        title_bbox = draw.textbbox((0, 0), title, font=font_large)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(
            ((width - title_width) // 2, 40),
            title,
            font=font_large,
            fill=colors["text_primary"]
        )

        # 绘制姓名
        display_name = name if len(name) <= 10 else name[:10] + "..."
        name_bbox = draw.textbbox((0, 0), display_name, font=font_medium)
        name_width = name_bbox[2] - name_bbox[0]
        draw.text(
            ((width - name_width) // 2, 150),
            display_name,
            font=font_medium,
            fill=colors["accent"]
        )

        # 绘制年龄
        age_text = f"喜迎 {age} 周岁"
        age_bbox = draw.textbbox((0, 0), age_text, font=font_small)
        age_width = age_bbox[2] - age_bbox[0]
        draw.text(
            ((width - age_width) // 2, 220),
            age_text,
            font=font_small,
            fill=colors["text_secondary"]
        )

        # 绘制生肖/星座
        y_offset = 280
        if zodiac and zodiac in self.ZODIAC_MAP:
            zodiac_text = f"生肖: {self.ZODIAC_MAP[zodiac]} {zodiac}"
            z_bbox = draw.textbbox((0, 0), zodiac_text, font=font_small)
            z_width = z_bbox[2] - z_bbox[0]
            draw.text(
                ((width - z_width) // 2, y_offset),
                zodiac_text,
                font=font_small,
                fill=colors["text_secondary"]
            )
            y_offset += 40

        if constellation and constellation in self.CONSTELLATION_MAP:
            const_text = f"星座: {self.CONSTELLATION_MAP[constellation]} {constellation}"
            c_bbox = draw.textbbox((0, 0), const_text, font=font_small)
            c_width = c_bbox[2] - c_bbox[0]
            draw.text(
                ((width - c_width) // 2, y_offset),
                const_text,
                font=font_small,
                fill=colors["text_secondary"]
            )

        # 绘制祝福语
        blessing = "愿你天天开心，事事顺心！"
        b_bbox = draw.textbbox((0, 0), blessing, font=font_tiny)
        b_width = b_bbox[2] - b_bbox[0]
        draw.text(
            ((width - b_width) // 2, height - 80),
            blessing,
            font=font_tiny,
            fill=colors["text_secondary"]
        )

        # 保存
        if output_path:
            img.save(output_path, "PNG")
            self._image_bytes = None
            return output_path
        else:
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            self._image_bytes = buffer.getvalue()
            return None

    def _create_gradient_background(
        self, width: int, height: int, colors: Dict
    ) -> Image.Image:
        """创建渐变背景"""
        img = Image.new("RGB", (width, height))
        draw = ImageDraw.Draw(img)

        r1, g1, b1 = colors["bg_gradient_start"]
        r2, g2, b2 = colors["bg_gradient_end"]

        for y in range(height):
            ratio = y / height
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        return img

    def _draw_decorations(self, draw: ImageDraw.Draw, width: int, height: int, colors: Dict):
        """绘制装饰元素"""
        import math

        # 绘制圆形装饰
        for i in range(8):
            x = width * (0.1 + i * 0.1)
            y = 50 + (i % 3) * 30
            r = 5 + (i % 2) * 3
            color = colors["accent"] if isinstance(colors["accent"], tuple) else (255, 255, 255)
            alpha = 100 + i * 20
            draw.ellipse([x - r, y - r, x + r, y + r], fill=color[:3])

        # 底部波浪装饰
        wave_y = height - 30
        points = []
        for x in range(0, width + 20, 20):
            y = wave_y + int(10 * math.sin(x * 0.05))
            points.append((x, y))
        if len(points) >= 2:
            draw.line(points, fill=(255, 255, 255, 80), width=2)

    def get_image_bytes(self) -> Optional[bytes]:
        """获取图片字节数据"""
        return self._image_bytes

    def save(self, path: str):
        """保存到文件"""
        if self._image:
            self._image.save(path, "PNG")


def generate_card_from_birthday(birthday, color_scheme: str = "default") -> bytes:
    """从生日对象生成贺卡"""
    from datetime import date
    from app.services.lunar import get_zodiac, get_constellation, calculate_age

    # 计算年龄
    birth_date = date.fromisoformat(birthday.birth_date)
    age = calculate_age(birth_date)

    # 获取生肖和星座
    zodiac = get_zodiac(birth_date) if not birthday.is_lunar else None
    constellation = get_constellation(birth_date) if not birthday.is_lunar else None

    generator = GreetingCardGenerator()
    generator.create(
        name=birthday.name,
        age=age,
        zodiac=zodiac,
        constellation=constellation,
        color_scheme=color_scheme,
        output_path=None
    )
    return generator.get_image_bytes()


def generate_card_with_zodiac(name: str, age: int, zodiac: str, color_scheme: str = "gold") -> bytes:
    """生成带生肖的贺卡"""
    generator = GreetingCardGenerator()
    generator.create(
        name=name,
        age=age,
        zodiac=zodiac,
        color_scheme=color_scheme,
        output_path=None
    )
    return generator.get_image_bytes()


def generate_card_with_constellation(name: str, age: int, constellation: str, color_scheme: str = "blue") -> bytes:
    """生成带星座的贺卡"""
    generator = GreetingCardGenerator()
    generator.create(
        name=name,
        age=age,
        constellation=constellation,
        color_scheme=color_scheme,
        output_path=None
    )
    return generator.get_image_bytes()
