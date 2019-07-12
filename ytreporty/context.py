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

import configparser
import logging
import os

from .authorization import read_secret, read_token

APPNAME = "ytreporty"


class Environment:
    def __init__(self):
        self.secret = read_secret(self, self.config.parser["ytreporty"]["secret"])
        self.token = read_token(self)

    @property
    def config(self):
        if not hasattr(self, "_config"):
            self._config = Config()
            self._config.load()
        return self._config


class Config:
    def __init__(self, configdir=None, datadir=None):
        self.configdir = (
            configdir if configdir else self._get_default_config_directory()
        )
        self.datadir = datadir if datadir else self._get_default_data_directory()
        self.configfilepath = os.path.join(self.configdir, APPNAME + ".conf")
        self.parser = None

    def load(self):
        """Read application configuration file."""
        config = configparser.ConfigParser()
        if self.configfilepath in config.read(self.configfilepath):
            logging.info("Read config file %s", self.configfilepath)
        else:
            logging.warning("Config file %s not found", self.configfilepath)
        self.parser = config

    @staticmethod
    def _get_default_config_directory():
        """Return the default application configuration directory."""
        xdg_config_home = (
            os.environ["XDG_CONFIG_HOME"]
            if "XDG_CONFIG_HOME" in os.environ
            else os.path.join(os.getenv("HOME"), ".config")
        )
        return os.path.join(xdg_config_home, APPNAME)

    @staticmethod
    def _get_default_data_directory():
        """Return the default application data directory."""
        xdg_data_home = (
            os.environ["XDG_DATA_HOME"]
            if "XDG_DATA_HOME" in os.environ
            else os.path.join(os.getenv("HOME"), ".local", "share")
        )
        return os.path.join(xdg_data_home, APPNAME)
