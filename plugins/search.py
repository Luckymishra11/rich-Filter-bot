import asyncio
from info import *
from utils import *
from time import time 
from client import User
from pyrogram import Client, filters 
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton 
import urllib.parse
import time

ignore_words = ["in", "and", "hindi", "movie", "tamil", "telugu", "dub", "hd", "man", "series", "full", "dubbed", "kannada", "season", "part", "all", "2022", "2021", "2023", "1", "2", "3", "4", "5", "6", "7" ,"8", "9", "0", "2020", "2019", "2018" , "2017", "2016", "2014", "all", "new", "2013", "()", "movies", "2012", "2011", "2010", "2009", "2008", "2007", "2006", "2005", "2004", "2003", "2002", "2001", "1999", "1998", "1997", "1996", "1995", "-+:;!?*", "language", "480p", "720p", "1080p",] # words to ignore in search query

async def should_ignore(word):
    # checks if a word should be ignored in the search query
    return word.lower() in ignore_words

async def clean_query(query):
    # cleans the search query by removing ignored words
    words = query.split()
    cleaned_words = [word for word in words if not await should_ignore(word)]
    return " ".join(cleaned_words)


@Client.on_message(filters.text & filters.group & filters.incoming & ~filters.command(["verify", "connect", "id"]))
async def search(bot, message):
    start_time = time.time()  # Start measuring elapsed time
    f_sub = await force_sub(bot, message)
    if f_sub == False:
        return

    channels = (await get_group(message.chat.id))["channels"]
    if not channels:
        return

    if message.text.startswith("/"):
        return

    query = await clean_query(message.text)
    head = "<u>Here are the results 👇</u>\n\n"
    results = ""
    try:
        for channel in channels:
            async for msg in User.search_messages(chat_id=channel, query=query):
                name = (msg.text or msg.caption).split("\n")[0]
                if name in results:
                    continue
                results += f"<b><i>♻️ {name}\n🔗 {msg.link}</i></b>\n\n"

        if not results:
            # Send message if no results are found
            query_encoded = urllib.parse.quote_plus(query)
            no_results_message = f"No Results Found For <b>{query}</b>\n\n"
            google_url = f"https://www.google.com/search?q={query_encoded}+movie"
            release_date_url = f"https://www.google.com/search?q={query_encoded}+release+date"
            markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Check Spelling on Google 🔍", url=google_url)],
                [InlineKeyboardButton("Check Release Date on Google 📅", url=release_date_url)]
            ])
            msg = await message.reply_text(text=no_results_message, disable_web_page_preview=True, reply_markup=markup)
            _time = int(time()) + (2 * 60)
            await save_dlt_message(msg, _time)
            return

        elapsed_time = time.time() - start_time
        footer = f"Searched in {elapsed_time:.2f} sec." # Add the duration to the footer
        msg = await message.reply_text(text=head + results + footer, disable_web_page_preview=True)
        _time = int(time()) + (120 * 60)
        await save_dlt_message(msg, _time)
    except:
        pass

