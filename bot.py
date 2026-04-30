import sqlite3
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ===== التوكن من Railway =====
TOKEN = os.getenv("TOKEN")

# ===== إعدادات شام كاش =====
SHAMCASH_NUMBER = "093XXXXXXX"  # حط رقمك هون
QR_IMAGE = "IMG_٢٠٢٦٠٤٣٠_٢٠١٩٤٦.jpg"

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
    ["الدعم الفني 🛠"]
]

deposit_menu = [
    ["شام كاش 📲"],
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
        "🔥 أهلاً بك في بوت 55bets",
        reply_markup=ReplyKeyboardMarkup(main_menu, resize_keyboard=True)
    )

# ===== التعامل مع الأزرار =====
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    # ===== شحن =====
    if text == "شحن الرصيد 💳":
        await update.message.reply_text(
            "💳 اختر طريقة الدفع",
            reply_markup=ReplyKeyboardMarkup(deposit_menu, resize_keyboard=True)
        )

    # ===== شام كاش =====
    elif text == "شام كاش 📲":
        try:
            with open(QR_IMAGE, "rb") as photo:
                await update.message.reply_photo(
                    photo,
                    caption=f"📲 الدفع عبر شام كاش\n\n"
                            f"📞 الرقم: {SHAMCASH_NUMBER}\n\n"
                            f"⚠️ بعد التحويل أرسل صورة التحويل للدعم"
                )
        except:
            await update.message.reply_text("❌ لم يتم العثور على صورة الباركود")

    # ===== سحب =====
    elif text == "سحب الأرباح 💰":
        await update.message.reply_text("💰 سيتم إضافة طرق السحب قريباً")

    # ===== الإحالات =====
    elif text == "روابط و نظام الإحالات 👥":
        cursor.execute("SELECT referrals FROM users WHERE user_id=?", (user_id,))
        result = cursor.fetchone()
        count = result[0] if result else 0

        bot_username = (await context.bot.get_me()).username
        link = f"https://t.me/{bot_username}?start={user_id}"

        await update.message.reply_text(
            f"👥 نظام الإحالات\n\n"
            f"🔗 رابطك:\n{link}\n\n"
            f"👤 عدد الإحالات: {count}",
            reply_markup=ReplyKeyboardMarkup([["القائمة الرئيسية 🔙"]], resize_keyboard=True)
        )

    # ===== دعم =====
    elif text == "الدعم الفني 🛠":
        await update.message.reply_text("📞 تواصل: @username")

    # ===== رجوع =====
    elif text == "القائمة الرئيسية 🔙":
        await update.message.reply_text(
            "🏠 القائمة الرئيسية",
            reply_markup=ReplyKeyboardMarkup(main_menu, resize_keyboard=True)
        )

    else:
        await update.message.reply_text("❗ اختر من القائمة")

# ===== تشغيل =====
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, handle))

app.run_polling() 
