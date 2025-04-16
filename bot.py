import logging
import re
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils import executor
from datetime import datetime, timedelta
import asyncio

API_TOKEN = '7763325161:AAEuBI8jE1bZLa8VQjR6KRgtey_3rhMNgV4'
OWNER_ID = 7562729376
CHANNEL_USERNAME = '@ShadiMojaz'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

pending_messages = {}

# تابعی برای حذف لینک‌ها و جایگزینی آیدی
def clean_message(text):
    # حذف لینک کانال‌های دیگر
    text = re.sub(r"https?://t\.me/\S+", "", text)
    text = re.sub(r"@\w+", "", text)  # حذف @آیدی‌ها
    text = re.sub(r"🆔@ShadiMojaz", "", text)  # حذف تکراری احتمالی
    return text.strip() + f"\n\n🆔{CHANNEL_USERNAME}"

@dp.message_handler(lambda message: message.from_user.id == OWNER_ID)
async def handle_message(message: Message):
    global pending_messages

    # اگر پیام عددی بود (برای زمان‌بندی)
    if message.text and message.text.isdigit():
        last_msg = pending_messages.get(message.from_user.id)
        if not last_msg:
            await message.reply("هیچ پیامی برای زمان‌بندی وجود ندارد.")
            return

        if message.text == '0':
            await bot.send_message(chat_id=CHANNEL_USERNAME, text=last_msg['text'], parse_mode='HTML')
        else:
            try:
                hour = int(message.text[:2])
                minute = int(message.text[2:])
                now = datetime.now()
                send_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                if send_time < now:
                    send_time += timedelta(days=1)
                delay = (send_time - now).total_seconds()
                await message.reply(f"پیام در ساعت {message.text} ارسال خواهد شد.")
                await asyncio.sleep(delay)
                await bot.send_message(chat_id=CHANNEL_USERNAME, text=last_msg['text'], parse_mode='HTML')
            except:
                await message.reply("فرمت زمان نادرست است. مثلاً 1120 برای ساعت 11:20")

        pending_messages.pop(message.from_user.id, None)
        return

    # گرفتن متن اصلی پیام (چه فوروارد چه معمولی)
    if message.forward_date:
        text = message.text or message.caption or ""
    else:
        text = message.text or message.caption or ""

    cleaned = clean_message(text)
    pending_messages[message.from_user.id] = {"text": cleaned}
    await message.reply("پیام ذخیره شد. لطفاً زمان ارسال را (مثل 1120 یا 0) وارد کنید.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
