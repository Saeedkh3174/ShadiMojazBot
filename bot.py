import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import re
from datetime import datetime, timedelta
import pytz

API_TOKEN = '7763325161:AAEuBI8jE1bZLa8VQjR6KRgtey_3rhMNgV4'
ALLOWED_USER_ID = 7562729376
DEST_CHANNEL = '@ShadiMojaz'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

def clean_text(text):
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        if 'http' in line:
            # حذف لینک و ایموجی‌های اون خط
            line = re.sub(r'https?://\S+', '', line)
            line = re.sub(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]+', '', line)
        cleaned_lines.append(line)
    return '\n'.join(cleaned_lines).strip()

def extract_time(text):
    match = re.search(r'\b(\d{4})\b$', text.strip())
    if match:
        return match.group(1)
    return None

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    if message.from_user.id != ALLOWED_USER_ID:
        await message.reply("❌ شما اجازه استفاده از این ربات را ندارید.")
        return
    await message.reply("👋 به ربات مدیریت کانال خوش آمدید.")

@dp.message_handler(content_types=types.ContentType.ANY)
async def handle_forward(message: types.Message):
    if message.from_user.id != ALLOWED_USER_ID:
        return

    # دریافت متن پست فورواردی
    if not message.forward_from_chat or not message.caption:
        await message.reply("⚠️ لطفاً یک پست فوروارد شده با متن ارسال کنید.")
        return

    raw_text = message.caption
    media = message.photo or message.video or message.document

    # پردازش متن
    scheduled_time = extract_time(raw_text)
    cleaned_text = clean_text(raw_text)
    cleaned_text += f"\n\n🔗 {DEST_CHANNEL}"

    if scheduled_time:
        try:
            now = datetime.now(pytz.timezone("Asia/Tehran"))
            send_time = now.replace(hour=int(scheduled_time[:2]), minute=int(scheduled_time[2:]), second=0, microsecond=0)
            if send_time < now:
                send_time += timedelta(days=1)
            delay = (send_time - now).total_seconds()
            await message.reply(f"⏰ پست زمان‌بندی شد برای ارسال در ساعت {scheduled_time[:2]}:{scheduled_time[2:]}")
            await asyncio.sleep(delay)
        except Exception as e:
            await message.reply("❌ خطا در زمان‌بندی")

    try:
        if message.photo:
            await bot.send_photo(chat_id=DEST_CHANNEL, photo=message.photo[-1].file_id, caption=cleaned_text)
        elif message.video:
            await bot.send_video(chat_id=DEST_CHANNEL, video=message.video.file_id, caption=cleaned_text)
        elif message.document:
            await bot.send_document(chat_id=DEST_CHANNEL, document=message.document.file_id, caption=cleaned_text)
        else:
            await bot.send_message(chat_id=DEST_CHANNEL, text=cleaned_text)
    except Exception as e:
        await message.reply("❌ ارسال با خطا مواجه شد")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
