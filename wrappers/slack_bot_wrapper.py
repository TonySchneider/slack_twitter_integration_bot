#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""slack_bot_wrapper.py: wraps all Slack api requests by using 'requests' lib."""

__author__ = 'Tony Schneider'
__email__ = 'tonysch05@gmail.com'

import logging
from time import sleep
from datetime import datetime, timedelta
from threading import Thread
from typing import Union, Callable, List, Optional
from wrappers.config_wrapper import ConfigWrapper
from wrappers.requests_wrapper import RequestWrapper
from wrappers.twitter_wrapper import TwitterWrapper


class SlackBotWrapper:

    def __init__(self):
        """
        This class wrappers all necessary methods that we will use in our bot handlers.
        Also, this class loads the necessary configurations like slack credentials and request urls.
        We don't use here any other python library except to 'requests' built-in lib.
        """
        self.slack_config = ConfigWrapper().get_config_file('slack_configurations')
        self.default_headers = {
            **self.slack_config['default_headers'],
            **{'Authorization': f"Bearer {self.slack_config['bot_user_oauth_token']}"},
        }
        self.message_handlers = []
        self.handled_messages = []
        self.request_obj = RequestWrapper(headers=self.default_headers)
        self._threads = []

    def send_message_to_channel(self, text_message: str, channel_id: str = None, thread_ts: str = None) -> bool:
        """
        This method sends a message to channel. It uses the channel id from slack_configurations.yaml by default.
        :param thread_ts: thread time stamp
        :param text_message: text message
        :param channel_id: channel id
        :return: True - the message sent successfully.
        """
        send_status = False
        params = {
            'channel': self.slack_config['default_channel_id'] if not channel_id else channel_id,
            'text': text_message,
        }
        if thread_ts:
            params['thread_ts'] = thread_ts
            params['reply_broadcast'] = 'true'

        response_content = self.request_obj.perform_request(method='POST',
                                                            url=self.slack_config['post_message_url'],
                                                            params=params)
        if response_content:
            logging.info(f"The message '{text_message}' was sent successfully to "
                        f"'{params['channel']}' channel via slack bot. response_content - '{response_content}'")
            send_status = True

        return send_status

    def get_list_of_channels(self) -> Union[list, None]:
        """
        This method returns a list of channels that the bot related them.
        :return: list of channels
        """
        response_content = self.request_obj.perform_request(method='GET',
                                                            url=self.slack_config['get_list_of_channels_url'])

        return response_content

    def get_latest_messages(self, channel_id: str = None) -> Optional[list]:
        """
        This method returns the latest messages (5 second ago) so we can handle them and check with our
        thread handlers if there are any command.
        :return: list of latest messages.
        """
        messages = None
        params = {
            'channel': self.slack_config['default_channel_id'] if not channel_id else channel_id,
            'inclusive': 'true',
            'oldest': (datetime.now() - timedelta(seconds=5)).timestamp()
        }

        response_content = self.request_obj.perform_request(method='GET',
                                                            url=self.slack_config['get_messages_url'],
                                                            params=params)

        if isinstance(response_content, dict) and response_content['ok']:
            messages = response_content['messages']
        return messages

    def thread_wrapper(self, handler: Callable, commands: list) -> None:
        """
        Thread wrapper that checks if the commands appear in current messages.
        :param handler: function as handler
        :param commands: commands to be handled
        """
        while True:
            current_messages = self.get_latest_messages()

            if not current_messages:
                continue

            for message in current_messages:
                for command in commands:
                    if message['text'].startswith(command) and message['ts'] not in self.handled_messages:
                        logging.info(f"'{command}' command appeared")
                        additional_text = message['text'].replace(command, '').strip()
                        handler({
                            'message_obj': message,
                            'additional_text': (additional_text if additional_text else None)
                        })
                        self.handled_messages.append(message['ts'])

            sleep(1)

    def start_handlers(self, tw_obj: TwitterWrapper, schedule_hourly_timer: bool = True) -> None:
        """
        This method starts all our messages handlers so our threads that runs in background will be able
         to catch all commands.
        """
        self._threads.append(Thread(target=tw_obj.new_tweets_consumer, args=(self,), daemon=True))

        if schedule_hourly_timer:
            self._threads.append(Thread(target=self.hourly_timer, daemon=True))

        for handler_details in self.message_handlers:
            self._threads.append(Thread(
                target=self.thread_wrapper,
                args=(handler_details['function'], handler_details['commands']),
                daemon=True,    # Don't want the thread to block exit
            ))

        for t in self._threads:
            t.start()

        logging.info("Slack bot has been activated.")

        for t in self._threads:
            t.join()

    def message_handler(self, commands: List[str]) -> Callable:
        """
        Message handler decorator.
        This decorator can be used to decorate functions that must handle certain types of messages.
        All message handlers are tested in the order they were added.
        """
        def decorator(handler):
            self.message_handlers.append({'function': handler, 'commands': commands})
            return handler

        return decorator

    def hourly_timer(self) -> None:
        """
        This method responsible on the hourly timer that sens every hour the current time.
        :return: None
        """
        while True:
            self.send_message_to_channel(
                text_message=datetime.now().strftime("Current time - %d/%m/%Y %H:%M:%S (Scheduled hourly timer)")
            )
            sleep(3600)
