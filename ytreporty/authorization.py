# -*- coding: utf-8; mode: Python; -*-
#
# Licensed under the Apache License, Version 2.0 (the "License"); you
# may not use this file except in compliance with the License. You may
# obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied. See the License for the specific language governing
# permissions and limitations under the License.

import json
import logging
import os

import requests


def read_secret(env, filename):
    """Read the secret given by filename."""
    filepath = os.path.join(env.config.configdir, filename)
    with open(filepath) as f:
        data = json.load(f)
    secret = data["installed"]
    return secret


def read_token(env, filename="token.json"):
    """Read the OAuth2 token file."""
    filepath = os.path.join(env.config.datadir, filename)
    with open(filepath) as f:
        token = json.load(f)
    return token


def write_token(env, filename="token.json"):
    """Write token to disk."""
    filepath = os.path.join(env.config.datadir, filename)
    with open(filepath, "w") as f:
        json.dump(env.token, f)


def refresh_token(token, secret):
    """Refresh YouTube access token."""
    GRANT_TYPE = "refresh_token"

    logging.info("Refreshing access token...")
    url = "https://www.googleapis.com/oauth2/v4/token"
    data = {
        "refresh_token": token["refresh_token"],
        "client_id": secret["client_id"],
        "client_secret": secret["client_secret"],
        "grant_type": GRANT_TYPE,
    }
    r = requests.post(url, data=data)
    if r.status_code != requests.codes.ok:
        r.raise_for_status()
    newtoken = r.json()
    logging.info("New token expires in %d seconds", newtoken["expires_in"])
    return newtoken


def add_token_to_headers(token, headers=None):
    """Add bearer token to header dict."""
    if headers is None:
        headers = {}
    return {**headers, **{"Authorization": "Bearer " + token["access_token"]}}
