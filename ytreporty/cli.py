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

import argparse
from datetime import datetime
import json
import logging
import os

from . import ExitStatus
from . import api
from .context import Environment

_environment = Environment()


def parse_arguments():
    class ArgparseFormatter(
        argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter
    ):
        pass

    parser = argparse.ArgumentParser(
        description="List and manipulate YouTube Reporting API jobs.",
        epilog="""
All commands are YouTube Reporting API methods except for `fetch'. For
details on the YouTube Reporting API, see:

    https://developers.google.com/youtube/reporting/v1/reference/rest/
""".format(
            os.path.basename(__file__)
        ),
        formatter_class=ArgparseFormatter,
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="print info-level log messages"
    )
    action = parser.add_subparsers(
        dest="method", required=True, help="API method to invoke", metavar="command"
    )

    # create command
    p = action.add_parser(
        "create",
        description="Create a new reporting job.",
        help="create a new reporting job",
    )
    action_create = p.add_subparsers(
        dest="resource_type",
        required=True,
        help="type of resource to create",
        metavar="resource_type",
    )
    p = action_create.add_parser(
        "jobs", description="Create a reporting job.", help="create a reporting job"
    )
    p.add_argument("reportTypeId", help="ID of report type")
    p.add_argument("name", help="name of reporting job")

    # delete command
    p = action.add_parser(
        "delete", description="Delete a reporting job.", help="delete a reporting job"
    )
    action_delete = p.add_subparsers(
        dest="resource_type",
        required=True,
        help="type of resource to delete",
        metavar="resource_type",
    )
    p = action_delete.add_parser(
        "jobs", description="Delete a reporting job.", help="delete a reporting job"
    )
    p.add_argument("jobId", help="ID of reporting job to delete")

    # get command
    p = action.add_parser(
        "get",
        description="Retrieve information about a reporting job or a specific report.",
        help="retrieve information about a reporting job or a specific report",
    )
    action_get = p.add_subparsers(
        dest="resource_type",
        required=True,
        help="type of resource about which to retrieve",
        metavar="resource_type",
    )
    p = action_get.add_parser(
        "jobs",
        description="Retrieve information about a reporting job.",
        help="retrieve information about a reporting job",
    )
    p.add_argument("jobId", help="ID of the reporting job")
    p = action_get.add_parser(
        "jobs.reports",
        description="Retrieve information about a specific report.",
        help="retrieve information about a specific report",
    )
    p.add_argument("jobId", help="ID of the reporting job")
    p.add_argument("reportId", help="ID of the report")

    # list command
    p = action.add_parser(
        "list",
        description="List reporting jobs, reports, or report types.",
        help="list reporting jobs, reports, or report types",
    )
    action_list = p.add_subparsers(
        dest="resource_type",
        required=True,
        help="type of resource to list",
        metavar="resource_type",
    )
    p = action_list.add_parser(
        "jobs", description="List reporting jobs.", help="list reporting jobs"
    )
    p = action_list.add_parser(
        "jobs.reports",
        description="List reports from a reporting job.",
        help="list reports from a reporting job",
    )
    p.add_argument("jobId", help="ID of the reporting job")
    p.add_argument(
        "--created-after",
        type=datetime.fromisoformat,
        help="limit to reports created after specified ISO date",
    )
    p.add_argument(
        "--start-time-at-or-after",
        type=datetime.fromisoformat,
        help="limit to reports whose oldest data starts on or after the specified date",
    )
    p.add_argument(
        "--start-time-before",
        type=datetime.fromisoformat,
        help="limit to reports whose oldest data starts before the specified date",
    )
    p = action_list.add_parser(
        "reportTypes",
        description="List available report types.",
        help="list available report types",
    )

    # fetch command
    p = action.add_parser(
        "fetch", description="Fetch YouTube report.", help="fetch YouTube report"
    )
    p.add_argument("jobId", help="ID of the reporting job")
    p.add_argument("reportId", help="ID of the report")

    args = parser.parse_args()
    return args


def main(env=_environment):
    args = parse_arguments()
    if args.verbose:
        logging.getLogger().setLevel(logging.INFO)
    logging.info("arguments read: %s", args)

    assert "method" in args
    assert "resource_type" not in args or args.resource_type in [
        "jobs",
        "jobs.reports",
        "reportTypes",
    ]
    if args.method == "fetch":
        r = api.fetch_report(env, job_id=args.jobId, report_id=args.reportId)
    elif args.resource_type == "jobs":
        assert args.method in ["create", "delete", "get", "list"]
        if args.method == "create":
            r = api.jobs_create(env, report_type_id=args.reportType, job_name=args.name)
        elif args.method == "delete":
            r = api.jobs_delete(env, job_id=args.jobId)
        elif args.method == "get":
            r = api.jobs_get(env, job_id=args.jobId)
        else:  # args.method == "list":
            r = api.jobs_list(env)
    elif args.resource_type == "jobs.reports":
        assert args.method in ["get", "list"]
        if args.method == "get":
            r = api.reports_get(env, job_id=args.jobId, report_id=args.reportId)
        else:  # args.method == "list":
            r = api.reports_list(
                env,
                job_id=args.jobId,
                created_after=args.created_after,
                start_time_at_or_after=args.start_time_at_or_after,
                start_time_before=args.start_time_before,
            )
    else:  # args.resource_type == "reportTypes":
        assert args.method in ["list"]
        r = api.reporttypes_list(env)

    if isinstance(r, str):
        print(r, end="")
    elif isinstance(r, dict):
        print(json.dumps(r, indent=2, sort_keys=True))
    else:
        print(r)

    return ExitStatus.SUCCESS
