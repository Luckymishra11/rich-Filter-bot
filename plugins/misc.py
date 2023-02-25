from utils import *
from info import *
from pyrogram import Client, filters 
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton 

@Client.on_message(filters.command("start") & ~filters.channel)
async def start(bot, message):
    await add_user(message.from_user.id, message.from_user.first_name)
    await message.reply(text=script.START.format(message.from_user.mention),
                        disable_web_page_preview=True,
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ➕', url=f'http://t.me/yourfindbot?startgroup=true')
            ],[InlineKeyboardButton("ʜᴇʟᴘ", callback_data="misc_help"),
                                                            InlineKeyboardButton("ʙᴜʏ", callback_data="misc_buymoney")]]))  
@Client.on_message(filters.command("help"))
async def help(bot, message):
    await message.reply(text=script.HELP, 
                        disable_web_page_preview=True)

@Client.on_message(filters.command("stats"))
async def stats(bot, message):
    g_count, g_list = await get_groups()
    u_count, u_list = await get_users()
    await message.reply(script.STATS.format(u_count, g_count))

@Client.on_message(filters.command("id"))
async def id(bot, message):
    text = f"Current Chat ID: `{message.chat.id}`\n"
    if message.from_user:
       text += f"Your ID: `{message.from_user.id}`\n"
    if message.reply_to_message:
       if message.reply_to_message.from_user:
          text += f"Replied User ID: `{message.reply_to_message.from_user.id}`\n"
       if message.reply_to_message.forward_from:
          text += f"Replied Message Forward from User ID: `{message.reply_to_message.forward_from.id}`\n"
       if message.reply_to_message.forward_from_chat:
          text += f"Replied Message Forward from Chat ID: `{message.reply_to_message.forward_from_chat.id}\n`"
    await message.reply(text)

@Client.on_callback_query(filters.regex(r"^misc"))
async def misc(bot, update):
    data = update.data.split("_")[-1]
    if data == "home":
        await update.message.edit(
            text=script.START.format(update.from_user.mention),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ʜᴇʟᴘ", callback_data="misc_help"),
                                                InlineKeyboardButton("ʙᴜʏ", callback_data="misc_buymoney")]])
        )
    elif data == "help":
        await update.message.edit(
            text=script.HELP,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="misc_home")]])
        )
    elif data == "buymoney":
        await update.message.edit(
            text=script.BUY.format((await bot.get_me()).mention),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("Qr", callback_data="buy_qr")],[
         InlineKeyboardButton("Upi", callback_data="buy_upi")],[
         InlineKeyboardButton("Mdisk Views", callback_data="buy_mdisk")]
    ])) 

         
@Client.on_message(filters.command("buy"))
async def buy(bot, message):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("QR", callback_data="buy_qr")],[
            InlineKeyboardButton("UPI", callback_data="buy_upi")],[
            InlineKeyboardButton("MDISK VIEWS", callback_data="buy_mdisk")]
        ])
        await message.reply("How do you want to pay?", reply_markup=keyboard)


@Client.on_callback_query(filters.regex(r"^buy"))
async def process_buy(bot, update):
    data = update.data.split("_")[-1]
    if data == "qr":
        # send photo
        photo_url = "https://graph.org/file/db1daea93ee48ce96b809.jpg"  # replace with your QR image URL
        await bot.send_photo(chat_id=update.message.chat.id, photo=photo_url)
        text = "Pay 40 Ruppe and then send a screenshot of the payment below, and also provide your group ID so I can verify After Sending Verification Request."
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Send Screenshot", url=f'https://t.me/cyniteofficial')]
        ])
        await bot.send_message(chat_id=update.message.chat.id, text=text, reply_markup=keyboard)
    elif data == "upi":
        # send message and button
        text = "`jaswindersingh42794@oksbi`\nPay 40 Ruppe and then send a screenshot of the payment below, and also provide your group ID After Sending Verification Request. can verify the payment."
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Send Screenshot", url=f'https://t.me/cyniteofficial')]
        ])
        await bot.send_message(chat_id=update.message.chat.id, text=text, reply_markup=keyboard)
    elif data == "mdisk":
        # send message and button
        text = "Send 1000 Mdisk Views To `1883570185` and then send a Message To The Bot Owner."
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Message", url=f'https://t.me/cyniteofficial')]
        ])
        await bot.send_message(chat_id=update.message.chat.id, text=text, reply_markup=keyboard)

 
