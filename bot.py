import sqlite3
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8706252372:AAG4Jp5lBsG_QR8ZhbhtZotX5jSaVXgWXuI"

# ===== معلوماتك =====
SHAMCASH_NUMBER = "093XXXXXXX"
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
    ["حوالة 🏦", "Payeer $"],
    ["Sham Cash (SYP) 🇸🇾"],
    ["$ Sham Cash (USD)"],
    ["Coine x", "Cwallet"],
    ["Usdt Bep 20", "Usdt trc20"],
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
        "🔥 أهلاً بك في بوت 55bets RagnarZ 🔥",
        reply_markup=ReplyKeyboardMarkup(main_menu, resize_keyboard=True)
    )

# ===== الردود =====
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

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
            f"🔻 مركز شامر للاتصالات 🔻\n\n"
            f"⚠️ من فضلك لا تقم بإخفاء هوية حساب شام كاش الذي تقوم بالشحن منه\n\n"
            f"🔢 ثم ادخل رقم العملية\n\n"
            f"💱 1 ShamCash USD = 11800"
        )

        qr_button = [["📱 عرض الباركود"], ["القائمة الرئيسية 🔙"]]

        await update.message.reply_text(
            "🔷 لعرض باركود شام كاش، اضغط على الزر أدناه:",
            reply_markup=ReplyKeyboardMarkup(qr_button, resize_keyboard=True)
        )

    elif text == "📱 عرض الباركود":
        await update.message.reply_photo(photo=QR_LINK)

    # ===== سحب =====
    elif text == "سحب الأرباح 💰":
        await update.message.reply_text(
            "🔥 أهلاً بك في بوت 55bets RagnarZ 🔥\n\nاختر طريقة السحب:",
            reply_markup=ReplyKeyboardMarkup(withdraw_menu, resize_keyboard=True)
        )

    elif text == "Sham Cash (SYP) 🇸🇾":
        await update.message.reply_text("💸 أرسل رقمك لاستلام الحوالة")

    # ===== إحالات =====
    elif text == "روابط و نظام الإحالات 👥":
        cursor.execute("SELECT referrals FROM users WHERE user_id=?", (user_id,))
        result = cursor.fetchone()
        count = result[0] if result else 0

        bot_username = (await context.bot.get_me()).username
        link = f"https://t.me/{bot_username}?start={user_id}"

        await update.message.reply_text(
            f"🔥 أهلاً بك في بوت 55bets RagnarZ 🔥\n\n"
            f"🔗 رابطك:\n{link}\n\n"
            f"👤 عدد الإحالات: {count}"
        )

    # ===== إرسال رصيد =====
    elif text == "إرسال رصيد لصديق 📩":
        await update.message.reply_text("📩 أرسل آيدي الشخص والمبلغ")

    # ===== كود هدية =====
    elif text == "تفعيل كود هدية 🎁":
        await update.message.reply_text("🎁 أرسل كود الهدية")

    # ===== الدعم =====
    elif text == "الدعم الفني 🛠":
        await update.message.reply_text("📞 تواصل مع الدعم: @username")

    # ===== السجل =====
    elif text == "سجلك الخاص إيداع/سحب 📜":
        await update.message.reply_text(
            "📜 اختر:",
            reply_markup=ReplyKeyboardMarkup(records_menu, resize_keyboard=True)
        )

    elif text == "📥 سجل الإيداع":
        await update.message.reply_text("📥 لا يوجد عمليات")

    elif text == "📤 سجل السحب":
        await update.message.reply_text("📤 لا يوجد عمليات")

    # ===== رجوع =====
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
