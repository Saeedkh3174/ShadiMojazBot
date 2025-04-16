import logging
import re
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.dispatcher.filters import CommandStart
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.executor import start_webhook

API_TOKEN = "7763325161:AAEuBI8jE1bZLa8VQjR6KRgtey_3rhMNgV4"
ALLOWED_USER_ID = 7562729376
DESTINATION_CHANNEL = "@ShadiMojaz"
WEBHOOK_HOST = 'https://your-render-url.onrender.com'
WEBHOOK_PATH = f'/webhook/{API_TOKEN}'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = 10000

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(level=logging.INFO)

def clean_text(text):
    # حذف آیدی‌ها و لینک کانال‌ها
    text = re.sub(r'(@\w+)', '', text)  # حذف آیدی‌ها
    text = re.sub(r'https://t\.me/\w+', '', text)  # حذف لینک کانال‌ها
    # اضافه کردن فقط یک بار لینک و آیدی خودمون
    text = text.strip()
    if DESTINATION_CHANNEL not in text:
        text += f"\n\n🆔{DESTINATION_CHANNEL}\nhttps://t.me/{DESTINATION_CHANNEL[1:]}"
    return text

@dp.message_handler(CommandStart())
async def start_handler(message: types.Message):
    if message.from_user.id != ALLOWED_USER_ID:
        return
    await message.answer("به ربات مدیریت کانال خوش آمدید.")

@dp.message_handler(content_types=types.ContentTypes.ANY)
async def handle_post(message: types.Message, state: FSMContext):
    if message.from_user.id != ALLOWED_USER_ID:
        return

    if message.text and re.fullmatch(r"\d{4}", message.text.strip()):
        await state.update_data(schedule_time=message.text.strip())
        await message.answer(f"⏰ زمان برنامه‌ریزی ثبت شد: {message.text.strip()}")
        return

    user_data = await state.get_data()
    schedule_time = user_data.get("schedule_time")
    await state.finish()

    # محتوای متنی پاک‌سازی‌شده
    caption = message.caption or message.text or ""
    caption = clean_text(caption)

    # ارسال پست به کانال
    try:
        if message.photo:
            await bot.send_photo(DESTINATION_CHANNEL, message.photo[-1].file_id, caption=caption, parse_mode=ParseMode.HTML)
        elif message.video:
            await bot.send_video(DESTINATION_CHANNEL, message.video.file_id, caption=caption, parse_mode=ParseMode.HTML)
        elif message.text:
            await bot.send_message(DESTINATION_CHANNEL, caption, parse_mode=ParseMode.HTML)
        else:
            await bot.send_message(DESTINATION_CHANNEL, "پستی قابل ارسال نبود.")
    except Exception as e:
        await message.answer(f"خطا در ارسال پست: {e}")

async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(dp):
    await bot.delete_webhook()

if __name__ == "__main__":
    from aiogram import executor
    from aiohttp import web

    async def webhook_handler(request):
        request_body_dict = await request.json()
        update = types.Update.to_object(request_body_dict)
        await dp.process_update(update)
        return web.Response()

    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, webhook_handler)
    app.on_startup.append(lambda app: on_startup(dp))
    app.on_shutdown.append(lambda app: on_shutdown(dp))
    web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT)
