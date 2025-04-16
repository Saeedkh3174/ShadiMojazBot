import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import asyncio
import re
from datetime import datetime, timedelta

API_TOKEN = '7763325161:AAEuBI8jE1bZLa8VQjR6KRgtey_3rhMNgV4'
AUTHORIZED_USER_ID = 7562729376
DESTINATION_CHANNEL = '@shadimojaz'
REPLACEMENT_ID = '🆔@ShadiMojaz'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

last_message = None
last_media = None
last_caption = None

# حذف خطوط حاوی آیدی و لینک‌ها
def clean_text(text):
    lines = text.splitlines()
    cleaned_lines = []
    for line in lines:
        if re.search(r'@\w+', line) or re.search(r'https?://\S+', line):
            continue
        cleaned_lines.append(line.strip())
    cleaned = '\n'.join(cleaned_lines).strip()
    if REPLACEMENT_ID not in cleaned:
        cleaned += f"\n\n{REPLACEMENT_ID}"
    return cleaned

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    if message.from_user.id != AUTHORIZED_USER_ID:
        return
    await message.reply("سلام! پیام مورد نظر رو بفرست، بعدش زمانش رو بفرست (مثل 2230 یا 0 برای ارسال فوری).")

# دریافت همه نوع پیام
@dp.message_handler(lambda message: message.from_user.id == AUTHORIZED_USER_ID and not message.text.isdigit())
async def handle_main_message(message: types.Message):
    global last_message, last_media, last_caption

    if message.text:
        cleaned = clean_text(message.text)
        last_message = cleaned
        last_media = None
        last_caption = None
    elif message.caption:
        last_caption = clean_text(message.caption)
        last_media = message
        last_message = None
    else:
        last_media = message
        last_caption = ''
        last_message = None

    await message.reply("زمان ارسال رو وارد کن (مثل 2230 یا 0 برای بلافاصله).")

# دریافت زمان ارسال
@dp.message_handler(lambda message: message.from_user.id == AUTHORIZED_USER_ID and message.text.isdigit())
async def handle_time(message: types.Message):
    global last_message, last_media, last_caption

    if not last_message and not last_media:
        await message.reply("لطفاً اول پیام یا فایل رو بفرست بعد زمان رو.")
        return

    time_str = message.text.strip()
    now = datetime.now()

    async def send_to_channel():
        if last_message:
            await bot.send_message(DESTINATION_CHANNEL, last_message)
        elif last_media:
            content_type = last_media.content_type
            send_func = getattr(bot, f"send_{content_type}", None)
            if send_func:
                file_id = getattr(last_media, content_type).file_id
                await send_func(chat_id=DESTINATION_CHANNEL, **{content_type: file_id}, caption=last_caption or None)
            else:
                await bot.send_message(DESTINATION_CHANNEL, "نوع فایل پشتیبانی نمی‌شود.")

    if time_str == "0":
        await send_to_channel()
        await message.reply("پیام بلافاصله ارسال شد.")
    else:
        try:
            hour = int(time_str[:2])
            minute = int(time_str[2:])
            send_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if send_time < now:
                send_time += timedelta(days=1)
            wait_time = (send_time - now).total_seconds()
            await message.reply(f"پیام در ساعت {hour:02d}:{minute:02d} ارسال خواهد شد.")
            await asyncio.sleep(wait_time)
            await send_to_channel()
        except:
            await message.reply("زمان وارد شده معتبر نیست.")

    last_message = None
    last_media = None
    last_caption = None

# پیام خوش‌آمدگویی هنگام روشن شدن ربات
async def on_startup(dp):
    await bot.send_message(AUTHORIZED_USER_ID, "✅ ربات روشن شد و آماده دریافت پیام‌هاته!")

if __name__ == '__main__':
    print("✅ ربات داره روشن میشه...")
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
