import logging
from telegram import Update
from telegram.ext import Updater, CallbackQueryHandler, Filters, CommandHandler, MessageHandler, ConversationHandler, PollAnswerHandler
from Bot import RoutesettingBot


def init_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    fle_handler = logging.FileHandler('data/logs', mode='w', encoding='UTF-16')
    fle_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fle_handler.setFormatter(fle_format)
    logger.addHandler(fle_handler)
    return


def main() -> None:
    init_logger()
    routesetter_bot = RoutesettingBot()
    with open('data/token.txt') as token_file:
        token = token_file.read().strip()
    if not token:
        logging.log(logging.ERROR, 'No app token')
    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('set', routesetter_bot.scheduler.set_default_jobs))
    dispatcher.add_handler(CallbackQueryHandler(routesetter_bot.scheduler.handle_tuesday, pattern='^' + 'ВТ' + '$'))
    dispatcher.add_handler(CallbackQueryHandler(routesetter_bot.scheduler.handle_thursday, pattern='^' + 'ЧТ' + '$'))
    dispatcher.add_handler(CallbackQueryHandler(routesetter_bot.scheduler.handle_tt, pattern='^' + r'ВТ\+ЧТ' + '$'))
    dispatcher.add_handler(CallbackQueryHandler(routesetter_bot.scheduler.handle_not, pattern='^' + 'Нет' + '$'))
    start_handler = CommandHandler(['start', 'help'], routesetter_bot.start)
    dispatcher.add_handler(start_handler)
    admin_menu_handler = ConversationHandler(entry_points=[CommandHandler('admin_menu', routesetter_bot.menu.admin_menu)],
                                             states={
            routesetter_bot.menu.ADMIN_START: [
                CallbackQueryHandler(routesetter_bot.menu.add_setter_button, pattern='^' + 'add_setter' + '$'),
                CallbackQueryHandler(routesetter_bot.menu.remove_setter_button, pattern='^' + 'remove_setter' + '$'),
                CallbackQueryHandler(routesetter_bot.menu.add_contest_button, pattern='^' + 'add_contest' + '$'),
                CallbackQueryHandler(routesetter_bot.menu.remove_contest_button, pattern='^' + 'remove_contest' + '$'),
                CallbackQueryHandler(routesetter_bot.change_button, pattern='^' + 'change' + '$'),
            ],
            routesetter_bot.menu.AWAIT_CONTEST: [
                MessageHandler(Filters.regex(r'^\d{2}\.\d{2}\.\d{4} [A-z0-9_ -]+ \d{1,5} ?$'), routesetter_bot.menu.add_contest_info),
            ],
            routesetter_bot.menu.AWAIT_SETTER: [MessageHandler(Filters.regex('^@[A-z0-9_-]+ ?$'), routesetter_bot.menu.choose_setter)],
            routesetter_bot.menu.AWAIT_PEOPLE: [MessageHandler(Filters.regex('^(@[A-z0-9_-]+ ?)+$'), routesetter_bot.menu.add_contest_setters)]},
                                             fallbacks=[CommandHandler("stop", routesetter_bot.stop)], conversation_timeout=120)
    dispatcher.add_handler(admin_menu_handler)
    menu_handler = ConversationHandler(entry_points=[CommandHandler('menu', routesetter_bot.menu.setter_menu)],
                                       states={
            routesetter_bot.menu.START: [
                CallbackQueryHandler(routesetter_bot.menu.handle_setting_table, pattern='^' + '1' + '$'),
                CallbackQueryHandler(routesetter_bot.menu.handle_results, pattern='^' + '2' + '$'),
                CallbackQueryHandler(routesetter_bot.menu.handle_the_richest, pattern='^' + '3' + '$'),
                CallbackQueryHandler(routesetter_bot.menu.handle_additional_results, pattern='^' + '4' + '$'),
            ],
            routesetter_bot.menu.AWAIT_RESULT: [MessageHandler(Filters.regex(r'^\d{2}\.\d{2}\.\d{4}( \d){5} ?$'), routesetter_bot.menu.add_single_results)]},
                                       fallbacks=[CommandHandler("stop", routesetter_bot.stop)], conversation_timeout=120)
    dispatcher.add_handler(menu_handler)
    dispatcher.add_handler(PollAnswerHandler(routesetter_bot.scheduler.receive_after_setting_poll))
    unknown_handler = MessageHandler(Filters.command, routesetter_bot.unknown)
    dispatcher.add_handler(unknown_handler)
    updater.start_polling(allowed_updates=Update.ALL_TYPES)
    updater.idle()
    return


if __name__ == '__main__':
    main()
