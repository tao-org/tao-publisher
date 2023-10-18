# TAO Publisher

[![Language](https://img.shields.io/badge/language-Python-3776ab?style=flat-square&logo=Python)](https://www.python.org/)
[![Documentation](https://img.shields.io/badge/documentation-mkdocs-0a507a?style=flat-square)](https://www.mkdocs.org/)
[![Style](https://img.shields.io/badge/style-black-9a9a9a?style=flat-square)](https://black.readthedocs.io/en/stable/)
[![Lint](https://img.shields.io/badge/lint-ruff,%20mypy-brightgreen?style=flat-square)](.)
[![Security](https://img.shields.io/badge/security-bandit,%20safety-purple?style=flat-square)](.)
[![Stability](https://img.shields.io/badge/stability-experimental-orange?style=flat-square)](.)

[Merge Request](https://gitlab.si.c-s.fr/space_platforms/dunia/tao-publisher/merge_requests) **·**
[Bug Report](https://gitlab.si.c-s.fr/space_platforms/dunia/tao-publisher/issues/new?issuable_template=bug_report) **·**
[Feature Request](https://gitlab.si.c-s.fr/space_platforms/dunia/tao-publisher/issues/new?issuable_template=feature_request)

-----

The TAO Publisher is a tool developed to provide an easy publishing interface with [TAO](https://hub.eoafrica-dunia.org/ui/sap.html) through a Python API / CLI.

## Table of Contents

- [Getting started](#getting-started)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Configuration](#configuration)
    - [Publishing](#publishing)

## Getting started

### Installation
<!-- --8<-- [start:install] -->

This project can be installed from its source code.

```bash
pip install git+https://gitlab.si.c-s.fr/space_platforms/dunia/tao-publisher
```

You can use `git+https://gitlab.si.c-s.fr/space_platforms/dunia/tao-publisher@<tag>`
to install a specific version.

You can also clone the repo and install from it locally:

```bash
git clone https://gitlab.si.c-s.fr/space_platforms/dunia/tao-publisher
cd tao-publisher
pip install .
```

!!! note "Virtualenvs"
    The use of a virtual environment is greatly recommended.
    You can also use [pipx](https://pypa.github.io/pipx/), a great tool that isolate the package
    and its dependencies in a virtualenv and expose only its scripts/entrypoints (_/bin_) like CLIs.

<!-- --8<-- [end:install] -->
### Usage

#### Configuration
<!-- --8<-- [start:config] -->

To begin with, whether you'll use our API or CLI you will need to setup some configuration.

```bash
tao config -a https://hub.eoafrica-dunia.org -u <username>
```

To interact with the TAO API you will need to login to the API.

```bash
tao login
```

You will be prompted for your password. When you log-in an API token is retrieved,
but it will expire after some time! You will need to login again.

You may check if everything's working by trying to request the API. Try the following:

```bash
tao component list --page 1 --page-size 1
```

A Processing Component should be displayed, congratulation!

<!-- --8<-- [end:config] -->
#### Publishing
<!-- --8<-- [start:publish] -->

The first and foremost important thing you can do is publish.
This is the TAO **Publisher** after all!

But publish what? You can publish two types of thing:

- **Toolbox Container**: docker image that contains executables and/or scripts,
called applications.
- **Processing Component**: used to define processing pipelines in TAO,
more precisely **Workflows**. Run within a Toolbox Container.

You could say a container is the execution environment used by the component.

With our publisher, you can create/develop containers locally and publish it to TAO,
while defining its related components. The publishing process is based on a file,
we will call it the **publish file**. This file is used to declare a container,
as well as the components linked to it. Declaring components is complex and tricky,
for our first publication we will only publish a container.

Check our _How-to_ guides to learn about component publication.

// TODO

<!-- --8<-- [end:publish] -->
