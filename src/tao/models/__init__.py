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

"""TAO models package.

This package contains the models corresponding to the TAO API data schemas.
They handle the data validation thanks to the use of Pydantic.

The models are just a way to encapsulate the data returned by the API,
they are used by the endpoints API classes in the package `tao.api.endpoints`.

Warning:
    Any "breaking change" in the TAO API could lead to malfunctions.
"""

from .component import Component, ComponentDescriptor
from .container import Container
from .publish import PublishSpec

__all__ = ["Component", "ComponentDescriptor", "Container", "PublishSpec"]
