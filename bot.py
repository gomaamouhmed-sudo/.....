import telebot
import feedparser
import time
import threading
from flask import Flask
import os
from googletrans import Translator
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import urllib.parse

# --- إعدادات البوت والقناة ---
BOT_TOKEN = '7607234516:AAHfehf32gFybQQQ4kMr3EMJ60QytV19Mfg'
CHANNEL_ID = '@CryptocurrenciesRu'

# --- روابط الأخبار ---
FEEDS = [
    'https://www.farsnews.ir/rss',
    'https://www.mehrnews.com/rss',
    'https://www.tasnimnews.com/fa/rss',
    'https://www.aljazeera.net/xml/rss/all.xml',
    'http://feeds.bbci.co.uk/arabic/rss.xml',
    'https://www.skynewsarabia.com/rss/news/'
]

bot = telebot.TeleBot(BOT_TOKEN)
translator = Translator()
app = Flask(__name__)

PUBLISHED_FILE = "published.txt"

def load_published():
    if os.path.exists(PUBLISHED_FILE):
        with open(PUBLISHED_FILE, 'r', encoding='utf-8') as f:
            return set(f.read().splitlines())
    return set()

def save_published(link):
    with open(PUBLISHED_FILE, 'a', encoding='utf-8') as f:
        f.write(link + '\n')
    published_links.add(link)

published_links = load_published()

@app.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def translate_text(text, dest_lang):
    try:
        translated = translator.translate(text, dest=dest_lang)
        return translated.text
    except Exception:
        return text

def fetch_and_post():
    while True:
        for url in FEEDS:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:2]:
                    if entry.link not in published_links:
                        title_ar = translate_text(entry.title, 'ar')
                        title_en = translate_text(entry.title, 'en')
                        
                        message = f"🔴 **خبر جديد | Breaking News**\n\n"
                        message += f"🇪🇬 **{title_ar}**\n"
                        message += f"🇬🇧 **{title_en}**\n\n"
                        message += f"🔗 [المصدر | Source]({entry.link})"
                        
                        markup = InlineKeyboardMarkup()
                        share_url = f"https://t.me/share/url?url={urllib.parse.quote(entry.link)}"
                        markup.add(InlineKeyboardButton(text="🔄 مشاركة | Share", url=share_url))
                        
                        bot.send_message(CHANNEL_ID, message, parse_mode='Markdown', reply_markup=markup)
                        save_published(entry.link)
                        time.sleep(5)
            except Exception as e:
                print(f"Error: {e}")
        time.sleep(600)

def keep_alive():
    threading.Thread(target=run_flask).start()

if __name__ == "__main__":
    keep_alive()
    threading.Thread(target=fetch_and_post).start()
    while True:
        time.sleep(10)
