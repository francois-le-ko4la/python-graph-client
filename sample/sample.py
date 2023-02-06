#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
import json
from graphqlclient import GraphClient, ExitStatus, valid_python, enable_logging


def get_argparser() -> argparse.ArgumentParser:
    """Define the argument parser and return it.

    Returns:
        ArgumentParser

    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-k', '--keyfile',
        dest='json_keyfile', help="JSON Keyfile", default=None, required=True)
    parser.add_argument(
        '--insecure',
        help='Deactivate SSL Verification', action="store_true")
    parser.add_argument(
        '--verbose',
        help='Logging on', default=False, action="store_true")
    return parser


if __name__ == "__main__":
    # manage args
    args = get_argparser().parse_args()

    if args.verbose:
        enable_logging()

    if not valid_python():
        sys.exit(ExitStatus.EX_CONFIG)

    try:
        my_obj: GraphClient = GraphClient(
            json_keyfile=args.json_keyfile,
            insecure=args.insecure,
            verbose=args.verbose,
            session="mysession",
            graphql="mygraphql",
            manage_token=False)

        query = """query XXXX
        XXXXX
        """

        print(json.dumps(my_obj.query(my_query=query), indent=4))

    except Exception:
        sys.exit(ExitStatus.EX_KO)

    sys.exit(ExitStatus.EX_OK)
