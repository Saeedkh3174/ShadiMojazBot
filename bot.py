import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import re
import emoji

API_TOKEN = '7763325161:AAEuBI8jE1bZLa8VQjR6KRgtey_3rhMNgV4'
AUTHORIZED_USER_ID = 7562729376
DESTINATION_CHANNEL = '@shadimojaz'
REPLACEMENT_ID = '🆔@ShadiMojaz'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

premium_emoji_pattern = re.compile(r'<emoji[^>]+></emoji>')

def clean_text(text):
    lines = text.splitlines()
    cleaned_lines = []
    for line in lines:
        if re.search(r'@\w+', line) or re.search(r'https?://\S+', line):
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
    if message.text:
        cleaned = clean_text(message.text)
        await bot.send_message(DESTINATION_CHANNEL, cleaned)

    elif message.caption:
        cleaned_caption = clean_text(message.caption)
        content_type = message.content_type
        send_func = getattr(bot, f"send_{content_type}", None)
        if send_func:
            file_id = getattr(message, content_type).file_id
            kwargs = {content_type: file_id, "chat_id": DESTINATION_CHANNEL, "caption": cleaned_caption}
            await send_func(**kwargs)
        else:
            await bot.send_message(DESTINATION_CHANNEL, "نوع فایل پشتیبانی نمی‌شود.")

    else:
        content_type = message.content_type
        send_func = getattr(bot, f"send_{content_type}", None)
        if send_func:
            file_id = getattr(message, content_type).file_id
            kwargs = {content_type: file_id, "chat_id": DESTINATION_CHANNEL}
            await send_func(**kwargs)
        else:
            await bot.send_message(DESTINATION_CHANNEL, "نوع فایل پشتیبانی نمی‌شود.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
