import asyncio
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
from telethon.tl.types import User

from config import Config

# 动态导入 socks 模块（仅在需要时导入）
try:
    import socks
except ImportError:
    socks = None

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TelegramBotClient:
    """Telegram Bot 客户端封装类"""
    
    def __init__(self):
        """初始化客户端"""
        Config.validate()
        
        # 获取代理配置
        proxy_config = Config.get_proxy_config()
        proxy = None
        
        if proxy_config:
            if socks is None:
                raise ImportError("使用代理需要安装 PySocks: pip install PySocks")
            
            proxy_type, host, port, username, password = proxy_config
            
            # 映射代理类型
            if proxy_type == 'socks5':
                proxy_type_enum = socks.SOCKS5
            elif proxy_type == 'socks4':
                proxy_type_enum = socks.SOCKS4
            elif proxy_type == 'http':
                proxy_type_enum = socks.HTTP
            else:
                raise ValueError(f"不支持的代理类型: {proxy_type}")
            
            # 构建代理配置
            proxy = (proxy_type_enum, host, port)
            if username and password:
                proxy = (proxy_type_enum, host, port, True, username, password)
            
            logger.info(f"使用代理: {proxy_type}://{host}:{port}")
        else:
            logger.info("未配置代理，使用直连")
        
        self.client = TelegramClient(
            Config.SESSION_NAME,
            Config.API_ID,
            Config.API_HASH,
            proxy=proxy
        )
        
        self.bot_entity = None
        self.waiting_for_reply = False
        self.last_message_time = None
        self.reply_message = None
        
    async def connect(self):
        """连接到 Telegram"""
        try:
            await self.client.start(phone=Config.PHONE_NUMBER)
            logger.info("成功连接到 Telegram")
            
            # 获取 bot 实体
            await self._get_bot_entity()
            
            # 注册消息处理器
            self._register_message_handler()
            
        except SessionPasswordNeededError:
            logger.error("需要两步验证密码，请在首次运行时手动完成验证")
            raise
        except Exception as e:
            logger.error(f"连接失败: {e}")
            raise
    
    async def _get_bot_entity(self):
        """获取目标 bot 的实体信息"""
        try:
            self.bot_entity = await self.client.get_entity(Config.BOT_USERNAME)
            if isinstance(self.bot_entity, User) and self.bot_entity.bot:
                logger.info(f"找到目标 bot: {self.bot_entity.username}")
            else:
                raise ValueError(f"{Config.BOT_USERNAME} 不是一个有效的 bot")
        except Exception as e:
            logger.error(f"无法找到 bot {Config.BOT_USERNAME}: {e}")
            raise
    
    def _register_message_handler(self):
        """注册消息处理器"""
        @self.client.on(events.NewMessage(from_users=self.bot_entity))
        async def handle_bot_reply(event):
            """处理 bot 回复"""
            if self.waiting_for_reply:
                # 检查消息时间，确保是我们发送消息后的回复
                if self.last_message_time and event.date > self.last_message_time:
                    self.reply_message = event.message.text
                    self.waiting_for_reply = False
                    logger.info(f"收到 bot 回复: {event.message.text[:50]}{'...' if len(event.message.text) > 50 else ''}")
                else:
                    # 调试信息：显示时间比较结果
                    if self.last_message_time:
                        logger.debug(f"忽略旧消息: 事件时间 {event.date}, 发送时间 {self.last_message_time}")
                    else:
                        logger.debug("忽略消息: 未设置发送时间")
    
    async def send_message_and_wait_reply(self, message: str) -> Optional[str]:
        """发送消息给 bot 并等待回复"""
        try:
            # 记录发送时间（使用 UTC 时间以匹配 Telegram 事件时间）
            self.last_message_time = datetime.now(timezone.utc)
            self.waiting_for_reply = True
            self.reply_message = None
            
            # 发送消息
            await self.client.send_message(self.bot_entity, message)
            logger.info(f"已发送消息: {message}")
            
            # 等待回复
            timeout_time = datetime.now(timezone.utc) + timedelta(seconds=Config.MESSAGE_TIMEOUT)
            
            while self.waiting_for_reply and datetime.now(timezone.utc) < timeout_time:
                await asyncio.sleep(0.1)  # 短暂休眠避免忙等待
            
            if self.reply_message:
                logger.info(f"收到回复: {self.reply_message}")
                return self.reply_message
            else:
                logger.warning(f"等待回复超时 ({Config.MESSAGE_TIMEOUT}秒)")
                return None
                
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            raise
        finally:
            self.waiting_for_reply = False
    
    async def send_message_only(self, message: str):
        """仅发送消息，不等待回复"""
        try:
            await self.client.send_message(self.bot_entity, message)
            logger.info(f"已发送消息: {message}")
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            raise
    
    async def disconnect(self):
        """断开连接"""
        if self.client.is_connected():
            await self.client.disconnect()
            logger.info("已断开 Telegram 连接")
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.disconnect()

def is_session_exists() -> bool:
    return os.path.exists(f"{Config.SESSION_NAME}.session")

async def login():
    if is_session_exists():
        return
    else:
        async with TelegramBotClient() as client:
            await client.connect()

async def send_to_bot(message: str, wait_reply: bool = True) -> Optional[str]:
    """便捷函数：发送消息给 bot"""
    async with TelegramBotClient() as client:
        if wait_reply:
            return await client.send_message_and_wait_reply(message)
        else:
            await client.send_message_only(message)
            return None