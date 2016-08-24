import re

import hangups
import requests

from hangupsbot.configuration.properties import Properties
from hangupsbot.handlers import handler
from hangupsbot.utils import text_to_segments


def is_valid_mail (mail):
    regex = '^[0-9]{5,}@thoughtworks.com$'
    return True if re.match(regex, mail) else False


@handler.register(priority=6, event=hangups.ChatMessageEvent)
def handle_all_chat_messages(bot, event):
    # Test if message is not empty
    properties = Properties()
    if not event.text:
        return

    user_emails = event.user.emails
    valid_email = next((mail for mail in user_emails if is_valid_mail(mail)), None)

    if valid_email:
        employee_id = valid_email.split("@")[0]
        response = requests.post(properties.get_string("api.help.urllink"), {"text": event.text, "ID": employee_id})
        answer = response.json()["reply"]
    else:
        answer = "I can't recognise you. Kindly consult the admin team."

    yield from event.conv.send_message(text_to_segments(answer))
    return
