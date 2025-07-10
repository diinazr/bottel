import os
import logging
import sqlite3
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from telegram.constants import ParseMode

BOT_TOKEN = "توکن خودتو اینجا بذار"

REQUIRED_CHANNELS = [
    {"name": "کانال اول", "username": "yourchannel1"},
    {"name": "کانال دوم", "username": "yourchannel2"},
]

conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()
c.execute(
    "CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, is_member INTEGER)"
)
conn.commit()

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args

    prompt_id = args[0] if args else None

    if not await is_user_member(update, context):
        await send_force_subscribe_buttons(update)
        return

    if prompt_id:
        prompt_text = get_prompt_text(prompt_id)
        if prompt_text:
            await update.message.reply_text(
                f"🧠 پرامپت {prompt_id}:

{prompt_text}", parse_mode=ParseMode.HTML
            )
        else:
            await update.message.reply_text("پرامپتی با این شناسه پیدا نشد.")
    else:
        await update.message.reply_text("برای دریافت پرامپت، از طریق لینک وارد شوید.")

async def check_membership(update, context, channel):
    try:
        user_id = update.effective_user.id
        member = await context.bot.get_chat_member(f"@{channel}", user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

async def is_user_member(update, context):
    for ch in REQUIRED_CHANNELS:
        if not await check_membership(update, context, ch["username"]):
            return False
    return True

async def send_force_subscribe_buttons(update):
    keyboard = [
        [InlineKeyboardButton(f"عضویت در {ch['name']}", url=f"https://t.me/{ch['username']}")]
        for ch in REQUIRED_CHANNELS
    ]
    keyboard.append([InlineKeyboardButton("✅ عضو شدم", callback_data="check_sub")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "⛔️ برای استفاده از ربات، ابتدا در کانال‌های زیر عضو شوید:",
        reply_markup=reply_markup,
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "check_sub":
        if await is_user_member(update, context):
            await query.edit_message_text("✅ عضویت تایید شد. لطفاً دوباره لینک پرامپت رو بزنید.")
        else:
            await query.answer("❌ هنوز عضو همه کانال‌ها نیستید!", show_alert=True)

def get_prompt_text(prompt_id):
    prompts = {
        "13": "I want you to make a hyperrealistic close-up portrait of my face from this picture, with only the left half visible and partly under water...",
        "14": "This is another prompt example...",
    }
    return prompts.get(prompt_id)

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.run_polling()

if __name__ == "__main__":
    main()