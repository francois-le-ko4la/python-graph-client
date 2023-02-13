#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Python GraphQL Client.

Why?:

    Developing a Python package to connect to a GraphQL API has several
    benefits:
    - Ease of use: Python is a popular language with a large developer
      community and many libraries that make it easy to work with GraphQL APIs.

    - Flexibility: GraphQL allows you to retrieve only the data you need, and
      Python makes it easy to manipulate that data in your application.

    - Scalability: Python is known for its scalability and can handle large
      amounts of data efficiently, making it a good choice for building
      applications that need to handle large amounts of data from GraphQL APIs.

    - Integration: Python has a large number of libraries and tools for
      integrating with other systems and technologies, making it a good choice
      for building applications that need to integrate with GraphQL APIs.

    - Visibility: This package can provide all info from request/http client
      with the --verbose mode. This is a feature used to check the
      communication with the API target.

    Overall, developing a Python package to connect to a GraphQL API can
    simplify the process of retrieving and manipulating data from the API,
    and make it easier to build powerful and scalable applications.

    With this package, you have control over the URL that the script connects
    to, the URL to get/delete token that is used, and the queries that are
    executed against the API.

    This package is a GENERIC package therefore we don't use GraphQL map.
    Use this package if you know what you are doing and according to your API
    documentation.

    This Software is provided 'AS IS' without warranty of any kind, including
    without limitation, any implied warranties of fitness for a particular
    purpose or result.

Usage:
    README.md

Setup:
    - Download the package:
      ```shell
      $ git clone https://github.com/francois-le-ko4la/python-graph-client.git
      ```

    - Change to the folder:
      ```shell
      $ cd python-graph-client
      ```

    - Install :
      ```shell
      $ make install
      ```

"""
from graphqlclient.__about__ import (__author__, __description__, __license__,
                                     __pkg_name__, __url__, __version__)
from graphqlclient.client import ExitStatus, GraphClient
