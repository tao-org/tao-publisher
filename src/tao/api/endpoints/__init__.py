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

"""TAO API endpoints package.

Each API endpoint is a class that represents an API route and the operations
available for that endpoint. They can be with or without authentication.
Each operation corresponds to an HTTP call, which can be GET, POST, DELETE
for a relative sub-route of the endpoint etc...
"""

from .component import ComponentAPI
from .container import ContainerAPI
from .publish import PublishAPI

__all__ = ["ComponentAPI", "ContainerAPI", "PublishAPI"]
