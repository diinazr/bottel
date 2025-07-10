import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# لیست کانال‌هایی که عضویت در آن‌ها الزامی است
REQUIRED_CHANNELS = [
    {"username": "channel1", "name": "کانال اول"},
    {"username": "channel2", "name": "کانال دوم"}
]

# دیکشنری پرامپت‌ها بر اساس آیدی
PROMPTS = {
    "13": """I want you to make a hyperrealistic close-up portrait of my face from this picture, with only the left half visible and partly under water. The scene is neon light that casts colorful reflections on wet skin and wet hair.
Drops of water and small blisters stick on the face and enhance the cinematic mood and skin structure.
The intense concentration of the eyes is clearly visible"""
}

# بررسی عضویت کاربر در کانال‌ها
async def is_user_member(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    missing_channels = []
    for channel in REQUIRED_CHANNELS:
        try:
            member = await context.bot.get_chat_member(chat_id=f"@{channel['username']}", user_id=user_id)
            if member.status not in ["member", "administrator", "creator"]:
                missing_channels.append(channel)
        except:
            missing_channels.append(channel)
    return missing_channels

# هندلر دکمه‌ها
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if data.startswith("prompt_"):
        prompt_id = data.split("_")[1]
        user_id = query.from_user.id

        missing = await is_user_member(user_id, context)

        if missing:
            buttons = [
                [InlineKeyboardButton(f"📢 عضویت در {ch['name']}", url=f"https://t.me/{ch['username']}")]
                for ch in missing
            ]
            buttons.append([InlineKeyboardButton("✅ عضو شدم", callback_data=f"check_{prompt_id}")])
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.edit_message_text(
                "⛔️ برای دریافت پرامپت، ابتدا در کانال‌های زیر عضو شوید:",
                reply_markup=reply_markup
            )
        else:
            prompt = PROMPTS.get(prompt_id, "پرامپتی یافت نشد.")
            await query.edit_message_text(f"🧠 پرامپت {prompt_id}:\n\n{prompt}")

    elif data.startswith("check_"):
        prompt_id = data.split("_")[1]
        user_id = query.from_user.id

        missing = await is_user_member(user_id, context)

        if missing:
            await query.answer("⛔️ هنوز در همه کانال‌ها عضو نشده‌اید.", show_alert=True)
        else:
            prompt = PROMPTS.get(prompt_id, "پرامپتی یافت نشد.")
            await query.edit_message_text(f"🧠 پرامپت {prompt_id}:\n\n{prompt}")

# شروع ربات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🧠 دریافت پرامپت 13", callback_data="prompt_13")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("سلام! یکی از پرامپت‌ها رو انتخاب کن:", reply_markup=reply_markup)

# پیکربندی ربات
def main():
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        print("❌ متغیر محیطی BOT_TOKEN تنظیم نشده.")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("✅ ربات با موفقیت اجرا شد.")
    app.run_polling()

if __name__ == "__main__":
    main()
