import re

import hangups

from hangupsbot.handlers import Glados, handler
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


@handler.register(priority=6, event=hangups.ChatMessageEvent)
def handle_all_chat_messages(bot, event):
    """Handle autoreplies to keywords in messages"""
    # Test if message is not empty
    if not event.text:
        return
    print("UserName:" + event.user.full_name)
    help_agent=Glados()
    answer = help_agent.get_help(event.text)
    print(answer)
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
