import telebot
import os
from dotenv import load_dotenv

load_dotenv()
tgBOT = os.getenv("TOKEN")

bot = telebot.TeleBot(tgBOT)





