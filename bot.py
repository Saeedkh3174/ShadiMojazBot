import re
import logging
from aiogram import Bot, Dispatcher, types, executor

API_TOKEN = "7763325161:AAEuBI8jE1bZLa8VQjR6KRgtey_3rhMNgV4"

# فقط اجازه به آیدی عددی تو
ALLOWED_USER_ID = 7562729376

# آیدی جایگزین و لینک کانال
CUSTOM_ID = "🆔@ShadiMojaz"
CHANNEL_LINK = "\n\n📢 @ShadiMojaz"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# تابع حذف لینک و آیدی‌های اضافی
def clean_text(text):
    # حذف آیدی‌های قبلی و لینک‌های کانال
    text = re.sub(r'@[\w\d_]+', '', text)
    text = re.sub(r'https://t\.me/[\w\d_]+', '', text)
    # حذف لینک‌های باقی‌مونده
    text = re.sub(r'https?://\S+', '', text)
    # حذف فاصله‌های اضافی
    text = re.sub(r'\n{2,}', '\n', text).strip()
    return text + '\n\n' + CUSTOM_ID + CHANNEL_LINK

# هندل پیام‌ها (فوروارد و معمولی)
@dp.message_handler(lambda message: message.from_user.id == ALLOWED_USER_ID)
async def handle_all_messages(message: types.Message):
    try:
        if message.text:
            cleaned = clean_text(message.text)
            await bot.send_message(message.chat.id, cleaned)
        elif message.caption:
            cleaned = clean_text(message.caption)
            if message.photo:
                await bot.send_photo(message.chat.id, photo=message.photo[-1].file_id, caption=cleaned)
            elif message.video:
                await bot.send_video(message.chat.id, video=message.video.file_id, caption=cleaned)
        else:
            await message.answer("این نوع پیام پشتیبانی نمی‌شود.")
    except Exception as e:
        logging.error(f"خطا در ارسال پیام: {e}")

@dp.message_handler()
async def reject_others(message: types.Message):
    await message.reply("دسترسی فقط برای ادمین هست.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
