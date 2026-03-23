# ansibleConfigGenerator

## Overview

ansibleConfigGenerator is a toolkit that generates Ansible host variable files and related artifacts for [ansible-linux-setup](https://github.com/takeharukato/ansible-linux-setup) from functions of computing nodes and network topology definitions.

The project provides 6 command-line tools:

- generate_host_vars_structured
- generate_host_vars_files
- generate_hostvars_matrix
- validate_hostvars_matrix
- generate_network_topology_design_sheet
- generate_terraform_tfvars

For schema/config lookup order and `schema_search_paths` details, see `docs/manual/toolchain-overview.md` ("スキーマと設定ファイルの探索順" and "設定ファイル形式 (schema_search_paths)").

## Prerequisite Packages

- Python 3.9 or later
- PyYAML
- jsonschema
- gettext 0.21 or later
- autoconf 2.69 or later
- automake 1.16 or later
- docker (only when running make rpm or make deb)

## Directory Structure

```text
.
├── autogen.sh
├── configure.ac
├── Makefile.am
├── Readme.md
├── ReadmeEN.md
├── requirements.txt
├── src/
│   └── genAnsibleConf/
│       ├── generate_host_vars_structured
│       ├── generate_host_vars_files
│       ├── generate_hostvars_matrix
│       ├── generate_network_topology_design_sheet
│       ├── generate_terraform_tfvars
│       ├── validate_hostvars_matrix
│       ├── field_metadata.yaml
│       ├── field_metadata.schema.yaml
│       ├── network_topology.schema.yaml
│       ├── host_vars_structured.schema.yaml
│       ├── convert-rule-config.yaml
│       └── lib/
├── config/
│   ├── sample-network_topology.yaml
│   ├── genAnsibleConf.system-config.yaml
│   └── genAnsibleConf.user-config.yaml
├── docs/
│   ├── SPECIFICATION.md
│   ├── commands-specJP.md
│   ├── manual/
│   ├── sphinx/
│   └── debug/
├── tests/
├── debian/
├── rpm/
└── Dockerfiles/
```

The contents of each directory are summarized below:

| Directory | Main purpose | Main contents |
|---|---|---|
| `src/genAnsibleConf/` | Core scripts and schema definitions | host_vars generators, YAML/JSON Schema files, shared Python library |
| `config/` | Sample and runtime config files | user config, system config, sample network topology |
| `docs/` | Japanese specifications and user documentation | specification, command reference, manuals, Sphinx sources |
| `tests/` | Automated tests | pytest-based tests and supporting test assets |
| `debian/` | Debian package definition | control, rules, copyright, install manifest |
| `rpm/` | RPM package definition | spec file |
| `Dockerfiles/` | Containerized package build definitions | RPM/Deb Dockerfiles and entrypoint scripts |

### Main files under src/genAnsibleConf/

| File/Directory | Description |
|---|---|
| `generate_host_vars_structured` | Generates structured host_vars from network topology definitions. |
| `generate_host_vars_files` | Generates per-node host_vars files from structured host_vars. |
| `generate_hostvars_matrix` | Generates a CSV matrix view of node scalar settings. |
| `validate_hostvars_matrix` | Validates matrix and structured data consistency. |
| `generate_network_topology_design_sheet` | Generates CSV files for network design review. |
| `generate_terraform_tfvars` | Generates terraform.tfvars from topology definitions. |
| `field_metadata.yaml` | Defines scalar field metadata and descriptions for host_vars. |
| `field_metadata.schema.yaml` | Schema definition for field_metadata.yaml. |
| `network_topology.schema.yaml` | Schema definition for network topology input files. |
| `host_vars_structured.schema.yaml` | Schema definition for structured host_vars output. |
| `convert-rule-config.yaml` | Field and service conversion rules. |
| `lib/` | Shared Python library modules used by generator scripts. |

### Files under config/

| File | Description |
|---|---|
| `sample-network_topology.yaml` | Comprehensive sample for network topology definitions. |
| `genAnsibleConf.system-config.yaml` | Example of system-wide configuration file. |
| `genAnsibleConf.user-config.yaml` | Example of per-user configuration file. |

### Main contents under docs/

| File/Directory | Description |
|---|---|
| `SPECIFICATION.md` | Overall behavior and data format specification. |
| `commands-specJP.md` | Japanese command input/output reference. |
| `manual/` | User guides, references, and troubleshooting documents. |
| `sphinx/` | Sources for generating Sphinx HTML documentation. |
| `debug/` | Debugging and development helper documents/settings. |

### Files under Dockerfiles/

| File | Description |
|---|---|
| `deb.ubuntu24.04.Dockerfile` | Ubuntu 24.04-based container for Debian package builds. |
| `rpm.almalinux9.Dockerfile` | AlmaLinux 9-based container for RPM package builds. |
| `entrypoint-deb.sh` | Entrypoint script for Debian package build container. |
| `entrypoint-rpm.sh` | Entrypoint script for RPM package build container. |

## Installation

```shell
./autogen.sh
./configure
make
make install
```

To install into a custom prefix:

```shell
./configure --prefix=/tmp/test
make
make install
```

## make Targets

- make: build project artifacts
- make install: install scripts, python modules, and schema files
- make check: run test suite
- make clean: remove build artifacts
- make dist: create source tarball
- make cloc: count lines of code (requires cloc)
- make coverage: run coverage measurement
- make docs: build Sphinx docs
- make rpm: build RPM package via Docker
- make deb: build Debian package via Docker

Packaging outputs are generated under dist/.

## Example Usage

Generate host_vars_structured.yaml from network_topology.yaml:

```shell
generate_host_vars_structured -i network_topology.yaml -o host_vars_structured.yaml
```

Generate per-host host_vars files:

```shell
generate_host_vars_files host_vars.gen -i host_vars_structured.yaml -m field_metadata.yaml
```

Generate node parameter matrix CSV:

```shell
generate_hostvars_matrix -H host_vars_structured.yaml -m field_metadata.yaml -o host_vars_scalars_matrix.csv
```

Generate design sheet CSV files:

```shell
generate_network_topology_design_sheet -i network_topology.yaml -o .
```

Generate terraform.tfvars:

```shell
generate_terraform_tfvars -t network_topology.yaml -o terraform.tfvars
```

Force schema lookup from a specific directory:

```shell
generate_hostvars_matrix --schema-dir /path/to/schema -H host_vars_structured.yaml
```

For detailed usage instructions, see docs/manual/index.md.

## Tests

```shell
make check
```

or

```shell
PYTHONPATH=.:tests python3 -m pytest tests/tests_py -q
```

## License

Copyright 2025 Takeharu KATO.

This project is distributed under the BSD 2-Clause License.
See the LICENSE file for details.
