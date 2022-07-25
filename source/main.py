import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters, CallbackQueryHandler
from Bot import RoutesettingBot


def init_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    fle_handler = logging.FileHandler('../data/logs', mode='w', encoding='UTF-16')
    fle_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fle_handler.setFormatter(fle_format)
    logger.addHandler(fle_handler)


def main() -> None:
    init_logger()
    routesetter_bot = RoutesettingBot()
    with open('../data/token.txt') as token_file:
        token = token_file.read().strip()
    if not token:
        logging.log(logging.ERROR, 'No app token')
        return
    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher
    start_handler = CommandHandler('start', routesetter_bot.setting_process.start)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(CallbackQueryHandler(routesetter_bot.setting_process.handle_days, pattern="^WJ.+$"))

    dispatcher.add_handler(CallbackQueryHandler(routesetter_bot.setting_process.add_setter, pattern="^add_setter$"))
    updater.start_polling(allowed_updates=Update.ALL_TYPES)
    updater.idle()


if __name__ == "__main__":
    main()
