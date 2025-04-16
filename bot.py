import logging
import re
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import Message

API_TOKEN = '7763325161:AAEuBI8jE1bZLa8VQjR6KRgtey_3rhMNgV4'
OWNER_ID = 7562729376
CHANNEL_TAG = "🆔@ShadiMojaz"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

def clean_caption(caption: str) -> str:
    if not caption:
        return CHANNEL_TAG

    # حذف تمام آیدی‌ها یا لینک‌های کانال‌های تلگرام
    caption = re.sub(r"@[\w\d_]+", "", caption)
    caption = re.sub(r"https?://t\.me/[\w\d_]+", "", caption)
    caption = caption.strip()

    # اضافه کردن فقط یک بار لینک کانال خودمون
    if CHANNEL_TAG not in caption:
        caption += f"\n\n{CHANNEL_TAG}"

    return caption

@dp.message_handler(lambda message: message.from_user.id == OWNER_ID, content_types=types.ContentTypes.ANY)
async def forward_or_send_handler(message: Message):
    if message.forward_from or message.forward_from_chat:
        # پیام فورواردی هست
        if message.caption:
            new_caption = clean_caption(message.caption)
            await bot.send_message(chat_id=message.chat.id, text=new_caption)
        elif message.text:
            new_text = clean_caption(message.text)
            await bot.send_message(chat_id=message.chat.id, text=new_text)
        else:
            await message.copy_to(chat_id=message.chat.id)
    else:
        # پیام خودته
        if message.caption:
            new_caption = clean_caption(message.caption)
            await bot.send_message(chat_id=message.chat.id, text=new_caption)
        elif message.text:
            new_text = clean_caption(message.text)
            await bot.send_message(chat_id=message.chat.id, text=new_text)
        else:
            await message.copy_to(chat_id=message.chat.id)

@dp.message_handler(lambda message: message.from_user.id != OWNER_ID)
async def deny_others(message: Message):
    await message.reply("⛔ فقط مدیر مجاز به استفاده از این ربات است.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
