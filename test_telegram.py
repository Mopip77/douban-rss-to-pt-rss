import os
from telegram_client import send_to_bot, is_session_exists
import asyncio

async def test_telegram():
    if os.getenv('TELEGRAM_BOT_ENABLE') == 'true' and is_session_exists():
        message = os.getenv('TELEGRAM_MESSAGE_TEMPLATE').format(title="123")
        print(message)
        await send_to_bot(message, wait_reply=False)

if __name__ == "__main__":
    asyncio.run(test_telegram())