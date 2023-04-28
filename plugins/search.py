import asyncio
from info import *
from utils import *
from time import time 
from client import User
from pyrogram import Client, filters 
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton 
import urllib.parse

ignore_words = ["in", "and", "hindi"] # words to ignore in search query

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
    start_time = time() # Record the start time
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
            google_url = f"https://www.google.com/search?q={query_encoded}"
            markup = InlineKeyboardMarkup([[InlineKeyboardButton("Check Spelling on Google 🔍", url=google_url)]])
            msg = await message.reply_text(text=no_results_message, disable_web_page_preview=True, reply_markup=markup)
            _time = int(time()) + (15 * 60)
            await save_dlt_message(msg, _time)
            return

        end_time = time() # Record the end time
        duration_ms = int((end_time - start_time) * 1000) # Calculate the duration in milliseconds
        footer = f"Searched in {duration_ms} ms." # Add the duration to the footer
        msg = await message.reply_text(text=head + results + footer, disable_web_page_preview=True)
        _time = int(time()) + (15 * 60)
        await save_dlt_message(msg, _time)
    except:
        pass
