import asyncio
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from google import genai

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PORT = int(os.getenv("PORT", 10000))

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
client = genai.Client(api_key=GEMINI_API_KEY)


async def health_check(request):
    return web.Response(text="OK")


async def start_web_server():
    app = web.Application()
    app.router.add_get("/", health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("Salom! Menga savol yozing, Gemini orqali javob beraman.")


@dp.message()
async def handle_message(message: types.Message):
    if not message.text:
        return
    try:
        response = await asyncio.to_thread(
            client.models.generate_content,
            model="gemini-2.5-flash",
            contents=message.text,
        )
        text = response.text or "Javob qaytarilmadi."
        await message.answer(text[:4000])
    except Exception as e:
        await message.answer(f"Xatolik yuz berdi: {e}")


async def main():
    await start_web_server()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
