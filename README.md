<p align="center">
  <img src="https://forthebadge.com/images/badges/made-with-python.svg" height="30" />
  <img src="https://img.shields.io/badge/Work_on-Linux_MACOS_Windows-0071C5?style=for-the-badge&logoColor=white" height="30" />
  <br />
  <img src="https://img.shields.io/github/v/release/francois-le-ko4la/python-graph-client?display_name=tag" />
  <img src="https://img.shields.io/badge/python-3.7%2B-blue" />
  <img src="https://img.shields.io/badge/PYCODESTYLE-PASSING-green" />
  <img src="https://img.shields.io/badge/PYLINT-PASSING-green" />
  <img src="https://img.shields.io/badge/MYPY-PASSING-green" />
  <img src="https://img.shields.io/github/license/francois-le-ko4la/python-graph-client" />
</p>

# Python-Graph-Client:
## Why?:

Developing a Python package to connect to a GraphQL API has several benefits:

- Ease of use: Python is a popular language with a large developer community
  and many libraries that make it easy to work with GraphQL APIs.

- Flexibility: GraphQL allows you to retrieve only the data you need, and
  Python makes it easy to manipulate that data in your application.

- Scalability: Python is known for its scalability and can handle large amounts
  of data efficiently, making it a good choice for building applications that
  need to handle large amounts of data from GraphQL APIs.

- Integration: Python has a large number of libraries and tools for integrating
  with other systems and technologies, making it a good choice for building
  applications that need to integrate with GraphQL APIs.

- Visibility: This package can provide all info from request/http client 
  with the verbose mode. This is a feature used to check the communication 
  with the API target.

Overall, developing a Python package to connect to a GraphQL API can simplify
the process of retrieving and manipulating data from the API, and make it
easier to build powerful and scalable applications.

With this package, you have control over the URL that the script connects to,
the URL to get/delete token that is used, and the queries that are executed 
against the API.

This package is a GENERIC package therefore we don't use GraphQL map.
Use this package if you know what you are doing and according to your API
documentation.

This Software is provided 'AS IS' without warranty of any kind, including
without limitation, any implied warranties of fitness for a particular purpose
or result.

# Usage
## Open Access
- integrate the library:
```python
from graphqlclient import GraphClient, ExitStatus
```

- Open access GraphQL:
```python
client = GraphClient(base_url="https://fruits-api.netlify.app",
                     verbose=True)
```

Note:
  - `base_url`: we don't use a JSON Keyfile to define the base url, therefore we 
    push the base_url value.
  - `graphql`: optional argument to define the endpoint to do your query.
    By default, graphql = "graphql" and url = "https://XXXXXXX/api/graphql"
    Here, the GraphQL url is https://fruits-api.netlify.app/graphql
  - `verbose`: True/False to enable/disable the verbose mode


## Authentication (client_id, client_secret)
- Create/generate a Key JSON keyfile:

`keyfile.json`
```python
{
	"client_id": "XXXXXXXXXX",
	"client_secret": "XXXXXXXXXX",
	"name": "XXXXXXXXXX",
	"access_token_uri": "https://XXXXXXX/api/XXX"
}
```
Note: access_token_uri is the URL to generate the token.

- integrate the library:
```python
from graphqlclient import GraphClient, ExitStatus
```

- Connect to the API:
```python
my_obj = GraphClient(
    json_keyfile=args.json_keyfile,  # json keyfile (credentials)
    insecure=args.insecure,          # True/False: If False check SSL certificat
    verbose=args.verbose,            # True/False: If True, show Request debug messages
    session="mysession",             # session url: https://XXXXXXX/api/<session>
    graphql="mygraphql",             # GraphQL url: https://XXXXXXX/api/<graphql>
    manage_token=False,              # True/False: If False, disable automatic token management
    keep_token=False)                # True/False: If False, disable token file creation
```
- Note:
  - `base url`: made with your json file -> "https://XXXXXXX/api"
  - `session`: optional argument to define the endpoint to delete your Token. 
    By default, session = "session" and url = "https://XXXXXXX/api/session"
  - `graphql`: optional argument to define the endpoint to do your query.
    By default, graphql = "graphql" and url = "https://XXXXXXX/api/graphql"
  - `verbose`: True/False to enable/disable the verbose mode
  - `insecure`: True/False to verify SSL certificate
  - `manage_token`: True by default if we define a json keyfile.
    If manage_token is False, then it disable token management and the token
    lifecycle will be manage by another process according to your GraphQL API
    (documentation is your best friend). This option is confirmed in the log:
```shell
2023-02-07T09:39:25+0100 - GraphClient - INFO - Token: ** KEEP THE CURRENT ACCESS TOKEN BY OPT. **
```
  - `keep_token`: True by default if we define a json keyfile.
    If keep_token is False, then the token is not write in the token file.
    We must use my_obj.close_session() to terminate the GraphQL session.
    If the script is regurarly launch (hourly) and token still valid between 2 calls then
    you can store the token to reuse it and let the automatic token refresh each hour.
    If the script is used 1 time per month, then dont store the token and close the session.


# Token
## Description

By default, we generate a token file to avoid multiple token generation
and use the same session for multiple script call.
The token is store on the same folder than keyfile, and we keep it for 1h by 
default.

New (0.1.7) : by default, if the token stored is invalid and manage_token=True
it will refresh and recreate a new token file. 

To cover multiple use cases we provide other mechanism:
- token renew
- disable the token file

## Token renew
By default, token is renew by default automatically
We can force the token renew in the script using renew_token() function.
Use case: multiple scripts use the same token stored on disk, and you want
a simple script to renew the token.
All scripts will use the option "manage_token=False" during GraphClient
instantiation and one script will be called to force the token renew:

`refresh_token.py`
```python
if __name__ == "__main__":
    # manage args
    args = get_argparser().parse_args()

    try:
        my_obj = GraphClient(
            json_keyfile=args.json_keyfile,  # json keyfile (credentials)
            insecure=args.insecure,          # True/False: If True, check SSL certificat
            verbose=args.verbose,            # True/False: If True, show Request debug messages
            manage_token=False)              # True/False: If False, disable automatic token management

        my_obj.renew_token()                 # Force token refresh

    except Exception:
        sys.exit(ExitStatus.EX_KO)

    sys.exit(ExitStatus.EX_OK)
```

## Disable the token file (0.1.7)

We can disable the token file to cover these use cases:
- We launch a script with a frequency (1 per month) incompatible with the lifespan of a GraphQL token.
- We prefer to close the session after the last query in the script

`script.py`
```python
if __name__ == "__main__":
    # manage args
    args = get_argparser().parse_args()

    try:
        my_obj = GraphClient(
            json_keyfile=args.json_keyfile,  # json keyfile (credentials)
            insecure=args.insecure,          # True/False: If True, check SSL certificat
            verbose=args.verbose,            # True/False: If True, show Request debug messages
            keep_token=False)                # True/False: If False, disable token file creation

        query = """
        ...
        """

        my_obj.close_session()               # Close the GraphQL Session

    except Exception:
        sys.exit(ExitStatus.EX_KO)

    sys.exit(ExitStatus.EX_OK)
```

Note:
By default, we close the current GraphQL session before the automatic renew.
When we disable the token file the session MUST be closed with the
close_session() function.

# Query

```python
# start a session
client = GraphClient(base_url="https://fruits-api.netlify.app",
                     verbose=True)
# build the query
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
# send the query / get the response
response = client.query(my_query=query)
```

Below, we provide the full function definition to use it correctly:
```python
@request_exception
def query(self, my_query: str,
          my_variables: Optional[dict[str, Any]] = None,
          timeout: int = Constants.TIMEOUT.value) -> dict[str, Any]:
    """Perform raw GraphQL request.
    
    Args:
        my_query(str): query
        my_variables(dict[str, Any]): variables to use during the query
        timeout(int): timeout (default: Constants.TIMEOUT.value)
    
    Return:
        dict[str, Any]: the response in json format.
    """
```

# Sample and error management
We raise errors from request library. We should use a try/except to catch our exception in the main script.
We provide a sample folder with all info.

# Setup:
## Compatibility
Python 3.7+

## Install
- Download the package:
  ```shell
  git clone https://github.com/francois-le-ko4la/python-graph-client.git
  ```

- Change to the folder:
  ```shell
  cd python-graph-client
  ```

- Install :
  ```shell
  make install
  ```

# Version history

- 0.1.0: first release.
- 0.1.1: add manage_token option.
- 0.1.2: remove unnecessary unlink (token lifecycle), improve logging 
  message, attributes optimization with NamedTuple.
- 0.1.3: improve the doc and fix typing issue (variables).
- 0.1.4: add a function (renew_token) to create a new token (force mode).
- 0.1.5: improve logging, simplify the code, clean constants.
- 0.1.6: add anonymous connection, add raise_for_status() to raise a message 
  if the query status >= 400.
- 0.1.7: add keep_token option, better automatic token creation

# License

This package is distributed under the [GPLv3 license](./LICENSE)
