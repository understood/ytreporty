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

from unittest import TestCase
from unittest.mock import mock_open, patch

import requests

from ytreporty.api import jobs_list
from ytreporty.context import Environment


class Response:
    def __init__(self):
        self.status_code = 200
        self.headers = {"Content-Type": "application/json"}

    def json(self):
        return dict()


class JobApiTestCase(TestCase):
    @patch("requests.get", return_value=Response())
    @patch(
        "builtins.open",
        side_effect=(
            mock_open(read_data='{"installed": {}}').return_value,
            mock_open(read_data='{"access_token": ""}').return_value,
        ),
    )
    @patch("configparser.ConfigParser", autospec=True)
    def test_jobs_list(self, mock_configparser, mock_open, mock_requests_get):
        """Test jobs_list() method."""
        conf = {"ytreporty": {"secret": "secret.json"}}
        mock_configparser.return_value.__getitem__.side_effect = conf.__getitem__
        mock_configparser.return_value.__iter__.side_effect = conf.__iter__
        mock_configparser.return_value.__len__.side_effect = conf.__len__
        mock_configparser.return_value.__contains__.side_effect = conf.__contains__

        env = Environment()
        jobs_list(env)
        requests.get.assert_called()
