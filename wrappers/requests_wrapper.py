#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""requests.py: wraps all project's requests."""

__author__ = 'Tony Schneider'
__email__ = 'tonysch05@gmail.com'

import requests
import json
import logging
from typing import Union
from retry import retry


class RequestWrapper:
    """
    Implementing as class in case we will add other functionality / methods
    """

    def __init__(self, headers: dict = None):
        """
        We're using request session to save cookies after the first request as well as handled default headers.
        :param headers: request headers
        """
        self.session = requests.Session()
        self.session.headers = headers

    @retry(exceptions=ConnectionResetError, tries=3, delay=2, jitter=2)
    def perform_request(self, method: str, url: str, params: dict = None) -> Union[dict, None]:
        """
        This method responsible on all our requests in the project. each get/post request is being done here.
        This method covered with 'retry' decorator so each temporary error connection handled and the method
        tries another time.
        Also, each connection error saves into a log file.
        :param method: the request method - GET / POST
        :param url: end point
        :param params: request's additional parameters to our request's urls
        :return: response content that parsed as JSON if there was no connection error.
        """
        parsed_response = None
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
            )
            response.raise_for_status()
            parsed_response = json.loads(response.content.decode('utf8'))
        except Exception:
            logging.exception(f"There was a connection error with '{url}' request API | params - '{params}'.")

        return parsed_response
