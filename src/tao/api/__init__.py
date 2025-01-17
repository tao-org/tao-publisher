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

"""TAO API package.

This package contains the API client as well as API endpoints.
You could say that everything in this package is the pure interface to the TAO API.

Warning:
    Any "breaking change" in the TAO API could lead to malfunctions.
"""

from .client import APIClient
from .endpoints import ComponentAPI, ContainerAPI, PublishAPI

__all__ = ["APIClient", "ComponentAPI", "ContainerAPI", "PublishAPI"]
