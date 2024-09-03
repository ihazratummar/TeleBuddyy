from telegram import Update
from telegram.ext import CommandHandler, Application
from commands.utils import start
import os 
from dotenv import load_dotenv
from commands_list import get_handlers
from error.error_handle import error_handle
from telegram.ext import CallbackQueryHandler
from pymongo import MongoClient



load_dotenv()
mongo_username = os.getenv("MONGO_USERNAME")
mongo_password = os.getenv("MONGO_PASSWORD")

uri = f"mongodb+srv://{mongo_username}:{mongo_password}@cluster0.7aptm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
mongo_client = MongoClient(uri)
database = mongo_client["TODO_Database"]

class Bot:
    def __init__(self, database) :
        self.token = os.getenv("TELEGRAM_TOKEN")
        self.app = Application.builder().token(self.token).build()
        self.mongo_client = mongo_client
        self.database = database


    def add_handler(self):
        commands , button_handlers = get_handlers(self.database)
        for command , handler in commands:
            self.app.add_handler(CommandHandler(command, handler))
        
        for button_handler in button_handlers:
            self.app.add_handler(CallbackQueryHandler(button_handler))
        self.app.add_error_handler(error_handle)
    def start(self):
        print("Starting Bot....")
        self.add_handler()
        print("Polling...")
        self.app.run_polling()

if __name__ == "__main__":
    bot = Bot(database=database)
    bot.start()

