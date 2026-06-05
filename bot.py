import os
from telegram.ext import Application, CommandHandler

TOKEN = os.environ.get("8516604474:AAFh7z4EfdfnMefSSzJyqrfKTseBCLYA66k")  # التوكن من متغير البيئة

async def start(update, context):
    await update.message.reply_text("✅ بوت فودافون أونلاين يعمل 24/7!")

if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("🚀 البوت يعمل أونلاين...")
    app.run_polling()
