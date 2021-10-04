import telegram
import subprocess
import os
import ntpath
import sys
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
import argparse
import logging


"""
Using arguments to enter the program from cmd:
python tg.py --token yourtokenhere --dl_path yourdownloadpathhere
"""
parser = argparse.ArgumentParser(description="login to telegram bot")
parser.add_argument("-d", "--debug", help="debug the program", action="store_true")
parser.add_argument("-t", "--token", help="add your token to the program", required=True)
parser.add_argument("-p", "--dl_path", help="write your directory", default=r'c:\downloads')

args = parser.parse_args()
if args.debug:
    print("debugging")
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

TOKEN = args.token
DOWNLOADS_PATH = args.dl_path


class File(object):
    """
    Class functions to fetch file later in command_cmd function.
    """
    name = ''
    __data__ = bytes()

    def read(self):
        return bytes(self.__data__)

    def write(self, data):
        self.__data__ += data

    def close(self):
        return

    def __init__(self, name, data):
        self.name = name
        self.__data__ = bytes(data, 'utf8')


def command(x):
    # Command function to use in cmd functions
    t = subprocess.getoutput(x)
    return t


def command_cmd(update, context):
    """
    cmd function. works in the bot like so:
    /cmd -yourcmdcommand-
    Returns in the bot your output
    """
    x = update.message.text
    x = x[5:]
    try:
        command_output = command(x)
        if len(command_output) > 4000:
            # if your output is longer than 4000 characters, the bot sends a file with the output to you.
            invalid_chars = ['\\', ':', '*', '<', '>', '|', '"', '?', '/']
            for c in invalid_chars:
                x = x.replace(c, '.')
            new = File(x, command_output)
            context.bot.send_document(chat_id=update.message.chat_id, document=new)
        else:
            context.bot.send_message(chat_id=update.message.chat_id, text=command_output)

    except Exception as e:
        context.bot.send_message(chat_id=update.message.chat_id, text=str(e))


def file_cmd(update, context):
    """
    file function. can change your file name,path and extention with string in caption.
    1. Drag file to the bot.
    2. write in caption new path and name:
    c:\newfolder\newfilename.newfileext
    The bot transfers your file to the new folder
    """
    f = update.message.document.get_file()
    if not update.message.caption:
        # if you write nothing in the caption - copies file to dl-path.
        d = os.path.join(DOWNLOADS_PATH, update.message.document.file_name)
    else:
        d = os.path.join(os.path.dirname(update.message.caption), ntpath.basename(update.message.caption))
    try:
        f.download(d)
    except Exception as e:
        context.bot.send_message(chat_id=update.message.chat_id, text=str(e))


def get_cmd(update, context):
    """get function. works in the bot like so:
    /get c:\foldername\filename.fileext
    the bot sends you the file specified.
    """
    x = update.message.text
    x = x[5:]
    try:
        context.bot.send_document(chat_id=update.message.chat_id, document=open(x, 'rb'))
    except Exception as e:
        context.bot.send_message(chat_id=update.message.chat_id, text=str(e))


if __name__ == '__main__':
    updater = Updater(token=TOKEN)
    dispatcher = updater.dispatcher

    command_handler = CommandHandler('cmd', command_cmd)
    dispatcher.add_handler(command_handler)

    get_handler = CommandHandler('get', get_cmd)
    dispatcher.add_handler(get_handler)

    generic_handler = MessageHandler(Filters.document, file_cmd)
    dispatcher.add_handler(generic_handler)

    q = updater.start_polling()
