# Copyright 2024, CS GROUP - France, https://www.csgroup.eu/
#
# This file is part of TAO Publisher project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""TAO Publisher top-level package.

This python package delivers a CLI and a python API to interact with the TAO API.

Available features:

- List, get, and delete of **Toolbox Containers**.
- List, get, and delete of **Processing Components**.
- Definition of Toolbox Containers and Processing Components with a declarative file,
  and a publish mechanism to register them inside TAO.
"""

from importlib.metadata import PackageNotFoundError, version

from tao.api import APIClient, PublishAPI
from tao.config import Config

try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pragma: no cover
    # package is not installed
    __version__ = "undefined"


__all__ = ["Config", "APIClient", "PublishAPI"]
