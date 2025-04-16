import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ContentType
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
last_message_type = None
last_message_file_id = None

# حذف آی‌دی‌ها و جایگزینی

def clean_caption_or_text(text):
    text = re.sub(r'🆔.*?(@\w+|\d+)', '', text or '')
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'https?://\S+', '', text)
    text = text.strip()
    if REPLACEMENT_ID not in text:
        text += f"\n\n{REPLACEMENT_ID}"
    return text

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    if message.from_user.id != AUTHORIZED_USER_ID:
        return
    await message.reply("سلام! پیام مورد نظر رو بفرست، بعدش زمانش رو بفرست (مثل 2230 یا 0 برای ارسال فوری).")

@dp.message_handler(lambda message: message.from_user.id == AUTHORIZED_USER_ID and not message.text.isdigit())
async def handle_main_message(message: types.Message):
    global last_message, last_message_type, last_message_file_id

    content_type = message.content_type
    last_message_type = content_type

    if content_type == ContentType.TEXT:
        cleaned_text = clean_caption_or_text(message.text)
        last_message = cleaned_text

    elif content_type in [ContentType.PHOTO, ContentType.VIDEO, ContentType.DOCUMENT, ContentType.VOICE, ContentType.AUDIO]:
        file_id = None
        caption = clean_caption_or_text(message.caption)

        if content_type == ContentType.PHOTO:
            file_id = message.photo[-1].file_id
        elif content_type == ContentType.VIDEO:
            file_id = message.video.file_id
        elif content_type == ContentType.DOCUMENT:
            file_id = message.document.file_id
        elif content_type == ContentType.VOICE:
            file_id = message.voice.file_id
        elif content_type == ContentType.AUDIO:
            file_id = message.audio.file_id

        last_message = caption
        last_message_file_id = file_id

    else:
        await message.reply("این نوع پیام پشتیبانی نمی‌شود.")
        return

    await message.reply("زمان ارسال رو وارد کن (مثل 2230 یا 0 برای بلافاصله).")

@dp.message_handler(lambda message: message.from_user.id == AUTHORIZED_USER_ID and message.text.isdigit())
async def handle_time(message: types.Message):
    global last_message, last_message_type, last_message_file_id

    if not last_message:
        await message.reply("لطفاً اول پیام رو بفرست بعد زمان رو.")
        return

    time_str = message.text.strip()
    now = datetime.now()

    async def send_to_channel():
        if last_message_type == ContentType.TEXT:
            await bot.send_message(DESTINATION_CHANNEL, last_message)
        elif last_message_type == ContentType.PHOTO:
            await bot.send_photo(DESTINATION_CHANNEL, photo=last_message_file_id, caption=last_message)
        elif last_message_type == ContentType.VIDEO:
            await bot.send_video(DESTINATION_CHANNEL, video=last_message_file_id, caption=last_message)
        elif last_message_type == ContentType.DOCUMENT:
            await bot.send_document(DESTINATION_CHANNEL, document=last_message_file_id, caption=last_message)
        elif last_message_type == ContentType.VOICE:
            await bot.send_voice(DESTINATION_CHANNEL, voice=last_message_file_id, caption=last_message)
        elif last_message_type == ContentType.AUDIO:
            await bot.send_audio(DESTINATION_CHANNEL, audio=last_message_file_id, caption=last_message)

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
    last_message_file_id = None
    last_message_type = None

if __name__ == '__main__':
    print("Starting bot...")
    executor.start_polling(dp, skip_updates=True)
