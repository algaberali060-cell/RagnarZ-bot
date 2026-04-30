import sqlite3
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TOKEN")
SHAM_NUMBER = os.getenv("SHAM_NUMBER")  # حساب الشام كاش

# ===== قاعدة البيانات =====
conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    referrer INTEGER,
    referrals INTEGER DEFAULT 0,
    balance REAL DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    txid TEXT PRIMARY KEY,
    user_id INTEGER,
    amount REAL,
    status TEXT
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
                referrer = None

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
        "اهلا بك في بوت 55bets",
        reply_markup=ReplyKeyboardMarkup(main_menu, resize_keyboard=True)
    )

# ===== الردود =====
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    # ===== شحن =====
    if text == "شحن الرصيد 💳":
        await update.message.reply_text(
            "اختر أحد طرق الشحن",
            reply_markup=ReplyKeyboardMarkup(deposit_menu, resize_keyboard=True)
        )

    # ===== سحب =====
    elif text == "سحب الأرباح 💰":
        await update.message.reply_text(
            "اختر أحد الطرق",
            reply_markup=ReplyKeyboardMarkup(withdraw_menu, resize_keyboard=True)
        )

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

    # ===== إرسال رصيد لصديق =====
    elif text == "إرسال رصيد لصديق 📩":
        await update.message.reply_text("📩 أرسل آيدي الشخص والمبلغ")

    # ===== كود هدية =====
    elif text == "تفعيل كود هدية 🎁":
        await update.message.reply_text("🎁 أرسل كود الهدية")

    # ===== الدعم الفني =====
    elif text == "الدعم الفني 🛠":
        await update.message.reply_text("📞 تواصل مع الدعم: @username")

    # ===== السجل =====
    elif text == "سجلك الخاص إيداع/سحب 📜":
        await update.message.reply_text(
            "📜 اختر",
            reply_markup=ReplyKeyboardMarkup(records_menu, resize_keyboard=True)
        )

    elif text == "📥 سجل الإيداع":
        await update.message.reply_text("📥 لا يوجد عمليات")

    elif text == "📤 سجل السحب":
        await update.message.reply_text("📤 لا يوجد عمليات")

    # ===== الشحن عبر الشام كاش =====
    elif text == "Sham Cash Auto ⚡ (USD , SYP) 🎁 +5%":
        await update.message.reply_text(
            f"📩 ارسل الى العنوان:\n\n{SHAM_NUMBER}\n\n"
            "♦ مركز شام للاتصالات ♦\n\n"
            "⚠️ لا تقم بإخفاء هوية حسابك\n\n"
            "💰 ثم ادخل رقم العملية\n\n"
            "1 ShamCash USD = 11800\n\n"
            "اضغط على زر (أرسلت التحويل)"
        )

    elif text == "أرسلت التحويل ✅":
        user_state[user_id] = "amount"
        await update.message.reply_text("💰 اكتب المبلغ:")

    elif user_state.get(user_id) == "amount":
        try:
            amount = float(text)
            context.user_data["amount"] = amount
            user_state[user_id] = "txid"
            await update.message.reply_text("🔢 أرسل رقم العملية:")
        except:
            await update.message.reply_text("❌ اكتب رقم صحيح")

    elif user_state.get(user_id) == "txid":
        txid = text
        amount = context.user_data.get("amount")

        cursor.execute("SELECT * FROM transactions WHERE txid=?", (txid,))
        if cursor.fetchone():
            await update.message.reply_text("❌ رقم العملية مستخدم مسبقاً")
            user_state[user_id] = None
            return

        cursor.execute(
            "INSERT INTO transactions (txid, user_id, amount, status) VALUES (?, ?, ?, 'pending')",
            (txid, user_id, amount)
        )
        conn.commit()

        await update.message.reply_text("⏳ تم إرسال طلبك، انتظر الموافقة")

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"💰 طلب شحن جديد\n\n👤 {user_id}\n💵 {amount}\n🔢 {txid}\n\n"
                 f"/approve {txid}\n/reject {txid}"
        )

        user_state[user_id] = None

    elif text == "رصيدي 💰":
        cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
        balance = cursor.fetchone()[0]
        await update.message.reply_text(f"💰 رصيدك: {balance}")

    # ===== العودة للقائمة الرئيسية =====
    elif text == "القائمة الرئيسية 🔙":
        await update.message.reply_text(
            "القائمة الرئيسية",
            reply_markup=ReplyKeyboardMarkup(main_menu, resize_keyboard=True)
        )

    else:
        await update.message.reply_text("اختر من القائمة 👇")

# ===== تشغيل التطبيق =====
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

print("Bot is running...")

app.run_polling() 
