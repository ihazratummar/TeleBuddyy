from telegram import Update
from telegram.ext import ContextTypes



async def error_handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"update {update} caused error {context.error}")