import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.dispatcher.filters import CommandStart
import re
import os

API_TOKEN = os.getenv("BOT_TOKEN")  # اگه تو محیط render گذاشتی

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

ALLOWED_USER_ID = 7562729376  # آیدی عددی خودت
CHANNEL_LINK = "🆔@ShadiMojaz"

def clean_caption(caption):
    if not caption:
        return CHANNEL_LINK
    # حذف تمام @username ها
    caption = re.sub(r'@\w+', '', caption)
    # حذف لینک‌ها
    caption = re.sub(r'https?://\S+', '', caption)
    # اضافه کردن لینک کانال فقط یک‌بار
    if CHANNEL_LINK not in caption:
        caption += f"\n\n{CHANNEL_LINK}"
    return caption.strip()

@dp.message_handler(lambda message: message.from_user.id == ALLOWED_USER_ID)
async def handle_message(message: types.Message):
    try:
        caption = clean_caption(message.caption or message.text)
        if message.photo:
            await bot.send_photo(chat_id=message.chat.id, photo=message.photo[-1].file_id, caption=caption)
        elif message.video:
            await bot.send_video(chat_id=message.chat.id, video=message.video.file_id, caption=caption)
        else:
            await bot.send_message(chat_id=message.chat.id, text=caption)
    except Exception as e:
        logging.error(f"Error: {e}")

@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    await message.reply("✅ ربات مدیریت کانال فعال است.")

if __name__ == '__main__':
    try:
        executor.start_polling(dp, skip_updates=True)
    finally:
        # وقتی ربات متوقف میشه، session رو می‌بندیم
        import asyncio
        asyncio.run(bot.session.close())
