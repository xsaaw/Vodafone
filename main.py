# main.py
"""
البوت الرئيسي لفودافون مصر
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)

from vodafone_api import vodafone_api
from database import db_manager
import config

# إعدادات
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# حالات المحادثة
PHONE, PASSWORD, CHOOSE_SERVICE, TRANSFER_DETAILS = range(4)

# ======================= أوامر البوت =======================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بدء البوت"""
    user = update.effective_user
    
    welcome_text = f"""
    🌟 **مرحباً {user.first_name}!**
    
    **بوت فودافون مصر الرسمي**
    
    الخدمات المتاحة:
    📊 عرض رصيدي وباقاتي
    🔄 تحويل إنترنت
    📞 تحويل دقائق
    💰 شحن رصيد
    🎁 العروض الحصرية
    ⚙️ تغيير النظام/الباقة
    
    لبدء الاستخدام، اضغط /login
    """
    
    keyboard = [
        [InlineKeyboardButton("🔐 تسجيل الدخول", callback_data='login')],
        [InlineKeyboardButton("ℹ️ المساعدة", callback_data='help')],
        [InlineKeyboardButton("📞 خدمة العملاء", callback_data='support')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def login_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بدء تسجيل الدخول"""
    await update.message.reply_text(
        "📱 **تسجيل الدخول إلى فودافون**\n\n"
        "أدخل رقم هاتفك فودافون (11 رقم):\n"
        "مثال: 01012345678"
    )
    
    return PHONE

async def receive_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """استقبال رقم الهاتف"""
    phone = update.message.text.strip()
    
    if not phone.isdigit() or len(phone) != 11 or not phone.startswith(('010', '011', '012', '015')):
        await update.message.reply_text(
            "❌ رقم غير صحيح!\n"
            "يجب أن يكون 11 رقماً ويبدأ بـ:\n"
            "010, 011, 012, أو 015"
        )
        return PHONE
    
    context.user_data['phone'] = phone
    
    await update.message.reply_text(
        "🔑 **كلمة السر**\n\n"
        "أدخل كلمة سر حساب فودافون:\n"
        "(هي نفس كلمة سر فودافون كاش أو الموقع)"
    )
    
    return PASSWORD

async def receive_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """استقبال كلمة السر"""
    password = update.message.text.strip()
    phone = context.user_data['phone']
    
    # محاكاة الاتصال بـ API فودافون
    try:
        auth_result = vodafone_api.authenticate(phone, password)
        
        if auth_result['success']:
            user_data = auth_result['data']
            
            # حفظ بيانات المستخدم
            db_manager.save_user(
                telegram_id=update.effective_user.id,
                vodafone_number=phone,
                full_name=update.effective_user.full_name
            )
            
            # حفظ في سياق المحادثة
            context.user_data['user_data'] = user_data
            context.user_data['authenticated'] = True
            
            # عرض القائمة الرئيسية
            keyboard = [
                [InlineKeyboardButton("📊 بياناتي", callback_data='my_info')],
                [InlineKeyboardButton("🔄 تحويل إنترنت", callback_data='transfer_internet')],
                [InlineKeyboardButton("📞 تحويل دقائق", callback_data='transfer_minutes')],
                [InlineKeyboardButton("💰 شحن رصيد", callback_data='recharge')],
                [InlineKeyboardButton("🎁 العروض", callback_data='offers')],
                [InlineKeyboardButton("⚙️ تغيير الباقة", callback_data='change_package')],
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"✅ **تم تسجيل الدخول بنجاح!**\n\n"
                f"مرحباً {user_data.get('name', 'عميل فودافون')}\n"
                f"اختر الخدمة المطلوبة:",
                reply_markup=reply_markup
            )
            
            return CHOOSE_SERVICE
        else:
            await update.message.reply_text("❌ بيانات الدخول غير صحيحة!")
            return ConversationHandler.END
            
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        await update.message.reply_text("⚠️ حدث خطأ في النظام. حاول لاحقاً.")
        return ConversationHandler.END

async def show_my_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض بيانات المستخدم"""
    query = update.callback_query
    await query.answer()
    
    phone = context.user_data.get('phone')
    
    if not phone:
        await query.edit_message_text("❌ لم تقم بتسجيل الدخول!")
        return
    
    # محاكاة استعلام البيانات
    info_result = vodafone_api.get_user_info(phone)
    
    if info_result['success']:
        data = info_result['data']
        
        info_text = f"""
📱 **بيانات خط فودافون**
────────────────────
📞 الرقم: `{data['msisdn']}`
💰 الرصيد: {data['balance']} جنيه
🌐 إنترنت: {data['internet_balance']}
📞 دقائق محلية: {data['local_minutes']} دقيقة
🌍 دقائق دولية: {data['international_minutes']} دقيقة
📨 رسائل: {data['sms_balance']} رسالة
📦 الباقة: {data['current_package']}
📅 انتهاء الباقة: {data['package_expiry']}
🔄 آخر شحن: {data['last_recharge']}
✅ الحالة: {data['status']}
────────────────────
        """
        
        await query.edit_message_text(info_text, parse_mode='Markdown')
    else:
        await query.edit_message_text("❌ تعذر جلب البيانات")

async def transfer_internet_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة تحويل الإنترنت"""
    query = update.callback_query
    await query.answer()
    
    # عرض أنواع التحويل
    keyboard = [
        [InlineKeyboardButton("1GB", callback_data='transfer_1gb')],
        [InlineKeyboardButton("500MB", callback_data='transfer_500mb')],
        [InlineKeyboardButton("2GB", callback_data='transfer_2gb')],
        [InlineKeyboardButton("🔙 رجوع", callback_data='back_to_main')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🌐 **تحويل إنترنت**\n\n"
        "اختر الكمية المراد تحويلها:\n"
        "ثم أرسل رقم المستلم",
        reply_markup=reply_markup
    )

async def handle_transfer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة عملية التحويل"""
    query = update.callback_query
    await query.answer()
    
    transfer_type = query.data
    phone = context.user_data.get('phone')
    
    # تعريف الكميات
    amounts = {
        'transfer_1gb': '1GB',
        'transfer_500mb': '500MB',
        'transfer_2gb': '2GB'
    }
    
    if transfer_type in amounts:
        context.user_data['transfer_amount'] = amounts[transfer_type]
        
        await query.edit_message_text(
            f"🔄 تحويل {amounts[transfer_type]} إنترنت\n\n"
            f"أدخل رقم فودافون المستلم (11 رقم):"
        )
        
        return TRANSFER_DETAILS

async def complete_transfer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إكمال عملية التحويل"""
    receiver_phone = update.message.text.strip()
    phone = context.user_data.get('phone')
    amount = context.user_data.get('transfer_amount')
    
    # التحقق من الرقم
    if not receiver_phone.isdigit() or len(receiver_phone) != 11:
        await update.message.reply_text("❌ رقم غير صحيح!")
        return TRANSFER_DETAILS
    
    # محاكاة عملية التحويل
    result = vodafone_api.transfer_internet(phone, receiver_phone, amount)
    
    if result['success']:
        # تسجيل العملية
        db_manager.log_transaction(
            telegram_id=update.effective_user.id,
            operation_type="internet_transfer",
            amount=0,  # لا يوجد مبلغ مالي
            from_number=phone,
            to_number=receiver_phone,
            status="completed",
            details=f"تحويل {amount} إنترنت"
        )
        
        success_text = f"""
✅ **تم التحويل بنجاح!**
────────────────────
📤 من: {phone}
📥 إلى: {receiver_phone}
📊 الكمية: {amount}
🆔 رقم العملية: {result['transaction_id']}
📅 التاريخ: {result['date']}
📉 المتبقي: {result['remaining_balance']}
────────────────────
        """
        
        await update.message.reply_text(success_text)
    else:
        await update.message.reply_text("❌ فشل عملية التحويل")
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إلغاء العملية"""
    await update.message.reply_text("تم الإلغاء.")
    return ConversationHandler.END

# ======================= التهيئة الرئيسية =======================

def main():
    """الدالة الرئيسية لتشغيل البوت"""
    
    # إنشاء التطبيق
    application = Application.builder().token(config.BOT_TOKEN).build()
    
    # محادثة تسجيل الدخول
    login_conversation = ConversationHandler(
        entry_points=[CommandHandler('login', login_command)],
        states={
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_phone)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_password)],
            CHOOSE_SERVICE: [
                CallbackQueryHandler(show_my_info, pattern='^my_info$'),
                CallbackQueryHandler(transfer_internet_handler, pattern='^transfer_internet$'),
                CallbackQueryHandler(handle_transfer, pattern='^transfer_.*$'),
            ],
            TRANSFER_DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, complete_transfer)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    # إضافة المعالجات
    application.add_handler(CommandHandler("start", start))
    application.add_handler(login_conversation)
    application.add_handler(CallbackQueryHandler(show_my_info, pattern='^my_info$'))
    application.add_handler(CallbackQueryHandler(transfer_internet_handler, pattern='^transfer_internet$'))
    
    # معالجات العودة
    application.add_handler(CallbackQueryHandler(start, pattern='^back_to_main$'))
    
    # بدء البوت
    print("🚀 بدء تشغيل بوت فودافون مصر...")
    print("📱 انتقل إلى تيليجرام وابحث عن بوتك")
    print("⚡ أرسل /start للبدء")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()