import logging
import os
import tempfile

import telegram.ext
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from search import search
from imutils import read_image
from imutils import get_text_from_image
from image_info import ImageInfo
import make_text
import string

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )

def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Help!\n/search <description> to find an image\n/caption with replied image to see a description')

def make_text_command(update: Update, context: CallbackContext) -> None:
    logging.info("I see a picture")
    picture = update.message.photo[-1]
    file = picture.get_file()
    logging.info("received an image")
    with tempfile.TemporaryDirectory() as d:
        file_path = os.path.join(d, "image.png")
        file.download(file_path)
        logging.info("saved the image")
        hash_ = read_image(file_path)
        if context.bot_data.get((update.message.chat_id, hash_), False):
            logging.info('already have this pic')
        else:
            context.bot_data[(update.message.chat_id, hash_)] = 1
            context.chat_data[update.message.message_id] = ImageInfo(hash_, get_text_from_image(file_path))
            logging.info(len(context.chat_data))
            logging.info('pic was added')

def sticker_to_text_command(update: Update, context: CallbackContext) -> None:
    logging.info("I see a sticker")
    stick = update.message.sticker
    if stick.is_animated:
        return
    file = stick.get_file()
    logging.info("received a sticker")
    with tempfile.TemporaryDirectory() as d:
        file_path = os.path.join(d, "image.png")
        file.download(file_path)
        logging.info("saved the stciker")
        hash_ = read_image(file_path)
        if context.bot_data.get((update.message.chat_id, hash_), False):
            logging.info('already have it')
        else:
            context.bot_data[(update.message.chat_id, hash_)] = 1
            context.chat_data[update.message.message_id] = ImageInfo(hash_, get_text_from_image(file_path))
            logging.info(len(context.chat_data))
            logging.info('sticker was added')

def trans_str(s):
    return s.translate(str.maketrans('', '', string.punctuation))

def search_command(update: Update, context: CallbackContext) -> None:
    if not context.chat_data:
        update.message.reply_text('No photo data')
        return
    MessageToBeReplied = search(trans_str((' '.join(context.args)).lower()), context.chat_data)
    print(trans_str((' '.join(context.args)).lower()))
    for to_reply in MessageToBeReplied:
        context.bot.send_message(chat_id=update.message.chat_id, text=context.chat_data[to_reply].text, reply_to_message_id=to_reply)

def caption_command(update: Update, context: CallbackContext):
    logging.info('caption command')
    if not update.message.reply_to_message:
        return
    logging.info("there's a replied message")
    image_id = update.message.reply_to_message.message_id
    if context.chat_data.get(image_id, False):
         update.message.reply_text(context.chat_data[image_id].text)
    elif update.message.reply_to_message.photo:
        picture = update.message.reply_to_message.photo[-1]
        file = picture.get_file()
        with tempfile.TemporaryDirectory() as d:
            file_path = os.path.join(d, "image.png")
            file.download(file_path)
            logging.info("saved the image")
            hash_ = read_image(file_path)
            if context.bot_data.get((update.message.chat_id, hash_), False):
                logging.info('already have it')
            else:
                context.bot_data[(update.message.chat_id, hash_)] = 1
                context.chat_data[update.message.reply_to_message.message_id] = ImageInfo(hash_, get_text_from_image(file_path))
                logging.info(len(context.chat_data))
                logging.info('image was added')
        update.message.reply_text(context.chat_data[image_id].text)
    else:
        update.message.reply_text("there's no image")

'''def search_pm_command(update: Update, context: CallbackContext) -> None:
    logging.info('search_pm_command')
    update.message.reply_text('Я пока не умею отвечать в лс, но скоро научусь')
'''
'''def description_command(update: Update, context: CallbackContext) -> None:
    logging.info('description_command')
    if not update.message.photo:
        update.message.reply_text('No photo')
        return
    update.message.reply_text('я пока не умею делать описание, но скоро научусь')
'''
def main() -> None:
    """Start the bot."""
    my_persistence = telegram.ext.PicklePersistence(filename='FinalData1.pickle')
    updater = Updater("5074946865:AAFUXJ20UVO618nGVUPqk3xr2yfBvQ6tKE0", persistence=my_persistence, use_context=True)
    #updater = Updater("5074946865:AAFUXJ20UVO618nGVUPqk3xr2yfBvQ6tKE0", use_context=True)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start, run_async=True))
    dispatcher.add_handler(CommandHandler("help", help_command, run_async=True))
    dispatcher.add_handler(CommandHandler("search", search_command, run_async=True))
    dispatcher.add_handler(CommandHandler("caption", caption_command, run_async=True))
    #dispatcher.add_handler(CommandHandler("search_pm", search_pm_command, run_async=True))
    #dispatcher.add_handler(CommandHandler("description", description_command, run_async=True))

    dispatcher.add_handler(MessageHandler(Filters.photo & ~Filters.command, make_text_command, run_async=True))
    dispatcher.add_handler(MessageHandler(Filters.sticker & ~Filters.command, sticker_to_text_command, run_async=True))
    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()