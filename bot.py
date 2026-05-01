import sqlite3
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8706252372:AAG4Jp5lBsG_QR8ZhbhtZotX5jSaVXgWXuI"

# ===== معلوماتك =====
SHAMCASH_NUMBER = "0986530683"
SHAMCASH_CODE = "fdfe47be1ac0be961dc8889406830f9b"
QR_LINK = "https://i.ibb.co/wFHW9804/qr.jpg"
SUPPORT = "@RagnarZ777"

# ===== قاعدة البيانات =====
conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    referrer INTEGER,
    referrals INTEGER DEFAULT 0
)
""")
conn.commit()

# ===== القوائم =====
main_menu = [
    ["شحن الرصيد 💳", "سحب الأرباح 💰"],
    ["روابط و نظام الإحالات 👥"],
    ["إرسال رصيد لصديق 📩", "تفعيل كود هدية 🎁"],
    ["الدعم الفني 🛠"],
    ["سجلك الخاص إيداع/سحب 📜"]
]

deposit_menu = [
    ["Syriatel Cash 🟢 🎁 +5% بونص"],
    ["عملات ومحافظ رقمية (USDT) 🎁 5% بونص"],
    ["Sham Cash Auto ⚡ (USD , SYP) 🎁 +5%"],
    ["القائمة الرئيسية 🔙"]
]

qr_menu = [
    ["📱 عرض الباركود"],
    ["القائمة الرئيسية 🔙"]
]

# ===== /start =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 أهلاً وسهلاً في بوت 55bets RagnarZ 🔥",
        reply_markup=ReplyKeyboardMarkup(main_menu, resize_keyboard=True)
    )

# ===== الردود =====
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # ===== شحن =====
    if text == "شحن الرصيد 💳":
        await update.message.reply_text(
            "اختر طريقة الشحن:",
            reply_markup=ReplyKeyboardMarkup(deposit_menu, resize_keyboard=True)
        )

    # ===== شام كاش =====
    elif "Sham Cash Auto" in text:
        await update.message.reply_text(
            f"📨 ارسل الى العنوان:\n\n"
            f"{SHAMCASH_NUMBER}\n\n"
            f"💳 كود الدفع:\n{SHAMCASH_CODE}\n\n"
            f"🔻 علي محمد 🔻\n\n"
            f"⚠️ لا تقم بإخفاء هوية الحساب\n\n"
            f"🔢 ثم ادخل رقم العملية\n\n"
            f"💱 1 ShamCash USD = 11800"
        )

        await update.message.reply_text(
            "🔷 لعرض باركود شام كاش اضغط الزر:",
            reply_markup=ReplyKeyboardMarkup(qr_menu, resize_keyboard=True)
        )

    # ===== عرض QR =====
    elif text == "📱 عرض الباركود":
        try:
            await update.message.reply_photo(photo=QR_LINK)
        except:
            await update.message.reply_text("❌ فشل تحميل الباركود")

    # ===== سحب =====
    elif text == "سحب الأرباح 💰":
        await update.message.reply_text("💸 ارسل طلب السحب للدعم الفني:\n" + SUPPORT)

    # ===== إحالات =====
    elif text == "روابط و نظام الإحالات 👥":
        user_id = update.effective_user.id
        bot_username = (await context.bot.get_me()).username
        link = f"https://t.me/{bot_username}?start={user_id}"

        await update.message.reply_text(f"🔗 رابطك:\n{link}")

    # ===== دعم =====
    elif text == "الدعم الفني 🛠":
        await update.message.reply_text(f"📞 تواصل مع الدعم:\n{SUPPORT}")

    # ===== رجوع =====
    elif text == "القائمة الرئيسية 🔙":
        await update.message.reply_text(
            "🏠 القائمة الرئيسية",
            reply_markup=ReplyKeyboardMarkup(main_menu, resize_keyboard=True)
        )

    else:
        await update.message.reply_text("اختر من القائمة 👇")

# ===== تشغيل =====
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, handle))

app.run_polling()
