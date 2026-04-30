import sqlite3
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TOKEN")

# 🔥 كود الشام كاش تبعك
SHAM_NUMBER = "fdfe47be1ac0be961dc8889406830f9b"

# ===== قاعدة البيانات =====
conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
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

# ===== متغيرات =====
user_state = {}

# 🔥 آيديك
ADMIN_ID = 8589599931

# ===== القوائم =====
main_menu = [
    ["شحن الرصيد 💳"],
    ["رصيدي 💰"]
]

deposit_menu = [
    ["Sham Cash ⚡"],
    ["عرض الباركود 📱"],
    ["أرسلت التحويل ✅"],
    ["القائمة الرئيسية 🔙"]
]

# ===== /start =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()

    await update.message.reply_text(
        "اهلا بك 👋",
        reply_markup=ReplyKeyboardMarkup(main_menu, resize_keyboard=True)
    )

# ===== الموافقة =====
async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    txid = context.args[0]

    cursor.execute("SELECT user_id, amount, status FROM transactions WHERE txid=?", (txid,))
    data = cursor.fetchone()

    if not data:
        await update.message.reply_text("❌ العملية غير موجودة")
        return

    user_id, amount, status = data

    if status == "approved":
        await update.message.reply_text("❌ تمت الموافقة مسبقاً")
        return

    cursor.execute("UPDATE transactions SET status='approved' WHERE txid=?", (txid,))
    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (amount, user_id))
    conn.commit()

    await context.bot.send_message(user_id, f"✅ تم شحن {amount}")
    await update.message.reply_text("✅ تم قبول العملية")

# ===== الرفض =====
async def reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    txid = context.args[0]

    cursor.execute("SELECT status FROM transactions WHERE txid=?", (txid,))
    data = cursor.fetchone()

    if not data:
        await update.message.reply_text("❌ العملية غير موجودة")
        return

    if data[0] == "approved":
        await update.message.reply_text("❌ لا يمكن رفض عملية مقبولة")
        return

    cursor.execute("UPDATE transactions SET status='rejected' WHERE txid=?", (txid,))
    conn.commit()

    await update.message.reply_text("❌ تم رفض العملية")

# ===== الردود =====
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    if text == "شحن الرصيد 💳":
        await update.message.reply_text(
            "اختر طريقة الشحن",
            reply_markup=ReplyKeyboardMarkup(deposit_menu, resize_keyboard=True)
        )

    elif text == "Sham Cash ⚡":
        await update.message.reply_text(
            f"📩 ارسل الى العنوان:\n\n{SHAM_NUMBER}\n\n"
            "♦ مركز شام للاتصالات ♦\n\n"
            "⚠️ لا تقم بإخفاء هوية حسابك\n\n"
            "💰 ثم ادخل رقم العملية\n\n"
            "1 ShamCash USD = 11800\n\n"
            "اضغط على (عرض الباركود 📱)"
        )

    elif text == "عرض الباركود 📱":
        try:
            await update.message.reply_photo(
                photo=open("qr.png", "rb"),
                caption="📱 هذا هو باركود الشحن"
            )
        except:
            await update.message.reply_text("⚠️ لم يتم رفع صورة الباركود بعد")

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

    elif text == "القائمة الرئيسية 🔙":
        await update.message.reply_text(
            "القائمة الرئيسية",
            reply_markup=ReplyKeyboardMarkup(main_menu, resize_keyboard=True)
        )

    else:
        await update.message.reply_text("اختر من القائمة")

# ===== تشغيل =====
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("approve", approve))
app.add_handler(CommandHandler("reject", reject))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

print("Bot is running...")

app.run_polling()
