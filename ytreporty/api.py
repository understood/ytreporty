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

from datetime import timezone
from json import JSONDecodeError
import logging
from urllib.parse import urljoin

import requests

from .authorization import add_token_to_headers, refresh_token, write_token

BASE_URL = "https://youtubereporting.googleapis.com"


def zuluformat(x):
    """Return Zulu format string representation of datetime object."""
    x = (
        x.replace(tzinfo=timezone.utc)
        if x.utcoffset() is None
        else x.astimezone(tz=timezone.utc)
    )
    return x.isoformat().replace("+00:00", "Z")


def _request_youtube(method, url, env, params=None, headers=None, json=None):
    """Perform a YouTube Reporting API request.

    This function refreshes the access token if necessary.

    """
    request_fn = {"DELETE": requests.delete, "GET": requests.get, "POST": requests.post}
    assert method in request_fn

    urlabs = urljoin(BASE_URL, url)
    headers = add_token_to_headers(env.token, headers)
    r = request_fn[method](urlabs, params=params, headers=headers, json=json)

    if (
        r.status_code != requests.codes.ok
        and r.json()["error"]["status"] == "UNAUTHENTICATED"
    ):
        logging.info("Request was not authenticated")

        # Refresh access token and repeat request.
        newtoken = refresh_token(env.token, env.secret)
        env.token.update(newtoken)
        write_token(env)
        headers = add_token_to_headers(env.token, headers)
        r = request_fn[method](urlabs, headers=headers)

    logging.info("Received status code %d", r.status_code)
    if r.status_code != requests.codes.ok:
        r.raise_for_status()

    return r


def request_youtube(method, url, env, params=None, headers=None, json=None):
    r = _request_youtube(method, url, env, params=params, headers=headers, json=json)
    logging.info(
        "Received request "
        + (
            "with content type `{}'.".format(r.headers["Content-Type"])
            if "Content-Type" in r.headers
            else "without Content-Type header."
        )
    )
    try:
        o = r.json()
    except JSONDecodeError:
        return r.text
    if "nextPageToken" not in o:
        return o

    L = [o]
    next_page_tokens = set()
    while "nextPageToken" in o and o["nextPageToken"] not in next_page_tokens:
        next_page_tokens.add(o["nextPageToken"])
        logging.info("Fetching next page using token %s", o["nextPageToken"])
        headers = {
            **(headers if headers is not None else {}),
            **{"pageToken": o["nextPageToken"]},
        }
        r = _request_youtube(
            method, url, env, params=params, headers=headers, json=json
        )
        try:
            o = r.json()
        except JSONDecodeError:
            raise ValueError("Response content not JSON decodable")
        L.append(o)
    keys = set(k for d in L for k in d.keys() if k != "nextPageToken")
    o = {k: [v for d in L if k in d for v in d[k]] for k in keys}
    return o


def jobs_create(env, report_type_id, job_name):
    """Create a reporting job."""
    url = "/v1/jobs"
    job = {"reportTypeId": report_type_id, "name": job_name}
    r = request_youtube("POST", url, env, json=job)
    return r


def jobs_delete(env, job_id):
    """Delete a reporting job."""
    url = "/v1/jobs/{jobId}".format(jobId=job_id)
    r = request_youtube("DELETE", url, env)
    return r


def jobs_get(env, job_id):
    """Get a reporting job."""
    url = "/v1/jobs/{jobId}".format(jobId=job_id)
    r = request_youtube("GET", url, env)
    return r


def jobs_list(env):
    """List reporting jobs."""
    url = "/v1/jobs"
    r = request_youtube("GET", url, env)
    return r


def reports_get(env, job_id, report_id):
    """Retrieve metadata about a report."""
    url = "/v1/jobs/{jobId}/reports/{reportId}".format(jobId=job_id, reportId=report_id)
    r = request_youtube("GET", url, env)
    return r


def reports_list(
    env, job_id, created_after=None, start_time_at_or_after=None, start_time_before=None
):
    """List reports from a reporting job."""
    url = "/v1/jobs/{jobId}/reports".format(jobId=job_id)
    params = {}
    if created_after is not None:
        params["createdAfter"] = zuluformat(created_after)
    if start_time_at_or_after is not None:
        params["startTimeAtOrAfter"] = zuluformat(start_time_at_or_after)
    if start_time_before is not None:
        params["startTimeBefore"] = zuluformat(start_time_before)
    r = request_youtube("GET", url, env, params=params)
    return r


def reporttypes_list(env):
    """List report types that can be retrieved."""
    url = "/v1/reportTypes"
    r = request_youtube("GET", url, env)
    return r


def fetch_report(env, job_id, report_id):
    """Return report with given job ID and report ID."""
    r_reportinfo = reports_get(env, job_id, report_id)
    url = r_reportinfo["downloadUrl"]
    r = request_youtube("GET", url, env)
    return r
