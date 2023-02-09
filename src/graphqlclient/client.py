#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=too-few-public-methods
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
from http.client import HTTPConnection
from pathlib import Path
from typing import Any, Callable, NamedTuple, Optional, TypeVar, cast

import requests

from graphqlclient.__about__ import __version__

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
    TOKEN_LIFESPAN: int = 1     # 1: 1 Hour
    ENCODING: str = "UTF-8"
    LOGGING_FMT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOGGING_DATE_FMT: str = "%Y-%m-%dT%H:%M:%S%z"


@unique
class Message(Enum):
    """Define messages."""

    PYT_INF: str = "Python version is supported: %s"
    PYT_ERR: str = "Python version is not supported: %s"
    PYT_DEB: str = "Python environment: %s"
    LOG_FUNC: str = "%s(): %s"
    KEYFILE_INFO: str = "Key file: %s"
    TOKEN_FOUND: str = "Token file: %s"
    TOKEN_GET: str = "Token: Use the current access token."
    TOKEN_DEL: str = "Token: Close your session and delete the token file."
    TOKEN_TIMESTAMP: str = "Current access token timestamp: %s"
    TOKEN_WRITE: str = "Token: Write the new access token."
    TOKEN_RENEW: str = "Token: ** GET A NEW ACCESS TOKEN - REQUESTED. **"
    TOKEN_KEEP_OPT: str = "Token: ** KEEP THE CURRENT ACCESS TOKEN BY OPT. **"
    TOKEN_KEEP: str = "Token: Keep the current access token."
    TOKEN_OLD: str = "Token: Refresh the access token is required."
    BASE_URL: str = "Base url: %s"
    VERBOSE_MODE: str = "Enable verbose mode."
    VERSION: str = "graphqlclient version: %s"


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
    logger.debug(Message.PYT_DEB.value, sys.version)
    return True


def http_patch_log(*args: Any) -> None:
    """Patch the http.client.print function to generate log."""
    logger.debug(" ".join(args))


def enable_logging() -> None:
    """Enable login to analyze the requests."""
    # verbose traceback - type ignore for mypy
    sys.tracebacklimit = None  # type: ignore
    # enable debug
    HTTPConnection.debuglevel = 1
    # patch http.client.print - type ignore for mypy
    http.client.print = http_patch_log  # type: ignore
    # simple logging setup
    logging.basicConfig(
        level=logging.DEBUG,
        format=Constants.LOGGING_FMT.value,
        datefmt=Constants.LOGGING_DATE_FMT.value)
    logger.info(Message.VERBOSE_MODE.value)
    logger.debug(Message.VERSION.value, __version__)


def check_exception(func: F) -> F:
    """Wrap the passed in function and logs exceptions.

    We have 3 function with request therefore we want an homogeneous exception
    management with this decorator.
    """

    @wraps(func)
    def func_wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            # track func name and run it
            info = "" if func.__doc__ is None else func.__doc__.split("\n")[0]
            logger.debug(Message.LOG_FUNC.value, func.__name__, info)
            return func(*args, **kwargs)
        # track all exceptions and finish with a generic "Exception"
        except (requests.exceptions.HTTPError,
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
                requests.exceptions.RequestException, Exception) as err:
            msg = f"{func.__name__}(): {type(err).__name__} - raised: {err}"
            logger.error(msg)
            raise
    return cast(F, func_wrapper)


class Files(NamedTuple):
    """Describe files used with a NamedTuple.

    Note: @classmethod is used to init the objects correctly with the key_file.
    """

    key: Path
    token: Path

    @classmethod
    def set_key_file(cls, path: str) -> Files:
        """Define files with key file.

        This function create the File object with the file's path,

        Args:
            path: The file's path.
        Returns:
            File

        """
        key_file = Path(os.path.abspath(path))
        token_file = Path(
            f"{key_file.parent}/{key_file.stem}.{Constants.TOKEN_EXT.value}")
        return cls(key=key_file, token=token_file)


class Options(NamedTuple):
    """Manage optional arguments."""

    verify: bool
    proxies: Optional[dict[str, str]]
    session: str
    graphql: str
    manage_token: bool


class GraphClient:
    """Define the GraphQL Client.

    Args:
        json_keyfile (str): /path/to/the/keyfile
        proxies (str): proxies
        session (str): url to delete a session
        manage_token (bool): True to manage the token lifecyle (default)
                             otherwise False.

    """

    __base_url: str = ""
    __json_key: dict[str, str] = {}
    __token: str = ""
    __files: Files
    __options: Options

    def __init__(self, json_keyfile: str, **kwargs: Any) -> None:
        """Initialize the Class."""
        self.__files = Files.set_key_file(json_keyfile)
        self.__options = Options(
            verify=not kwargs.get('insecure', False),
            proxies=kwargs.get('proxies'),
            session=kwargs.get('session', 'session'),
            graphql=kwargs.get('graphql', 'graphql'),
            manage_token=kwargs.get('manage_token', True))
        self.__manage_session()

    @check_exception
    def __read_key_file(self) -> None:
        """Read Key File and update attributes."""
        # log the filename used
        logger.info(Message.KEYFILE_INFO.value, self.__files.key)
        # read the json key file
        self.__json_key = json.loads(self.__files.key.read_text(
            Constants.ENCODING.value))
        # get base url
        self.__base_url = re.sub(
            r"/[^/]*$", "", self.__json_key['access_token_uri'])
        # log the base url
        logger.info(Message.BASE_URL.value, self.__base_url)

    @check_exception
    def __get_headers(self) -> dict[str, str]:
        """Get the current header."""
        return {'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f"Bearer {self.__token}"} if self.__token \
            else {'Content-Type': 'application/json',
                  'Accept': 'application/json'}

    @check_exception
    def __read_token_file(self) -> bool:
        """Read the current token file and manage the token lifespan."""
        if not self.__files.token.exists():
            return False
        # log the token filename and read it.
        logger.info(Message.TOKEN_FOUND.value, self.__files.token)
        self.__token = self.__files.token.read_text(Constants.ENCODING.value)
        # get the timestamp
        timestamp = os.path.getmtime(self.__files.token)
        token_timestamp = datetime.datetime.fromtimestamp(timestamp)
        logger.info(Message.TOKEN_TIMESTAMP.value, token_timestamp)
        # if the token lifecycle is managed by this instance and the token
        # is too old then delete it and return False
        if (self.__options.manage_token
                and token_timestamp < datetime.datetime.today() -
                datetime.timedelta(hours=Constants.TOKEN_LIFESPAN.value)):
            logger.info(Message.TOKEN_OLD.value)
            self.__delete_token()
            return False
        if self.__options.manage_token:
            # keep the token according to the timestamp:
            logger.info(Message.TOKEN_KEEP.value)
        else:
            # keep the token - manage_token=False
            logger.info(Message.TOKEN_KEEP_OPT.value)
        return True

    @check_exception
    def __delete_token(self) -> None:
        """Close the current GraphQL session."""
        requests.delete(
            f"{self.__base_url}/{self.__options.session}",
            headers=self.__get_headers(),
            verify=self.__options.verify,
            proxies=self.__options.proxies,
            timeout=Constants.TIMEOUT.value)
        # clear current token in memory
        self.__token = ""

    @check_exception
    def __get_access_token_keyfile(self) -> None:
        """Generate an access token using key file."""
        session_url = self.__json_key['access_token_uri']
        payload = {
            "client_id": self.__json_key['client_id'],
            "client_secret": self.__json_key['client_secret'],
            "name": self.__json_key['name']}

        response = requests.post(
            session_url,
            json=payload,
            headers=self.__get_headers(),
            verify=self.__options.verify,
            proxies=self.__options.proxies,
            timeout=Constants.TIMEOUT.value)

        response_json = response.json()
        self.__token = response_json['access_token']
        logger.info(Message.TOKEN_WRITE.value)
        self.__files.token.write_text(self.__token,
                                      encoding=Constants.ENCODING.value)

    @check_exception
    def __manage_session(self) -> None:
        """Manage the GraphQL session."""
        # get info from the json keyfile
        self.__read_key_file()
        if not self.__read_token_file():
            self.__get_access_token_keyfile()
        # delete sensitive info !
        self.__json_key = {}

    @check_exception
    def renew_token(self) -> None:
        """Renew the access token with the keyfile (force mode).

        This function force token generation.

        Returns:
            None
        """
        logger.info(Message.TOKEN_RENEW.value)
        self.__read_key_file()
        self.__delete_token()
        self.__get_access_token_keyfile()
        # delete sensitive info !
        self.__json_key = {}

    @check_exception
    def query(self, my_query: str,
              my_variables: Optional[dict[str, Any]] = None,
              timeout: int = Constants.TIMEOUT.value) -> dict[str, Any]:
        """Perform a GraphQL request.

        Args:
            my_query(str): query
            my_variables(dict[str, Any]): variables to use during the query
            timeout(int): timeout (default: Constants.TIMEOUT.value)

        Return:
            dict[str, Any]: the response in json format.
        """
        body: dict[str, Any] = {"query": f"{my_query}"}
        if my_variables:
            body['variables'] = my_variables

        resp = requests.post(
            f"{self.__base_url}/{self.__options.graphql}",
            headers=self.__get_headers(),
            json=body,
            verify=self.__options.verify,
            proxies=self.__options.proxies,
            timeout=timeout)

        return resp.json()
