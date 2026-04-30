import sqlite3
import requests
from io import BytesIO
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8706252372:AAG4Jp5lBsG_QR8ZhbhtZotX5jSaVXgWXuI"

# ===== معلوماتك =====
SHAMCASH_CODE = "fdfe47be1ac0be961dc8889406830f9b"
QR_LINK = "https://raw.githubusercontent.com/algaberali060/RagnarZ-bot/main/qr.jpg"

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

withdraw_menu = [
    ["Syriatel Cash 🟢"],
    ["Sham Cash (SYP) 🇸🇾"],
    ["القائمة الرئيسية 🔙"]
]

records_menu = [
    ["📥 سجل الإيداع", "📤 سجل السحب"],
    ["القائمة الرئيسية 🔙"]
]

# ===== /start =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 أهلاً بك في بوت 55bets RagnarZ 🔥",
        reply_markup=ReplyKeyboardMarkup(main_menu, resize_keyboard=True)
    )

# ===== الردود =====
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # ===== شحن =====
    if text == "شحن الرصيد 💳":
        await update.message.reply_text(
            "🔥 أهلاً بك في بوت 55bets RagnarZ 🔥\n\nاختر طريقة الشحن:",
            reply_markup=ReplyKeyboardMarkup(deposit_menu, resize_keyboard=True)
        )

    elif "Sham Cash Auto" in text:
        await update.message.reply_text(
            f"📨 ارسل الى العنوان:\n\n"
            f"{SHAMCASH_NUMBER}\n\n"
            f"💳 كود الدفع:\n{SHAMCASH_CODE}\n\n"
            f"🔻 مركز شامر للاتصالات 🔻\n\n"
            f"⚠️ لا تقم بإخفاء هوية الحساب\n\n"
            f"🔢 ثم ادخل رقم العملية\n\n"
            f"💱 1 ShamCash USD = 11800"
        )

        qr_menu = [
            ["📱 عرض الباركود"],
            ["القائمة الرئيسية 🔙"]
        ]

        await update.message.reply_text(
            "🔷 لعرض الباركود اضغط الزر:",
            reply_markup=ReplyKeyboardMarkup(qr_menu, resize_keyboard=True)
        )

    # ===== عرض QR (مصلح 100%) =====
    elif text == "📱 عرض الباركود":
        try:
            response = requests.get(QR_LINK)
            bio = BytesIO(response.content)
            bio.name = "qr.jpg"

            await update.message.reply_photo(photo=bio)
        except Exception as e:
            await update.message.reply_text(f"❌ خطأ بالصورة: {e}")

    # ===== سحب =====
    elif text == "سحب الأرباح 💰":
        await update.message.reply_text(
            "اختر طريقة السحب:",
            reply_markup=ReplyKeyboardMarkup(withdraw_menu, resize_keyboard=True)
        )

    # ===== دعم =====
    elif text == "الدعم الفني 🛠":
        await update.message.reply_text("📞 الدعم: @RagnarZ777")

    # ===== باقي =====
    elif text == "القائمة الرئيسية 🔙":
        await update.message.reply_text(
            "🔥 أهلاً بك في بوت 55bets RagnarZ 🔥",
            reply_markup=ReplyKeyboardMarkup(main_menu, resize_keyboard=True)
        )

    else:
        await update.message.reply_text("اختر من القائمة 👇")

# ===== تشغيل =====
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, handle))

app.run_polling()
