# Python-Graph-Client:
[![badge](https://forthebadge.com/images/badges/made-with-python.svg)]()
![](./doc/pycodestyle-passing.svg)
![](./doc/pylint-passing.svg)
![](./doc/mypy-passing.svg)

## Why?:

Developing a Python script to connect to a GraphQL API has several benefits:

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
  with the --verbose mode. This is a feature used to check the communication 
  with the API target.

Overall, developing a Python script to connect to a GraphQL API can simplify
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

- Create/generate a Key JSON keyfile:
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
from graphqlclient import GraphClient, ExitStatus, valid_python, enable_logging
```

- Connect to the API:
```python
    my_obj = GraphClient(
        json_keyfile=args.json_keyfile,
        insecure=args.insecure,
        verbose=args.verbose,
        session="mysession",
        graphql="mygraphql",
        manage_token=False)
```
- Note:
  - base url is made with your json file : "https://XXXXXXX/api"
  - session: optional argument to define the endpoint to delete your Token. 
    By default, session = "session" and url = "https://XXXXXXX/api/session"
  - graphql: optional argument to define the endpoint to do your query.
    By default, graphql = "graphql" and url = "https://XXXXXXX/api/graphql"
  - manage_token: True by default, this optional argument disable token 
    management the token lifecycle will be manage by another process 
    according to your GraphQL API (documentation is your best friend). This 
    option is confirmed in the log:
```
2023-02-07T09:39:25+0100 - GraphClient - INFO - Token: ** KEEP THE CURRENT ACCESS TOKEN BY OPT. **
```

- Important note:

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

You can force the token renew in your script using renew_token function.
Use case: multiple scripts use the same token and you want a simple script 
to renew the token.
All scripts will use the option "manage_token=False" during GraphClient
instantiation and one script will be called to force the token renew:
```python
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
	    manage_token=False)

        my_obj.renew_token()

    except Exception:
        sys.exit(ExitStatus.EX_KO)

    sys.exit(ExitStatus.EX_OK)
```

We provide a [sample script](./sample/sample.py) with all info.

# Token
The token is store on the same folder than keyfile and we keep it for 1h by 
default.

# Setup:
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

# License

This package is distributed under the [GPLv3 license](./LICENSE)
