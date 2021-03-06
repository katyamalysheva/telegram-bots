from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import datetime
import math
from telegram import KeyboardButton
#import logging

STATE = None
BIRTH_YEAR = 1
BIRTH_MONTH = 2
BIRTH_DAY = 3

# function to handle the /start command
def start(update, context):
    first_name = update.message.chat.first_name
    update.message.reply_text(f"Hi {first_name}, nice to meet you!\n We can check your biorhythm, but we need to know your birthday first")
    start_getting_birthday_info(update, context)

def start_getting_birthday_info(update, context):
    global STATE
    STATE = BIRTH_YEAR
    update.message.reply_text(
        f"Tell me what year you were born in?")

def received_birth_year(update, context):
    global STATE
    try:
        today = datetime.date.today()
        year = int(update.message.text)
        if year > today.year or year < 1900:
            raise ValueError("invalid value")
        context.user_data['birth_year'] = year
        update.message.reply_text(
            f"ok, now I need to know the month")
        STATE = BIRTH_MONTH
    except:
        update.message.reply_text("Incorrect year")

def received_birth_month(update, context):
    global STATE
    try:
        today = datetime.date.today()
        month = int(update.message.text)
        if month > 12 or month < 1:
            raise ValueError("invalid value")
        context.user_data['birth_month'] = month
        update.message.reply_text(f"great! And now, the day")
        STATE = BIRTH_DAY
    except:
        update.message.reply_text(
            "Incorrect mounth")

def received_birth_day(update, context):
    global STATE
    try:
        today = datetime.date.today()
        dd = int(update.message.text)
        yyyy = context.user_data['birth_year']
        mm = context.user_data['birth_month']
        birthday = datetime.date(year=yyyy, month=mm, day=dd)
        if today - birthday < datetime.timedelta(days=0):
            raise ValueError("invalid value")
        context.user_data['birthday'] = birthday
        STATE = None
        update.message.reply_text(f'ok, you were born on {birthday}. \nTry /biorhythm to see your biorhythm')
        
    except:
        update.message.reply_text(
            "Incorrect day")

# function to handle the /help command
def help(update, context):
    update.message.reply_text('try /start or /biorhythm')

# function to handle errors occured in the dispatcher 
def error(update, context):
    update.message.reply_text('an error occured')

def text(update, context):
    global STATE
    if STATE == BIRTH_YEAR:
        return received_birth_year(update, context)
    if STATE == BIRTH_MONTH:
        return received_birth_month(update, context)
    if STATE == BIRTH_DAY:
        return received_birth_day(update, context)

# This function is called when the /biorhythm command is issued
def biorhythm(update, context):
    print("ok")
    user_biorhythm = calculate_biorhythm(
        context.user_data['birthday'])
    update.message.reply_text(f"Phisical: {user_biorhythm['phisical']}")
    update.message.reply_text(f"Emotional: {user_biorhythm['emotional']}")
    update.message.reply_text(f"Intellectual: {user_biorhythm['intellectual']}")
def calculate_biorhythm(birthdate):
    today = datetime.date.today()
    delta = today - birthdate
    days = delta.days
    phisical = math.sin(2*math.pi*(days/23))
    emotional = math.sin(2*math.pi*(days/28))
    intellectual = math.sin(2*math.pi*(days/33))
    biorhythm = {}
    biorhythm['phisical'] = int(phisical * 10000)/100
    biorhythm['emotional'] = int(emotional * 10000)/100
    biorhythm['intellectual'] = int(intellectual * 10000)/100
    biorhythm['phisical_critical_day'] = (phisical == 0)
    biorhythm['emotional_critical_day'] = (emotional == 0)
    biorhythm['intellectual_critical_day'] = (intellectual == 0)
    return biorhythm
def main():

    with open('token.txt', 'r') as f:
        TOKEN = f.read()
    # create the updater, that will automatically create also a dispatcher and a queue to
    # make them dialoge
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher


    
    #logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
    # add handlers for start and help commands
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))
    # add an handler for our biorhythm command
    dispatcher.add_handler(CommandHandler("biorhythm", biorhythm))
    # add an handler for normal text (not commands)
    dispatcher.add_handler(MessageHandler(Filters.text, text))
    # add an handler for errors
    dispatcher.add_error_handler(error)
    # start your shiny new bot
    updater.start_polling()
    # run the bot until Ctrl-C
    updater.idle()
if __name__ == '__main__':
    main()