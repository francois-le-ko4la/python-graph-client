#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=too-many-instance-attributes, try-except-raise
# pylint: disable=dangerous-default-value, too-few-public-methods
"""Python GraphQL Client."""
from __future__ import annotations

import datetime
import http
import json
import logging
import os
import re
import sys
from enum import Enum, IntEnum, unique
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional, TypeVar, cast

import requests

# Function type
F = TypeVar('F', bound=Callable[..., Any])

# by default don't print traceback
# changed by the --verbose option
sys.tracebacklimit = 0

# logging
logger: logging.Logger = logging.getLogger("GraphClient")


# exit values
@unique
class ExitStatus(IntEnum):
    """Define Exit status."""

    EX_OK: int = getattr(os, 'EX_OK', 0)
    EX_KO: int = 1
    EX_CONFIG: int = getattr(os, 'EX_CONFIG', 78)


@unique
class Constants(Enum):
    """Define constants."""

    CHK_PYT_MIN: tuple[int, int, int] = (3, 7, 0)
    TIMEOUT: int = 30
    TOKEN_EXT: str = "token"
    REFRESH_TOKEN: int = 1     # 1: 1 Hour
    ENCODING: str = "UTF-8"


@unique
class Message(Enum):
    """Define messages."""

    ARGS: str = "Arguments: %s"
    PYT_INF: str = "Python version is supported: %s"
    PYT_ERR: str = "Python version is not supported: %s"
    PYT_DEB: str = "Python: %s"
    KEYFILE_INFO: str = "Key file: %s"
    KEYFILE_ERROR: str = "Key file: %s %s"
    TOKEN_FOUND: str = "Token file: %s"
    TOKEN_READ: str = "Token: Read the token."
    TOKEN_OLD: str = "Token: Your file is too old -> delete token."
    TOKEN_GET: str = "Token: Get current token in your file."
    TOKEN_DEL: str = "Token: Close your session and delete you token file."
    TOKEN_WRITE: str = "Token: write the new token."
    BASE_URL: str = "Base url: %s"
    VERBOSE_MODE: str = "Enable verbose mode."
    TOKEN_TIMESTAMP: str = "Current token timestamp: %s"


def valid_python() -> bool:
    """Check python.

    This function check Python version, log the result and return a status
    True/False.

    Returns:
        True if successful, False otherwise.

    """
    # Python __version__
    current_version: tuple[int, int, int] = sys.version_info[:3]
    current_version_txt: str = ".".join(map(str, current_version))

    if current_version < Constants.CHK_PYT_MIN.value:
        logger.error(Message.PYT_ERR.value, current_version_txt)
        logger.debug(sys.version)
        return False
    logger.info(Message.PYT_INF.value, current_version_txt)
    logger.debug(sys.version)
    return True


def http_patch_log(*args: Any) -> None:
    """Patch the http.client.print function to generate log."""
    logger.debug(" ".join(args))


def enable_logging() -> None:
    """Enable login to analyze the requests."""
    # verbose traceback
    sys.tracebacklimit = None
    # enable debug
    http.client.HTTPConnection.debuglevel = 1
    # patch http.client.print
    http.client.print = http_patch_log
    # simple logging setup
    logging.basicConfig(level=logging.DEBUG)
    logger.info(Message.VERBOSE_MODE.value)


def request_exception(func: F) -> F:
    """Wrap the passed in function and logs exceptions.

    We have 3 function with request therefore we want an homogeneous exception
    management with this decorator.
    """

    @wraps(func)
    def func_wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            # give info
            logger.info("%s: new request in progress.", func.__name__)
            # run the function
            return func(*args, **kwargs)
        # track all exception and finish with a generic "Exception"
        except (requests.exceptions.HTTPError,
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
                requests.exceptions.RequestException, Exception) as err:
            msg = f"{func.__name__} - {type(err).__name__} raised: {err}"
            logger.error(msg)
            raise
    return cast(F, func_wrapper)


class GraphClient:
    """Define the GraphQL Client."""

    def __init__(self, json_keyfile: str, **kwargs: Any) -> None:
        """Initialize the Class."""
        self.__base_url: str = ""
        self.__json_key: dict[str, str] = {}
        self.__token: str = ""
        self.__headers: dict[str, str] = {}
        self.__json_keyfile = Path(os.path.abspath(json_keyfile))
        self.__token_file = Path(
            f"{self.__json_keyfile.parent}/"
            f"{self.__json_keyfile.stem}.{Constants.TOKEN_EXT.value}")
        self.__verify = not kwargs.get('insecure', False)
        self.__proxies = kwargs.get('proxies')
        self.__session = kwargs.get('session', 'session')
        self.__graphql = kwargs.get('graphql', 'graphql')
        print(self.__session)
        print(self.__graphql)
        exit()
        # get info from json keyfile
        self.__read_key_file()
        if not self.__read_token_file():
            self.__get_access_token_keyfile()
        # build header
        self.__build_headers()
        # delete sensitive info !
        del self.__json_key
        del self.__json_keyfile

    def __read_key_file(self) -> None:
        try:
            logger.info(Message.KEYFILE_INFO.value, self.__json_keyfile)
            self.__json_key = json.loads(self.__json_keyfile.read_text(
                Constants.ENCODING.value))
        except Exception:
            raise

        # get base url
        self.__base_url = re.sub(
            r"/[^/]*$", "", self.__json_key['access_token_uri'])
        logger.info(Message.BASE_URL.value, self.__base_url)

    def __build_headers(self) -> None:
        self.__headers['Content-Type'] = 'application/json'
        self.__headers['Accept'] = 'application/json'
        if self.__token:
            self.__headers['Authorization'] = 'Bearer ' + self.__token

    def __read_token_file(self) -> bool:
        if self.__token_file.exists():
            logger.info(Message.TOKEN_FOUND.value, self.__token_file)
            timestamp = os.path.getmtime(self.__token_file)
            token_timestamp = datetime.datetime.fromtimestamp(timestamp)
            logger.info(Message.TOKEN_TIMESTAMP.value, token_timestamp)
            if (token_timestamp < datetime.datetime.today() -
                    datetime.timedelta(hours=Constants.REFRESH_TOKEN.value)):
                logger.info(Message.TOKEN_OLD.value)
                self.__delete_token()
                return False
            logger.info(Message.TOKEN_GET.value)
            self.__token = self.__token_file.read_text(
                Constants.ENCODING.value)
            return True
        return False

    @request_exception
    def __delete_token(self) -> None:
        logger.info(Message.TOKEN_READ.value)
        # get current value
        self.__token = self.__token_file.read_text(Constants.ENCODING.value)
        # build header
        self.__build_headers()
        logger.info(Message.TOKEN_DEL.value)
        # delete session on GraphQL
        requests.delete(
            f"{self.__base_url}/{self.__session}",
            headers=self.__headers,
            verify=self.__verify,
            proxies=self.__proxies,
            timeout=Constants.TIMEOUT.value
            )
        # delete token file
        os.unlink(self.__token_file)
        # clear current token in memory
        self.__token = ""

    @request_exception
    def __get_access_token_keyfile(self) -> None:
        self.__build_headers()
        session_url = self.__json_key['access_token_uri']
        payload = {
            "client_id": self.__json_key['client_id'],
            "client_secret": self.__json_key['client_secret'],
            "name": self.__json_key['name']
        }
        response = requests.post(
            session_url,
            json=payload,
            headers=self.__headers,
            verify=self.__verify,
            proxies=self.__proxies,
            timeout=Constants.TIMEOUT.value
        )
        response_json = response.json()
        self.__token = response_json['access_token']
        logger.info(Message.TOKEN_WRITE.value)
        self.__token_file.write_text(self.__token,
                                     encoding=Constants.ENCODING.value)

    @request_exception
    def query(self, my_query: str,
              my_variables: Optional[dict[str, str]] = None,
              timeout: int = Constants.TIMEOUT.value) -> dict[str, Any]:
        """Perform raw GraphQL request.

        Return:
            Return the raw response in json format.
        """
        body: dict[str, Any] = {"query": f"{my_query}"}
        if my_variables:
            body['variables'] = my_variables

        resp = requests.post(
            f"{self.__base_url}/{self.__graphql}",
            headers=self.__headers,
            json=body,
            verify=self.__verify,
            proxies=self.__proxies,
            timeout=timeout
        )
        return resp.json()
