import json
import concurrent.futures
import threading
import time
import requests
import math
import os
import pandas as pd
import numpy as np

SESSION_THREAD_LOCAL = threading.local()

SERVER = "prod"
# if 'UPLOAD_SERVER' in os.environ:
#     print("Env: {}".format(os.environ['UPLOAD_SERVER']))
#     SERVER = os.environ['UPLOAD_SERVER']


class InvalidResponseError(Exception):
    """Base class for exceptions in this module."""
    pass


def upload_blocks(data, query):
    initialized = getattr(SESSION_THREAD_LOCAL, 's', None)
    if initialized is None:
        SESSION_THREAD_LOCAL.s = requests.Session()
    start = time.time()
    domain = "sf"
    staging_url = "https://statecraft-api-staging.herokuapp.com/api"
    production_url = "https://api.statecrafthq.com/api"
    local_url = "http://localhost:9000/api"
    local_docker_url = "http://docker.for.mac.localhost:9000/api"

    if SERVER == "prod":
        url = production_url
    elif SERVER == "staging":
        url = staging_url
        domain = "sfhousing"
    elif SERVER == "docker":
        url = local_docker_url
    else:
        url = local_url

    headers = {
        'x-statecraft-domain': domain,
        'Content-Type': 'application/json'
    }
    container = {
        "query": query,
        "variables": {
            "data": data,
        }
    }
    data = json.dumps(container)
    response = SESSION_THREAD_LOCAL.s.post(
        url, data=data, headers=headers, stream=False)
    try:
        rdata = json.loads(response.text)
        if 'errors' in rdata:
            raise InvalidResponseError("Wrong response!")
    except BaseException as e:
        print("Wrong Response!")
        print("Sent:")
        print(data)
        print("Got:")
        print(response.text)
        raise e

    #    print(r.text)
    end = time.time()
    print("Uploaded in {} sec".format(end-start))


def importData(fileName, query):
    pending = []
    with open(fileName, "r") as lines:
        for line in lines:
            s = json.loads(line.rstrip('\n'))
            pending.append(s)
            if len(pending) > 50:
                while True:
                    try:
                        upload_blocks(pending, query)
                        break
                    except:
                        pass
                pending = []
    if len(pending) > 0:
        upload_blocks(pending, query)


# importData('Blocks.jsvc', "mutation($data: [BlockInput!]!) { importBlocks(state: \"CA\", county: \"San Francisco\", city: \"San Francisco\", blocks: $data) }")
importData('Lots.jsvc', "mutation($data: [ParcelInput!]!) { importParcels(state: \"CA\", county: \"San Francisco\", city: \"San Francisco\", parcels: $data) }")
