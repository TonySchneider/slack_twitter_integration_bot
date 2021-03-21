#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Author: Tony Schneider
from threading import Thread

import tweepy
import logging
from time import sleep
from datetime import timedelta, datetime, timezone
from typing import Union
from wrappers.config_wrapper import ConfigWrapper


class TwitterWrapper:

    def __init__(self):
        """
        This class wrappers all necessary method that we will use in our bot handlers.
        Also, this class loads the necessary configurations like tw credentials and request urls.
        We're using here tweepy (python library) that do for us the oauth and creates API object to be able publish
        tweets and pull them from other users.
        """
        self.tw_config = ConfigWrapper().get_config_file('twitter_configurations')
        self.auth = tweepy.OAuthHandler(self.tw_config['api_key'], self.tw_config['api_key_secret'])
        self.auth.set_access_token(self.tw_config['access_token'], self.tw_config['access_token_secret'])
        self.api_obj = tweepy.API(self.auth)
        logging.debug("Pulling tweets from personal TW account...")
        self.handled_tweets = self.get_latest_tweets(personal_user=True, all_tweets=True)
        self._threads = []

    def get_latest_tweets(self, language: str = None, delta_time: timedelta = timedelta(hours=1), personal_user: bool = False, all_tweets: bool = False) -> Union[list, None]:
        """
        This method returns the latest (1 hour ago) posts of our saved users in "twitter_configurations".
        It returns the posts according to provided language.
        :return: posts as list if they exist
        """
        delta = datetime.utcnow() - delta_time
        tweets = []

        tw_users = [self.tw_config['personal_username']] if personal_user else self.tw_config['tw_users'][language]

        for tw_user in tw_users:
            for tweet in tweepy.Cursor(self.api_obj.user_timeline,
                                       screen_name=tw_user,
                                       exclude_replies=True,
                                       count=1).items():
                if (tweet.created_at > delta and hasattr(tweet, 'text')) or all_tweets:
                    tweets.append({'from': tw_user, 'text': tweet.text, 'created_at': tweet.created_at, 'tweet_id': tweet.id})
                else:
                    break

        return tweets

    def publish_new_tweet(self, text: str) -> bool:
        """
        This method publishes a new tweet by the provided text to our personal TW account.
        :param text: tweet text
        :return: True if the tweet has been published successfully
        """
        publish_status = False
        try:
            self.api_obj.update_status(text)
            publish_status = True
            logging.info(f"published {text} tweet.")
        except tweepy.error.TweepError:
            logging.exception(f"Didn't manage to publish a new tweet to our personal timeline.")

        return publish_status

    def new_tweets_consumer(self, slack_bot):
        """
        The thread task method for the new tweets consumer.
        :return:
        """
        while True:
            latest_tweets = self.get_latest_tweets(delta_time=timedelta(minutes=5), personal_user=True)
            for latest_tweet in latest_tweets:
                if latest_tweet['tweet_id'] not in self.handled_tweets:
                    slack_bot.send_message_to_channel(text_message=f"From: {latest_tweet['from']}\nTweet: {latest_tweet['text']}")
                    self.handled_tweets.append(latest_tweet['tweet_id'])
            sleep(1)
