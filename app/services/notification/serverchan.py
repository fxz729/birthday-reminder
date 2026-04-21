"""
ServerChan 推送发送器
"""
import httpx
from typing import Dict
import logging
from app.services.notification.base import NotificationBase

logger = logging.getLogger(__name__)


class ServerChanSender(NotificationBase):
    """ServerChan 推送发送器"""

    def __init__(self, sckey: str):
        self.sckey = sckey

    def render_content(self, name: str, extra_info: Dict) -> str:
        """渲染纯文本内容"""
        lines = [f"亲爱的{name}："]
        if extra_info.get("days_until", 0) == 0:
            if extra_info.get("solar_match") and extra_info.get("lunar_match"):
                lines.append("今天是您的阳历和农历生日，祝您生日快乐！🎉")
            elif extra_info.get("solar_match"):
                lines.append("今天是您的阳历生日，祝您生日快乐！🎉")
            else:
                lines.append("今天是您的农历生日，祝您农历生日快乐！🎉")
        else:
            if extra_info.get("solar_match") and extra_info.get("lunar_match"):
                lines.append(f"{extra_info['days_until']}天后是您的阳历和农历生日！")
            elif extra_info.get("solar_match"):
                lines.append(f"{extra_info['days_until']}天后是您的阳历生日！")
            else:
                lines.append(f"{extra_info['days_until']}天后是您的农历生日！")

        lines.append(f"年龄：{extra_info.get('age', 0)}岁")
        lines.append(f"生肖：{extra_info.get('zodiac', '')}")
        lines.append(f"星座：{extra_info.get('constellation', '')}")

        if extra_info.get("solar_term"):
            lines.append(f"节气：{extra_info['solar_term']}")
        if extra_info.get("lunar_festival"):
            lines.append(f"农历节日：{extra_info['lunar_festival']}")
        if extra_info.get("solar_festival"):
            lines.append(f"阳历节日：{extra_info['solar_festival']}")

        # 添加干支信息
        if extra_info.get("gz_year"):
            lines.append(f"今日干支：{extra_info['gz_year']}年 {extra_info['gz_month']}月 {extra_info['gz_day']}日")

        return "\n\n".join(lines)

    async def send(self, email: str, name: str, content: str, days_until: int, age: int, extra_info: Dict) -> bool:
        """发送 ServerChan 推送"""
        subject = self.generate_subject(name, age, days_until)

        # 使用 email 参数作为可选的额外收件人标识
        title = f"{subject} - {age}岁"

        data = {
            "title": title,
            "desp": content
        }

        url = f"https://sctapi.ftqq.com/{self.sckey}.send"

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, data=data)
                if resp.status_code == 200:
                    result = resp.json()
                    if result.get("code") == 0 or result.get("data", {}).get("errno") == 0:
                        logger.info(f"ServerChan 推送成功: {name}")
                        return True
                    else:
                        logger.error(f"ServerChan 推送失败: {name}, 响应: {result}")
                        return False
                else:
                    logger.error(f"ServerChan 推送失败: {name}, HTTP状态码: {resp.status_code}")
                    return False
        except Exception as e:
            logger.error(f"ServerChan 推送异常: {name}, 错误: {type(e).__name__}: {e}")
            return False
