#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Author: Tony Schneider

"""
To make the bot work, please fill the following keys at the slack and twitter configuration files that
located in configurations folder:
TW:
- access_token
- access_token_secret
- api_key
- api_key_secret
- personal_username
Slack:
- bot_user_oauth_token
- default_channel_id
"""

import sys
import logging
from datetime import datetime, timedelta
from wrappers.config_wrapper import ConfigWrapper
from wrappers.slack_bot_wrapper import SlackBotWrapper
from wrappers.twitter_wrapper import TwitterWrapper
from logging.config import dictConfig

dictConfig(ConfigWrapper().get_config_file("logging"))
logger = logging.getLogger(__name__)

slack_bot_obj = SlackBotWrapper()
twitter_obj = TwitterWrapper()


@slack_bot_obj.message_handler(commands=['!now'])
def send_current_time(message):
    slack_bot_obj.send_message_to_channel(
        text_message=datetime.now().strftime("Current time - %d/%m/%Y %H:%M:%S"),
        thread_ts=message['message_obj']['ts'],
    )


@slack_bot_obj.message_handler(commands=['!new-content'])
def send_current_time(message: dict) -> None:
    content_lang = message['additional_text'] or 'python'

    if content_lang and content_lang not in twitter_obj.tw_config['tw_users'].keys():
        slack_bot_obj.send_message_to_channel(text_message=f"Invalid language - '{content_lang}'")
        return

    slack_bot_obj.send_message_to_channel(text_message=f"Searching new content for {content_lang}...")
    latest_tweets = twitter_obj.get_latest_tweets(content_lang)

    if latest_tweets:
        for tweet in latest_tweets:
            slack_bot_obj.send_message_to_channel(text_message=f"From: {tweet['from']}\nTweet: {tweet['text']}")
    else:
        slack_bot_obj.send_message_to_channel(text_message=f"There is no new content for {content_lang}")


@slack_bot_obj.message_handler(commands=['!tweet'])
def send_current_time(message):
    if not message['additional_text']:
        slack_bot_obj.send_message_to_channel(text_message=f"Please provide a message after !tweet.")
        return

    # Did we publish the tweet?
    if twitter_obj.publish_new_tweet(message['additional_text']):
        slack_bot_obj.send_message_to_channel(
            text_message=f"The tweet '{message['additional_text']}' has been published successfully."
        )
    else:
        slack_bot_obj.send_message_to_channel(text_message=f"Didn't manage to publish a new tweet.")


def main(*args, **kwargs) -> int:
    try:
        logger.info('Starting bot... Press CTRL+C to quit.')
        slack_bot_obj.start_handlers(schedule_hourly_timer=True, tw_obj=twitter_obj)
    except KeyboardInterrupt:
        logger.info('Quitting... (CTRL+C pressed)')
        return 0
    except Exception:   # Catch-all for unexpected exceptions, with stack trace
        logger.exception(f'Unhandled exception occurred!')
        return 1


if __name__ == '__main__':
    sys.exit(main(*sys.argv[1:]))

