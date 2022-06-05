from telegram import Update, constants
from telegram.ext import CallbackContext
from typing import Dict
import logging

logger = logging.getLogger('utils')


def is_admin_choice(context: CallbackContext, info) -> bool:
    chat_member = context.bot.getChatMember(info['chat_id'], info['user_id'])
    if chat_member.status != constants.CHATMEMBER_CREATOR:
        info['query'].answer(text='Ты не Босс. Только он может выбрать')
        return False
    info['query'].edit_message_text(text=f"Выбранная опция: {info['query'].data}")
    logger.info(f'Owner selected {info["query"].data}')
    return True


def get_button_tap_info(update: Update) -> Dict:
    query = update.callback_query
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    username = update.effective_user.username.strip().lower()
    logger.info(f'{username} tried to choose the option in admin menu')
    info = {'query': query, 'chat_id': chat_id, 'user_id': user_id}
    return info


def is_admin_message(update: Update, context: CallbackContext) -> bool:
    message = update.effective_message.text
    user = update.effective_user.username.strip().lower()
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    logger.info(f'{user} tried to send the "{message}"')
    chat_member = context.bot.getChatMember(chat_id, user_id)
    if chat_member.status != constants.CHATMEMBER_CREATOR:
        update.message.reply_text(f'Ты не Босс. Только он может написать {message}')
        return False
    return True
