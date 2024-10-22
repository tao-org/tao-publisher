# TAO Publisher
<!-- --8<-- [start:overview-header] -->

![License](https://img.shields.io/badge/license-Apache--2.0-yellow?style=flat-square)
[![Language](https://img.shields.io/badge/language-Python-3776ab?style=flat-square&logo=Python)](https://www.python.org/)
[![Documentation](https://img.shields.io/badge/documentation-mkdocs-0a507a?style=flat-square)](https://www.mkdocs.org/)
![Style](https://img.shields.io/badge/style-ruff-9a9a9a?style=flat-square)
![Lint](https://img.shields.io/badge/lint-ruff,%20mypy-brightgreen?style=flat-square)
![Security](https://img.shields.io/badge/security-bandit,%20pip%20audit-purple?style=flat-square)

The TAO Publisher is a client developed for [TAO](https://hub.eoafrica-dunia.org/ui/sap.html)
that provides an easy publishing interface with the service through a Python API / CLI.

<!-- --8<-- [end:overview-header] -->
## Table of Contents

- [Getting started](#getting-started)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Configuration](#configuration)
    - [Publishing](#publishing)
- [Contributing](#contributing)
- [License](#license)

<!-- --8<-- [start:overview-content] -->
## Getting started

### Installation
<!-- --8<-- [start:install] -->

This project can be installed from its source code.

```bash
pip install git+https://github.com/tao-org/tao-publisher.git
```

You can use `git+https://github.com/tao-org/tao-publisher.git@<tag>`
to install a specific version.

You can also clone the repo and install from it locally:

```bash
git clone https://github.com/tao-org/tao-publisher.git
cd tao-publisher
pip install .
```

The use of a virtual environment is greatly recommended.

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

<!-- --8<-- [end:publish] -->
<!-- --8<-- [end:overview-content] -->
## Contributing

If you want to contribute to this project or understand how it works,
please check [CONTRIBUTING.md](CONTRIBUTING.md).

Any contribution is greatly appreciated.

## License

Distributed under the Apache-2.0 License. See [LICENSE](LICENSE) for more
information.
