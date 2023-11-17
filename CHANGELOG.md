## v0.1.0 (2023-11-17)

### Feat

- better APIClient.request annotation for 'method' parameter
- improve publish errors with missing files
- can disable config load, can give value for config init
- add component API and cli command
- improve rich display of containers
- EndpointAPI auth required, add class parameters
- add user to config
- config file can be changed, improve load/write
- add component model for list endpoint and add/fix fields
- endpoints api make APIClient optional with default one
- add --quiet for verbosity 0, default verbosity to 1
- add container register to publish containers and its components
- add file request serialization methods to utils.http
- client request files upload
- add container read to parse container file and validate its content
- add container init to create base container spec
- add utils.file with parsing and writing methods
- add slugify to utils.http
- complete models with component-related models and container spec file
- add container list query params support
- set imports in __init__.py files for better access
- add container delete
- add container get
- add container list
- add login command
- add configuration management
- add logging with verbosity level from CLI

### Fix

- endpoints list sortBy and sortByField set only when paginating
- better parsing of Container format and ParameterDescriptors default value
- simpler login info log
- config token init
- container and component pagination
- ComponentAPI get bug workaround, must fix back later
- container get and list remove --applications, remove --logo for container list
- parser_file error handling was not covering all errors
- use click.get_app_dir to define DEFAULT_CONFIG_DIR
- change is_uri to is_url for better validation
- container get and delete now requires at least one id
- correct models and update container init
- annotate client request return
- login error handling
- remove periods from logs
- CLI save config only when needed
- config display token renamed to auth
- json print correctly formatted
- remove markup and colors in logs
- use api message for errors
- remove container list rich highlight on str for visibility on terminal light theme
- use rich console for prints

### Refactor

- make get_logger and get_console private
- move tao.cli to tao._cli to make it private
- config rename write() as save()
- cli display method per models
- separate register-related things from container API/models for abstraction
- mark some functions as private in utils.file
- rename services to endpoints
- restructurations, improve errors, logs, docs
- add client to api module and create module api.services
- rename click commands get and delete with prefix 'container_'
- create Application model for better Container validation
- rename ContainerDescription to Container
- improve error handling
- improve architecture
- change errors thrown in client
