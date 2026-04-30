import sqlite3
from telegram import Update, ReplyKeyboardMarkup, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8706252372:AAG4Jp5lBsG_QR8ZhbhtZotX5jSaVXgWXuI"

# ===== معلوماتك =====
SHAMCASH_NUMBER = "fdfe47be1ac0be961dc8889406830f9b"
QR_IMAGE = "qr.jpg"

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
    ["USDT 🎁 5%"],
    ["Sham Cash ⚡"],
    ["القائمة الرئيسية 🔙"]
]

withdraw_menu = [
    ["Syriatel Cash 🟢"],
    ["Sham Cash 🇸🇾"],
    ["USDT"],
    ["القائمة الرئيسية 🔙"]
]

records_menu = [
    ["📥 سجل الإيداع", "📤 سجل السحب"],
    ["القائمة الرئيسية 🔙"]
]

# ===== /start =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()

    if not user:
        referrer = None

        if context.args:
            try:
                referrer = int(context.args[0])
            except:
                pass

        cursor.execute(
            "INSERT INTO users (user_id, referrer, referrals) VALUES (?, ?, 0)",
            (user_id, referrer)
        )
        conn.commit()

        if referrer and referrer != user_id:
            cursor.execute(
                "UPDATE users SET referrals = referrals + 1 WHERE user_id=?",
                (referrer,)
            )
            conn.commit()

    await update.message.reply_text(
        "🔥 أهلاً بك في بوت 55bets 🔥",
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

    elif text == "Sham Cash ⚡":
        await update.message.reply_text(
            f"💰 شحن عبر شام كاش\n\n"
            f"📱 الرقم: {SHAMCASH_NUMBER}\n\n"
            f"📸 أرسل صورة التحويل بعد الدفع"
        )

        # إرسال QR
        try:
            await update.message.reply_photo(photo=InputFile(QR_IMAGE))
        except:
            await update.message.reply_text("IMG_٢٠٢٦٠٤٣٠_٢٠١٩٤٦.jpg")

    # ===== سحب =====
    elif text == "سحب الأرباح 💰":
        await update.message.reply_text(
            "اختر طريقة السحب:",
            reply_markup=ReplyKeyboardMarkup(withdraw_menu, resize_keyboard=True)
        )

    elif text == "Sham Cash 🇸🇾":
        await update.message.reply_text("💸 أرسل رقمك لاستلام الحوالة")

    # ===== إحالات =====
    elif text == "روابط و نظام الإحالات 👥":
        user_id = update.effective_user.id

        cursor.execute("SELECT referrals FROM users WHERE user_id=?", (user_id,))
        result = cursor.fetchone()
        count = result[0] if result else 0

        bot_username = (await context.bot.get_me()).username
        link = f"https://t.me/{bot_username}?start={user_id}"

        await update.message.reply_text(
            f"👥 رابطك:\n{link}\n\n👤 عدد الإحالات: {count}"
        )

    # ===== باقي =====
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
