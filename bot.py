import random
import os
from helpers import helpers
from pyrogram import Client, filters
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from video import download, remove, gen_thumb
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ProcessPoolExecutor

#region api_id api_hash bot_token
api_id = 
api_hash = ""
bot_token = ""
#endregion

PATH = 'cache/'

if not os.path.exists('cache'):
    os.mkdir('cache')
if not os.path.exists('thumbs'):
    os.mkdir('thumbs')

helper = helpers()
app = Client("my_account", api_id=api_id, api_hash=api_hash, bot_token=bot_token)
ADMIN_LIST = [] #users get whitelisted on the whitelist file, admin can add users to the whitelist using the bot.

def is_admin(id):
    if id not in ADMIN_LIST:
        return False
    else:
        return True

def handle_video(url, file_name, chat_id, caption, uid):
    rc = download(url, file_name)
    duration = helper.get_duration(file_name)
    if rc == 0:
        try:
            thumb = gen_thumb(file_name) 
            if os.path.isfile('thumbs/thumb_' + str(uid)):
                message = app.send_video(chat_id, PATH + file_name, caption, thumb='thumbs/thumb_' + str(uid), duration=duration) 
            elif thumb != 'null':
                message = app.send_video(chat_id, PATH + file_name, caption, 'thumbs/' + thumb, duration=duration)
            else:
                message = app.send_video(chat_id, PATH + file_name, caption, duration=duration)
        except:
            remove(PATH + file_name)
            remove('thumbs/' + thumb)
        # app.forward_messages(chatid, message.chat.id, message.message_id) #uncomment this if you want to forward everything somewhere
        remove(PATH + file_name)
        remove('thumbs/' + thumb)
    else:
        remove(PATH + file_name)
        remove('thumbs/' + thumb)       


@app.on_message(filters.command('push'))
def push_to_list(client, message):
    chat_id = message.chat.id
    if not is_admin(chat_id):
        return
    message2 = message.text 
    message2 = message2.split()
    helper.add_to_whitelist(message2[1])
    message.reply_text('User added to whitelist')

@app.on_message(filters.command('pull'))
def pull_from_list(client, message):
    chat_id = message.chat.id
    if not is_admin(chat_id):
        return
    message2 = message.text 
    message2 = message2.split()
    helper.remove_whitelist(message2[1])
    message.reply_text('User removed from whitelist')

executors = {
    'default': {'type': 'threadpool', 'max_workers': 500},
    'processpool': ProcessPoolExecutor(max_workers=500)
}
scheduler = AsyncIOScheduler(executors=executors)
@app.on_message(filters.regex(r'https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,}') & ~filters.command(['start', 'help', 'push', 'pull', 'id', 'delete_thumb', 'thumb']))
def start_job(client, message):
    n = random.randint(10000000, 99999999) #add some random shit to allow people to download the same thing at the same time
    chat_id = message.chat.id
    text = message.text
    splited = text.split(" | ")
    test = text.split()     
    uid = message.from_user.id
    url = splited[0]
    is_valid = helper.b_valid_url(url)
    # for x in range(len(test)):
        # if test[x].isnumeric():
        #     message.forward( chat_id=-1001372231901, from_chat_id=message.chat.id, message_ids=message.message_id)
    if not helper.b_whitelisted(chat_id):
        message.reply_text('Usuário não autorizado, contacte @anticongelante para se informar e obter acesso')
        return
    if not is_valid:
        message.reply_text('Connection error thrown at ' + url, quote=True)
        return
    ext = helper.get_ext(url)
    if not ext:
        message.reply_text('Failed to get content-type from headers, using mp4 as fallback ', quote=True)
        ext = '.mp4'
    if len(splited) < 2:
        caption = url   #just for now xD
        file_name = str(n) + ext
    else:
        caption = splited[1] 
        file_name = str(n) + ext
    message.reply_text('Trying to download: ' + url)
    scheduler.add_job(handle_video, args=(url, file_name, chat_id, caption, uid), max_instances=500)

@app.on_message(filters.photo & filters.command(['thumb']))
def set_thumb(client, message):
    uid = message.from_user.id
    try:
        if os.path.isfile('thumbs/thumb_' + str(uid)):
            remove('thumbs/thumb_' + str(uid))
        client.download_media(message=message, file_name='thumbs/thumb_' + str(uid)) #no extension cuz fuck it
        message.reply_text("Thumbnail set for user: " + str(uid))
    except Exception:
        message.reply_text("Failed to download media, check logs")

@app.on_message(filters.command('id'))
def get_id(client, message):
    uid = message.chat.id
    message.reply_text('Your ID is: ' + str(uid))

@app.on_message(filters.command('delete_thumb'))
def delete_thumb(client, message):
    uid = message.from_user.id
    if os.path.isfile('thumbs/thumb_' + str(uid)):
        remove('thumbs/thumb_' + str(uid))
        message.reply_text('thumbnail deleted')
    else:
        message.reply_text('No thumbnail found')

@app.on_message(filters.command(['start', 'help']))
def help(client, message):
    message.reply_text("""
    Usage: 
    URL | NAME 
    in case name is omitted a random one will be generated

    To set a default thumbnail just send a new image file maximum 200kb (i never tested this feature so it may break everything xD)
    To delete the current thumbnail use /delete_thumb
    """)


scheduler.start()
app.run()
