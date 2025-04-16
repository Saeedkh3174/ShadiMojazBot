import asyncio
import logging
import re
import datetime
import pytz
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import os

API_TOKEN = os.getenv("API_TOKEN")  # توکن از متغیر محیطی
ALLOWED_USER_ID = int(os.getenv("ALLOWED_USER_ID"))  # آیدی عددی شما
CHANNEL_ID = "@ShadiMojaz"  # آیدی کانال مقصد

# لاگر
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    if message.from_user.id != ALLOWED_USER_ID:
        return
    await message.reply("به ربات مدیریت کانال خوش آمدید 😊")


@dp.message_handler(content_types=types.ContentTypes.ANY)
async def handle_message(message: types.Message):
    if message.from_user.id != ALLOWED_USER_ID:
        return

    # استخراج متن یا کپشن
    if message.caption:
        content = message.caption
    elif message.text:
        content = message.text
    else:
        content = ""

    # حذف لینک‌های t.me
    content = re.sub(r'https:\/\/t\.me\/[^\s]+', '', content)

    # حذف ایموجی و متن بعد از آن در خط لینک
    content = re.sub(r'[🔗📎].*', '', content)

    # بررسی و استخراج زمان‌بندی (فرمت 1120 یا 2330)
    time_match = re.search(r'\b([01]\d|2[0-3])[0-5]\d\b', content)
    send_time = None
    if time_match:
        time_str = time_match.group(0)
        content = content.replace(time_str, '')  # حذف زمان از متن
        now = datetime.datetime.now(pytz.timezone('Asia/Tehran'))
        target_time = now.replace(hour=int(time_str[:2]), minute=int(time_str[2:]), second=0, microsecond=0)
        if target_time < now:
            target_time += datetime.timedelta(days=1)
        send_time = target_time

    # افزودن لینک کانال مقصد
    content = content.strip() + '\n\n🔗 @ShadiMojaz'

    # تابع ارسال
    async def send_post():
        if message.photo:
            await bot.send_photo(CHANNEL_ID, message.photo[-1].file_id, caption=content)
        elif message.video:
            await bot.send_video(CHANNEL_ID, message.video.file_id, caption=content)
        elif message.text:
            await bot.send_message(CHANNEL_ID, content)
        else:
            await message.reply("نوع پیام پشتیبانی نمی‌شود.")

    # زمان‌بندی یا ارسال مستقیم
    if send_time:
        delay = (send_time - datetime.datetime.now(pytz.timezone('Asia/Tehran'))).total_seconds()
        await message.reply(f"⏰ پست زمان‌بندی شد برای ساعت {send_time.strftime('%H:%M')}")
        await asyncio.sleep(delay)
        await send_post()
    else:
        await send_post()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
