#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script is a sample script to request an open access GraphQL.
"""
import sys
from graphqlclient import GraphClient, ExitStatus


if __name__ == "__main__":

    try:
        client = GraphClient(
            base_url="https://fruits-ai.netlify.app",
            verbose=True)
        my_query = """query oneFruit {
          fruit(id: 5) {
            id
            scientific_name
            tree_name
            fruit_name
            family
          }
        }
        """
        print(client.query(my_query=my_query))
    except Exception:
        sys.exit(ExitStatus.EX_KO)

    sys.exit(ExitStatus.EX_OK)
