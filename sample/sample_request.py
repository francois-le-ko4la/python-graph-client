#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script is a sample script to request an open access GraphQL.
"""
import sys
import json
from graphqlclient import GraphClient, ExitStatus


if __name__ == "__main__":

    try:
        client = GraphClient(base_url="https://fruits-api.netlify.app",
                             verbose=True)
        query = """query oneFruit {
          fruit(id: 5) {
            id
            scientific_name
            tree_name
            fruit_name
            family
          }
        }
        """
        print(json.dumps(client.query(my_query=query), indent=4))

    except Exception:
        sys.exit(ExitStatus.EX_KO)

    sys.exit(ExitStatus.EX_OK)
