# Contributing

First off, thanks for taking the time to contribute! 🎉

The following elements will allow you to contribute with a little guide
to learn how to make an approved contribution. Don't hesitate to share
some new ideas to improve it!

## Table of Contents

- [Getting started](#getting-started)
  - [Pre-requisites](#pre-requisites)
  - [Clone the repository](#clone-the-repository)
  - [Environment setup](#environment-setup)
- [How to contribute?](#how-to-contribute)
  - [Organization](#organization)
    - [Reporting Issues](#reporting-issues)
    - [Suggesting Enhancements](#suggesting-enhancements)
    - [Submitting Pull Requests](#submitting-pull-requests)
  - [Writing code](#writing-code)
    - [References](#references)
    - [Quality Assurance](#quality-assurance)
      - [Lint](#lint)
      - [Tests](#tests)
      - [Security](#security)
      - [Documentation](#documentation)
    - [Release](#release)

## Getting started

### Pre-requisites

We recommended a linux-based distribution. You will need the following
tools on your system:

- [Git](https://git-scm.com/)
- [Make](https://www.gnu.org/software/make/)
- [Python](https://www.python.org/)
- [Virtualenv](https://virtualenv.pypa.io/)

### Clone the repository

```bash
git clone https://github.com/csgroup-oss/tao-publisher
```

### Environment setup

First, create an isolated Python virtual environment:

```bash
virtualenv -p python3.10 .venv
source .venv/bin/activate
pip install --upgrade pip
# OR
python3.10 -m venv --upgrade-deps .venv
source .venv/bin/activate
```

List available commands:

```bash
make help
```

You must also install in editable mode, with dev dependencies.

```bash
make install-dev
```

This project uses multiple tools for its development, and your virtual
environment created earlier is just here to give you a working
development environment. Some tools are handled in sub-virtual
environments created by [Tox](https://tox.wiki), a virtual env manager
and automation tool. The `install-dev` only gives you the tools that you
will be directly using, delegating other installations inside of *Tox*
virtual envs.

In order to complete the environment setup, you must install some Git
Hooks.

```bash
pre-commit install --install-hooks
```

## How to contribute?

### Organization

#### Reporting Issues

Issue tracker: <https://github.com/csgroup-oss/tao-publisher/issues>

If you find a bug, please create an issue in the issue tracker and
provide the following information:

- **Description**: Provide a clear and concise description of the problem.
- **Steps to Reproduce**: List the steps to reproduce the problem.
- **Expected Behavior**: Describe what you expected to happen.
- **Actual Behavior**: Describe what actually happened.
- **Screenshots**: If applicable, add screenshots to help explain your problem.
- **Environment**: Provide information about your environment, such as
  your operating system and version, and the version of the project you are using.

#### Suggesting Enhancements

If you have an idea to improve the project, we would love to hear it!
Please create an issue and provide the following information:

- **Description**: Provide a clear and concise description of the enhancement.
- **Rationale**: Explain why this enhancement would be useful.
- **Implementation**: If possible, describe how you would implement the enhancement.

#### Submitting Pull Requests

1. **Fork the Repository**: Create a fork of the repository by clicking the
   "Fork" button on the repository page.
2. **Clone the Fork**: Clone your fork to your local machine.

   ```shell
   git clone https://github.com/csgroup-oss/tao-publisher.git
   cd tao-publisher
   python3 -mvenv .venv
   source .venv/bin/activate
   make install-dev
   pre-commit install --install-hooks
   git checkout -b (fix-or-feat)/your-topic-name
   ```

3. **Commit changes**: Commit your changes with a clear and concise commit message.
4. **Push changes**: Push your changes to your fork

   ```shell
   git push origin (fix-or-feat)/your-topic-name
   ```

5. **Create a Pull Request**: Create a pull request from your fork's branch to the
   main repository's main branch. Provide a clear and concise description of your
   changes and the problem they address.

### Writing code

#### References

Writing clean code is very important for a project. References such as
"Clean Code", by Robert C. Martin, are good to keep in mind. Readable
code is not a luxury, it is a necessity.

Let us be reminded of the Zen of Python, by Tim Peters:

```text
Beautiful is better than ugly.
Explicit is better than implicit.
Simple is better than complex.
Complex is better than complicated.
Flat is better than nested.
Sparse is better than dense.
Readability counts.
Special cases aren't special enough to break the rules.
Although practicality beats purity.
Errors should never pass silently.
Unless explicitly silenced.
In the face of ambiguity, refuse the temptation to guess.
There should be one-- and preferably only one --obvious way to do it.
Although that way may not be obvious at first unless you're Dutch.
Now is better than never.
Although never is often better than *right* now.
If the implementation is hard to explain, it's a bad idea.
If the implementation is easy to explain, it may be a good idea.
Namespaces are one honking great idea -- let's do more of those!
```

You are not alone for this difficult task. In the next sections you will
find about our recommended development method, our linting and
formatting tools, and how to use tests.

#### Quality Assurance

##### Lint

To ensure good code writing, we use a lot of lint tools:

- [validate-pyproject](https://validate-pyproject.readthedocs.io):
    command line tool and Python library for validating
    `pyproject.toml`, includes models defined for `PEP 517`, `PEP 518`
    and `PEP 621`.
- [ruff](https://docs.astral.sh/ruff/): an extremely fast Python linter and formatter,
    written in Rust. Integrate `pyupgrade`, `pylint`, `bandit`, `isort`,
    `eradicate`, and `flake8` with dozens of its plugins.
- [mypy](https://mypy.readthedocs.io): static type checker.

These tools are run with:

```bash
make lint
```

You can use `lint-watch` to run ruff on `src/` with `--watch` flag. This
is really useful as it gives you instantaneous feedback on your code.

> Note: All of these are also run for each commit, failing the commit
> if at least one error is found.

##### Tests

The test frameworks used are unittest and pytest, run with tox.

Run the tests with *make*:

```bash
make test
```

##### Security

We use [pip-audit](https://pypi.org/project/pip-audit/) to check our Python
dependencies for potential security vulnerabilities and suggests the
proper remediation for vulnerabilities detected.

```bash
make security
```

##### Documentation

Doing features is great, but it is useless if nobody knows how to use
them. Keeping a clean, up-to-date documentation is of high priority.

This project is documented with [MkDocs](https://www.mkdocs.org/).
The documentation source can be found in the `docs/src` folder.

You can build the docs with:

```bash
make docs
```

If you want to build the docs, and serve it with an http server after
the build:

```bash
make docs serve
```

When writing the docs, use the live server to automatically rebuild the
docs.

```bash
make docs-live
```

#### Release

You can create a release with `make release`. Because we follow a
[Conventional Commit](https://www.conventionalcommits.org/en/v1.0.0/),
the next version can be guessed from the commit history.
The `CHANGELOG.md` is generated automatically too.

Don't forget to push the tags to your origin repo!

```bash
git push --tags
```
