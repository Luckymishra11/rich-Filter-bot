import asyncio
from info import *
from utils import *
from time import time 
from client import User
from pyrogram import Client, filters 
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton 

@Client.on_message(filters.text & filters.group & filters.incoming & ~filters.command(["verify", "connect", "id"]))
async def search(bot, message):
    # Check if auto-delete is enabled for group admins
    group_settings = await get_group(message.chat.id)
    auto_delete_enabled = group_settings.get("auto_delete", False) and message.from_user.id in group_settings.get("admins", [])
    
    f_sub = await force_sub(bot, message)
    if f_sub == False:
        return     
    channels = (await get_group(message.chat.id))["channels"]
    if bool(channels) == False:
        return     
    if message.text.startswith("/"):
        return    
    query = message.text 
    head = "<u>Here is the results 👇</u>\n\n"
    results = ""
    try:
        for channel in channels:
            async for msg in User.search_messages(chat_id=channel, query=query):
                name = (msg.text or msg.caption).split("\n")[0]
                if name in results:
                    continue 
                results += f"<b><I>♻️ {name}\n🔗 {msg.link}</I></b>\n\n"                                                      
        if bool(results) == False:
            movies = await search_imdb(query)
            buttons = []
            for movie in movies: 
                buttons.append([InlineKeyboardButton(movie['title'], callback_data=f"recheck_{movie['id']}")])
            msg = await message.reply_photo(
                photo="https://graph.org/file/409991ff17c47b910be92.jpg",
                caption="<b><I>I Couldn't find anything related to Your Query😕.\nDid you mean any of these?</I></b>", 
                reply_markup=InlineKeyboardMarkup(buttons))
        else:
            msg = await message.reply_text(text=head + results, disable_web_page_preview=True)
        _time = (int(time()) + (5*60))
        await save_dlt_message(msg, _time)
        if auto_delete_enabled:
            await msg.delete()
    except:
        pass

       


@Client.on_callback_query(filters.regex(r"^recheck"))
async def recheck(bot, update):
    clicked = update.from_user.id
    try:      
       typed = update.message.reply_to_message.from_user.id
    except:
       return await update.message.delete(2)       
    if clicked != typed:
       return await update.answer("That's not for you! 👀", show_alert=True)

    m=await update.message.edit("Finding..🥵")
    id      = update.data.split("_")[-1]
    query   = await search_imdb(id)
    channels = (await get_group(update.message.chat.id))["channels"]
    head    = "<u>I Have Searched Movie With Wrong Spelling But Take care next time 👇\n\nPowered By </u>\n\n"
    results = ""
    try:
       for channel in channels:
           async for msg in User.search_messages(chat_id=channel, query=query):
               name = (msg.text or msg.caption).split("\n")[0]
               if name in results:
                  continue 
               results += f"<b><I>♻️🍿 {name}</I></b>\n\n🔗 {msg.link}</I></b>\n\n"
       if bool(results)==False:          
          return await update.message.edit("Still no results found! Please Request To Group Admin", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎯 Request To Admin 🎯", callback_data=f"request_{id}")]]))
       await update.message.edit(text=head+results, disable_web_page_preview=True)
    except Exception as e:
       await update.message.edit(f"❌ Error: `{e}`")


@Client.on_callback_query(filters.regex(r"^request"))
async def request(bot, update):
    clicked = update.from_user.id
    try:      
       typed = update.message.reply_to_message.from_user.id
    except:
       return await update.message.delete()       
    if clicked != typed:
       return await update.answer("That's not for you! 👀", show_alert=True)

    admin = (await get_group(update.message.chat.id))["user_id"]
    id    = update.data.split("_")[1]
    name  = await search_imdb(id)
    url   = "https://www.imdb.com/title/tt"+id
    text  = f"#Request\n\nName: `{name}`\nIMDb: {url}\n\nGroup ID: {update.message.chat.id}\nGroup Name: {update.message.chat.title}"
    await bot.send_message(chat_id=admin, text=text, disable_web_page_preview=True)
    await update.answer("✅ Request Sent To Admin", show_alert=True)
    await update.message.delete(60)


@Client.on_message(filters.command(["set"]) & filters.group & filters.user(Config.BOT_OWNER) & filters.reply_to_message)
async def set_group_setting(bot, message):
    # Get the group settings
    group_id = message.chat.id
    group_settings = await get_group(group_id)

    # Check if the message is a reply to a message
    reply_message = message.reply_to_message
    if not reply_message:
        return

    # Get the setting name and value from the reply message text
    setting_text = reply_message.text
    setting_name, setting_value = setting_text.split(" ", 1)
    setting_value = setting_value.lower()

    # Update the group settings
    if setting_name == "auto_delete":
        if setting_value == "on":
            group_settings["auto_delete"] = True
            await message.reply_text("Auto-delete has been turned on for group admins.")
        elif setting_value == "off":
            group_settings["auto_delete"] = False
            await message.reply_text("Auto-delete has been turned off for group admins.")
        else:
            await message.reply_text("Invalid value for auto_delete setting. Please use 'on' or 'off'.")
    elif setting_name == "admins":
        admins = setting_value.split(",")
        group_settings["admins"] = [int(admin.strip()) for admin in admins]
        await message.reply_text("New group admins have been set.")
    elif setting_name == "channels":
        channels = setting_value.split(",")
        group_settings["channels"] = [int(channel.strip()) for channel in channels]
        await message.reply_text("New channels have been set.")
    else:
        await message.reply_text("Invalid setting name. Please use 'auto_delete', 'admins', or 'channels'.")

    # Save the updated group settings
    await save_group(group_id, group_settings)
