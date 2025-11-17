import os
from dotenv import load_dotenv
from typing import Optional, Tuple

# 加载环境变量
load_dotenv()

class Config:
    """配置类"""
    
    # Telegram API 配置
    API_ID = os.getenv('TELEGRAM_API_ID')
    API_HASH = os.getenv('TELEGRAM_API_HASH')
    PHONE_NUMBER = os.getenv('TELEGRAM_PHONE_NUMBER')
    
    # Bot 配置
    BOT_USERNAME = os.getenv('BOT_USERNAME')  # 目标 bot 的用户名
    
    # 代理配置
    PROXY_TYPE = os.getenv('PROXY_TYPE')  # 代理类型: socks5, socks4, http
    PROXY_HOST = os.getenv('PROXY_HOST')  # 代理服务器地址
    PROXY_PORT = os.getenv('PROXY_PORT')  # 代理端口
    PROXY_USERNAME = os.getenv('PROXY_USERNAME')  # 代理用户名（可选）
    PROXY_PASSWORD = os.getenv('PROXY_PASSWORD')  # 代理密码（可选）
    
    # 会话文件配置
    SESSION_NAME = 'config/telegram_bot_client'
    
    # 超时配置
    MESSAGE_TIMEOUT = 30  # 等待回复的超时时间（秒）
    
    @classmethod
    def get_proxy_config(cls) -> Optional[Tuple]:
        """获取代理配置
        
        Returns:
            代理配置元组 (proxy_type, addr, port, username, password) 或 None
        """
        if not cls.PROXY_TYPE or not cls.PROXY_HOST or not cls.PROXY_PORT:
            return None
        
        try:
            port = int(cls.PROXY_PORT)
        except (ValueError, TypeError):
            raise ValueError(f"代理端口必须是数字: {cls.PROXY_PORT}")
        
        # 验证代理类型
        valid_types = ['socks5', 'socks4', 'http']
        proxy_type = cls.PROXY_TYPE.lower()
        if proxy_type not in valid_types:
            raise ValueError(f"不支持的代理类型: {proxy_type}. 支持的类型: {', '.join(valid_types)}")
        
        return (
            proxy_type,
            cls.PROXY_HOST,
            port,
            cls.PROXY_USERNAME,
            cls.PROXY_PASSWORD
        )
    
    @classmethod
    def validate(cls):
        """验证配置是否完整"""
        missing_configs = []
        
        if not cls.API_ID:
            missing_configs.append('TELEGRAM_API_ID')
        if not cls.API_HASH:
            missing_configs.append('TELEGRAM_API_HASH')
        if not cls.PHONE_NUMBER:
            missing_configs.append('TELEGRAM_PHONE_NUMBER')
        if not cls.BOT_USERNAME:
            missing_configs.append('BOT_USERNAME')
            
        if missing_configs:
            raise ValueError(f"缺少配置项: {', '.join(missing_configs)}")
        
        return True