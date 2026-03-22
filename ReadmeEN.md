# ansibleConfigGenerator

## Overview

ansibleConfigGenerator is a toolkit that generates Ansible host variable files and related artifacts for [ansible-linux-setup](https://github.com/takeharukato/ansible-linux-setup) from functions of computing nodes and network topology definitions.

The project provides 5 command-line tools:

- generate_host_vars_structured.py
- generate_host_vars_files.py
- generate_hostvars_matrix.py
- generate_network_topology_design_sheet.py
- generate_terraform_tfvars.py

The schema/config file lookup order is fixed to the following 5-step cascade:

1. CLI option: --schema-dir
2. User config: ~/.genAnsibleConf.yaml
3. System config: /etc/genAnsibleConf/config.yaml
4. Datadir: ${datadir}/genAnsibleConf/schema
5. Script directory fallback

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
├── requirements.txt
├── src/
│   └── genAnsibleConf/
│       ├── generate_host_vars_structured.py
│       ├── generate_host_vars_files.py
│       ├── generate_hostvars_matrix.py
│       ├── generate_network_topology_design_sheet.py
│       ├── generate_terraform_tfvars.py
│       ├── field_metadata.yaml
│       ├── network_topology.schema.yaml
│       ├── type_schema.yaml
│       ├── convert-rule-config.yaml
│       └── lib/
├── config/
│   ├── genAnsibleConf.system-config.yaml
│   └── genAnsibleConf.user-config.yaml
├── tests/
├── debian/
├── rpm/
└── Dockerfiles/
```

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

## Configuration Files

The tools search for configuration files in the following order:

1. User config: `~/.genAnsibleConf.yaml`
2. System config: `/etc/genAnsibleConf/config.yaml`

Both files are optional. When found, the `schema_search_paths` section is read to locate schema files.
If neither file exists, schema files are located via the remaining steps of the 5-step cascade described in the Overview (Datadir -> Script directory fallback).

The configuration file format is:

`schema_search_paths` keys:

| Key | Description | Example |
|---|---|---|
| `field_metadata` | Path to the field metadata YAML file | `~/.genAnsibleConf/field_metadata.yaml` |
| `network_topology` | Path to the network topology JSON Schema file | `~/.genAnsibleConf/network_topology.schema.yaml` |
| `type_schema` | Path to the type schema YAML file | `~/.genAnsibleConf/type_schema.yaml` |
| `convert_rule_config` | Path to the conversion rule config YAML file | `~/.genAnsibleConf/convert-rule-config.yaml` |
| `default_dir` | Default directory used when a key-specific path is not set | `~/.genAnsibleConf` |

Configuration file example:

```yaml
schema_search_paths:
  field_metadata: ~/.genAnsibleConf/field_metadata.yaml
  network_topology: ~/.genAnsibleConf/network_topology.schema.yaml
  type_schema: ~/.genAnsibleConf/type_schema.yaml
  convert_rule_config: ~/.genAnsibleConf/convert-rule-config.yaml
  default_dir: ~/.genAnsibleConf
```

Sample files:

- config/genAnsibleConf.user-config.yaml
- config/genAnsibleConf.system-config.yaml

## Example Usage

Generate host_vars_structured.yaml from network_topology.yaml:

```shell
generate_host_vars_structured.py -i network_topology.yaml -o host_vars_structured.yaml
```

Generate per-host host_vars files:

```shell
generate_host_vars_files.py host_vars.gen -i host_vars_structured.yaml -m field_metadata.yaml
```

Generate matrix CSV:

```shell
generate_hostvars_matrix.py -H host_vars_structured.yaml -m field_metadata.yaml -o host_vars_scalars_matrix.csv
```

Generate design sheet CSV files:

```shell
generate_network_topology_design_sheet.py -i network_topology.yaml -o .
```

Generate terraform.tfvars:

```shell
generate_terraform_tfvars.py -t network_topology.yaml -o terraform.tfvars
```

Force schema lookup from a specific directory:

```shell
generate_hostvars_matrix.py --schema-dir /path/to/schema -H host_vars_structured.yaml
```

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
