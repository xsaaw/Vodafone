import os
from telegram.ext import Application, CommandHandler

TOKEN = os.environ.get("8877926312:AAH0wnE3NqpaI4Xsoq8i_2vY4e0yL3zZ9lM")  # التوكن من متغير البيئة

async def start(update, context):
    await update.message.reply_text("✅ بوت فودافون أونلاين يعمل 24/7!")

if __name__ == "__main__":
    app = Application.builder().token(8877926312:AAH0wnE3NqpaI4Xsoq8i_2vY4e0yL3zZ9lM).build()
    app.add_handler(CommandHandler("start", start))
    print("🚀 البوت يعمل أونلاين...")
    app.run_polling()
