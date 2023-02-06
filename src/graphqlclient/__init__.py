#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Python GraphQL Client."""
import sys

from .client import ExitStatus, GraphClient, enable_logging, valid_python

if sys.version_info >= (3, 8):
    from importlib import metadata
else:
    import importlib_metadata as metadata  # type: ignore

__pkg_name__: str = "graphqlclient"
__version__: str = metadata.version(__pkg_name__)
__author__: str = metadata.metadata(__pkg_name__)["Author"]
__url__: str = metadata.metadata(__pkg_name__)["Project-URL"]
__license__: str = metadata.metadata(__pkg_name__)["License"]
__description__: str = metadata.metadata(__pkg_name__)["Summary"]
