import re

import hangups
import requests

from hangupsbot.handlers import handler
from hangupsbot.utils import word_in_text, text_to_segments


def find_keyword(kw, text):
    """Return True if keyword is in text"""
    if kw == "*":
        return True
    elif kw.lower().startswith("regex:") and re.search(kw[6:], text, re.DOTALL | re.IGNORECASE):
        return True
    elif word_in_text(kw, text):
        return True
    else:
        return False


@handler.register(priority=7, event=hangups.ChatMessageEvent)
def handle_autoreply(bot, event):
    """Handle autoreplies to keywords in messages"""
    # Test if message is not empty
    if not event.text:
        return
    print("HANDLE AUTO REPLY")
    # Test if autoreplies are enabled
    if not bot.get_config_suboption(event.conv_id, 'autoreplies_enabled'):
        return

    # Test if there are actually any autoreplies
    return
    autoreplies_list = bot.get_config_suboption(event.conv_id, 'autoreplies')
    if not autoreplies_list:
        return

    for kwds, sentence in autoreplies_list:
        for kw in kwds:
            if find_keyword(kw, event.text):
                yield from event.conv.send_message(text_to_segments(sentence))
                break

def is_valid_mail (mail):
    regex = '^[0-9]{5,}@thoughtworks.com$'
    return True if re.match(regex, mail) else False

@handler.register(priority=6, event=hangups.ChatMessageEvent)
def handle_all_chat_messages(bot, event):
    """Handle autoreplies to keywords in messages"""
    # Test if message is not empty
    if not event.text:
        return

    user_emails = event.user.emails
    employee_id = next((mail for mail in user_emails if is_valid_mail(mail)), None).split("@")[0]

    response = requests.post("http://localhost:4000/api/help", {"text": event.text, "ID": employee_id})
    answer = response.json()['answer']
    yield from event.conv.send_message(text_to_segments(answer))
    return
    # Test if autoreplies are enabled
    if not bot.get_config_suboption(event.conv_id, 'autoreplies_enabled'):
        return

    # Test if there are actually any autoreplies
    autoreplies_list = bot.get_config_suboption(event.conv_id, 'autoreplies')
    if not autoreplies_list:
        return

    for kwds, sentence in autoreplies_list:
        for kw in kwds:
            if find_keyword(kw, event.text):
                yield from event.conv.send_message(text_to_segments(sentence))
                break
