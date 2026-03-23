# -*- mode: makefile; coding: utf-8; line-endings: unix -*-
# SPDX-License-Identifier: BSD-2-Clause
# Copyright (c) 2026 Takeharu KATO
#
# This file is distributed under the two-clause BSD license.
# For the full text of the license, see the LICENSE file in the project root directory.
# このファイルは2条項BSDライセンスの下で配布されています。
# ライセンス全文はプロジェクト直下の LICENSE を参照してください。
#
# OpenAI's ChatGPT partially generated this code.
# Author has modified some parts.
# OpenAIのChatGPTがこのコードの一部を生成しました。
# 著者が修正している部分があります。

## 実行スクリプト
bin_SCRIPTS = \
	generate_host_vars_files \
	generate_host_vars_structured \
	generate_hostvars_matrix \
	validate_hostvars_matrix \
	generate_network_topology_design_sheet \
	generate_terraform_tfvars

## Python パッケージ本体
pythondir = @pythondir@/genAnsibleConf
python_PYTHON = \
	__init__.py

## Python CLI サブモジュール
clipythondir = $(pythondir)/cli
clipython_PYTHON = \
	cli/__init__.py \
	cli/generate_host_vars_files.py \
	cli/generate_host_vars_structured.py \
	cli/generate_hostvars_matrix.py \
	cli/validate_hostvars_matrix.py \
	cli/generate_network_topology_design_sheet.py \
	cli/generate_terraform_tfvars.py

## Python サブモジュール
libpythondir = $(pythondir)/lib
libpython_PYTHON = \
	lib/__init__.py \
	lib/cli_defaults.py \
	lib/cluster_platform.py \
	lib/global_params.py \
	lib/hostvars_node_pipeline.py \
	lib/hostvars_runtime_context.py \
	lib/k8s_cluster_platform.py \
	lib/k8s_neighbor.py \
	lib/k8s_normalize.py \
	lib/neighbor_provider.py \
	lib/netif_builder.py \
	lib/network_core.py \
	lib/network_role_policy.py \
	lib/node_topology_utils.py \
	lib/routing_frr.py \
	lib/service_processing.py \
	lib/service_rules.py \
	lib/supply_map.py \
	lib/user_merge.py \
	lib/yaml_io.py

## schema/config YAML
genansibleconfschemadir = $(datadir)/genAnsibleConf/schema
genansibleconfschema_DATA = \
	convert-rule-config.yaml \
	field_metadata.yaml \
	field_metadata.schema.yaml \
	host_vars_structured.schema.yaml \
	network_topology.schema.yaml

## 配布に含めるが install しないファイル
EXTRA_DIST = \
	generate_host_vars_files \
	generate_host_vars_structured \
	generate_hostvars_matrix \
	validate_hostvars_matrix \
	generate_network_topology_design_sheet \
	generate_terraform_tfvars \
	cli/__init__.py \
	cli/generate_host_vars_files.py \
	cli/generate_host_vars_structured.py \
	cli/generate_hostvars_matrix.py \
	cli/validate_hostvars_matrix.py \
	cli/generate_network_topology_design_sheet.py \
	cli/generate_terraform_tfvars.py \
	convert-rule-config.yaml \
	field_metadata.yaml \
	network_topology.schema.yaml \
	field_metadata.schema.yaml \
	host_vars_structured.schema.yaml \
	terraform.tfvars
