from telegram import Update
from telegram.ext import  ContextTypes
from datetime import datetime


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I am your bot. How can i help you  today!")

async def calculate_age(update: Update, context : ContextTypes.DEFAULT_TYPE):
    try:
        dob_str = " ".join(context.args)
        dob = datetime.strptime(dob_str, "%Y-%m-%d")

        today  = datetime.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

        await update.message.reply_text(f"Your age is {age} years.")

    except ValueError:
        await update.message.reply_text("Please provide your date of birth in YYYY-MM-DD format.")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        message = " ".join(context.args)
        if message:
            await update.message.reply_text(message)
        else:
            await update.message.reply_text(f"Enter a message to get the echo")
    except ValueError:
        await update.message.reply_text(f"Enter a message first")