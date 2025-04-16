import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import asyncio
import re
from datetime import datetime, timedelta

API_TOKEN = '7763325161:AAEuBI8jE1bZLa8VQjR6KRgtey_3rhMNgV4'
AUTHORIZED_USER_ID = 7562729376
DESTINATION_CHANNEL = '@ShadiMojaz'
REPLACEMENT_ID = '🆔@ShadiMojaz'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

last_message = None

# حذف آی‌دی‌ها و جایگزینی
def clean_message(text):
    text = re.sub(r'🆔.*?(@\w+|\d+)', '', text)  # حذف آیدی فوروارد شده
    text = re.sub(r'@[\w_]+', '', text)  # حذف آیدی‌های متنی
    text = re.sub(r'https?://\S+', '', text)  # حذف لینک
    text = text.strip()

    # فقط یک بار آیدی کانال مقصد اضافه شود
    if REPLACEMENT_ID not in text:
        text += f"\n\n{REPLACEMENT_ID}"
    return text

# پیام شروع
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    if message.from_user.id != AUTHORIZED_USER_ID:
        return
    await message.reply("سلام! پیام مورد نظر رو بفرست، بعدش زمانش رو بفرست (مثل 2230 یا 0 برای ارسال فوری).")

# دریافت پیام اصلی
@dp.message_handler(lambda message: message.from_user.id == AUTHORIZED_USER_ID and not message.text.isdigit())
async def handle_main_message(message: types.Message):
    global last_message
    if message.forward_date or message.forward_from:
        content = clean_message(message.text or '')
    else:
        content = clean_message(message.text or '')
    last_message = content
    await message.reply("زمان ارسال رو وارد کن (مثل 2230 یا 0 برای بلافاصله).")

# دریافت زمان
@dp.message_handler(lambda message: message.from_user.id == AUTHORIZED_USER_ID and message.text.isdigit())
async def handle_time(message: types.Message):
    global last_message
    if not last_message:
        await message.reply("لطفاً اول پیام رو بفرست بعد زمان رو.")
        return

    time_str = message.text.strip()
    now = datetime.now()

    if time_str == "0":
        await bot.send_message(DESTINATION_CHANNEL, last_message)
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
            await bot.send_message(DESTINATION_CHANNEL, last_message)
        except:
            await message.reply("زمان وارد شده معتبر نیست.")

    last_message = None

if __name__ == '__main__':
    print("Starting bot...")
    executor.start_polling(dp, skip_updates=True)
