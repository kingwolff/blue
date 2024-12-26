# bot.py

import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import TOKEN
from link_decoder import extract_username 
from database import Database
from telegram_utils import get_telegram_info

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = Database()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
   """Start command handler"""
   await update.message.reply_text("Send your subscription link")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
   """Handle received messages"""
   if not update.message or not update.message.text:
       await update.message.reply_text("Please send a valid link")
       return

   link = update.message.text.strip()
   
   if not (link.startswith('http://') or link.startswith('https://')):
       await update.message.reply_text("Please send a valid link that starts with http:// or https://")
       return

   # Extract username from link
   username = extract_username(link)
   if not username:
       await update.message.reply_text("Could not extract username from this link")
       return
       
   # Get telegram user info
   user_info = get_telegram_info(update.message.from_user)
   
   try:
       # Save to database
       db.save_user(
           username=username,
           telegram_id=user_info['telegram_id'],
           telegram_username=user_info['telegram_username'], 
           telegram_name=user_info['telegram_name']
       )
       
       await update.message.reply_text("Your subscription has been registered")
       
   except Exception as e:
       logger.error(f"Error saving user: {e}")
       await update.message.reply_text("An error occurred. Please try again")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
   """Log errors"""
   logger.error(f"Error: {context.error}")

def main():
   """Start the bot"""
   try:
       app = Application.builder().token(TOKEN).build()

       app.add_handler(CommandHandler("start", start))
       app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
       app.add_error_handler(error_handler)

       logger.info("Bot started")
       app.run_polling(allowed_updates=Update.ALL_TYPES)
       
   except Exception as e:
       logger.error(f"Bot error: {e}")
   finally:
       db.close()

if __name__ == '__main__':
   main()