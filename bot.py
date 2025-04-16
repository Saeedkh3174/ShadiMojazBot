import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils.executor import start_webhook
import re
import emoji
import os

API_TOKEN = '7763325161:AAEuBI8jE1bZLa8VQjR6KRgtey_3rhMNgV4'
AUTHORIZED_USER_ID = 7562729376
DESTINATION_CHANNEL = '@shadimojaz'
REPLACEMENT_ID = '🆔@ShadiMojaz'

# تنظیمات وب‌هوک
WEBHOOK_HOST = os.getenv("RENDER_EXTERNAL_URL", "")
WEBHOOK_PATH = f"/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.getenv("PORT", 8000))

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

premium_emoji_pattern = re.compile(r'<emoji[^>]+></emoji>')

# حذف کل خط‌هایی که شامل @ یا لینک هستند و حذف ایموجی‌های پرمیوم
def clean_text(text):
    lines = text.splitlines()
    cleaned_lines = []
    for line in lines:
        if '@' in line or 'http' in line:
            continue
        line = emoji.replace_emoji(line, replace='')
        line = premium_emoji_pattern.sub('', line)
        cleaned_lines.append(line.strip())
    cleaned = '\n'.join(cleaned_lines).strip()
    if REPLACEMENT_ID not in cleaned:
        cleaned += f"\n\n{REPLACEMENT_ID}"
    return cleaned

@dp.message_handler(lambda message: message.from_user.id == AUTHORIZED_USER_ID)
async def handle_message(message: types.Message):
    content_type = message.content_type

    if message.text:
        cleaned = clean_text(message.text)
        await bot.send_message(DESTINATION_CHANNEL, cleaned)

    elif message.caption:
        cleaned_caption = clean_text(message.caption)

        if content_type == 'photo':
            file_id = message.photo[-1].file_id
        elif hasattr(message, content_type):
            file_id = getattr(message, content_type).file_id
        else:
            file_id = None

        send_func = getattr(bot, f"send_{content_type}", None)
        if send_func and file_id:
            kwargs = {
                content_type: file_id,
                "chat_id": DESTINATION_CHANNEL,
                "caption": cleaned_caption
            }
            await send_func(**kwargs)
        else:
            await bot.send_message(DESTINATION_CHANNEL, "این نوع پیام پشتیبانی نمی‌شود.")

    else:
        if content_type == 'photo':
            file_id = message.photo[-1].file_id
        elif hasattr(message, content_type):
            file_id = getattr(message, content_type).file_id
        else:
            file_id = None

        send_func = getattr(bot, f"send_{content_type}", None)
        if send_func and file_id:
            kwargs = {
                content_type: file_id,
                "chat_id": DESTINATION_CHANNEL
            }
            await send_func(**kwargs)
        else:
            await bot.send_message(DESTINATION_CHANNEL, "این نوع پیام پشتیبانی نمی‌شود.")

async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(dp):
    await bot.delete_webhook()

if __name__ == '__main__':
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT
    )
