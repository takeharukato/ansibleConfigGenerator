# -*- mode: python; coding: utf-8; line-endings: unix -*-
# SPDX-License-Identifier: BSD-2-Clause
# Copyright (c) 2025 TAKEHARU KATO
# This file is distributed under the two-clause BSD license.
# For the full text of the license, see the LICENSE file in the project root directory.
# このファイルは2条項BSDライセンスの下で配布されています。
# ライセンス全文はプロジェクト直下の LICENSE を参照してください。
#
# OpenAI's ChatGPT partially generated this code.
# Author has modified some parts.
# OpenAIのChatGPTがこのコードの一部を生成しました。
# 著者が修正している部分があります。
"""generate_terraform_tfvars の挙動テスト。"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable, cast

import pytest

SOURCE_DIR: Path = Path(__file__).resolve().parents[2] / "src"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from genAnsibleConf.cli import generate_terraform_tfvars as terraform_tfvars_module
terraform_tfvars_module_any: Any = terraform_tfvars_module

BuildNetworkRolesType = Callable[[dict[str, Any], dict[str, str]], dict[str, list[str]]]
ConvertInterfacesType = Callable[[dict[str, Any], dict[str, str]], list[dict[str, Any]]]
RenderTfvarsType = Callable[[dict[str, Any], dict[str, dict[str, Any]], dict[str, list[str]]], str]

build_network_roles: BuildNetworkRolesType = cast(
    BuildNetworkRolesType,
    terraform_tfvars_module_any.build_network_roles,
)
convert_interfaces_to_networks: ConvertInterfacesType = cast(
    ConvertInterfacesType,
    terraform_tfvars_module_any.convert_interfaces_to_networks,
)
render_tfvars: RenderTfvarsType = cast(
    RenderTfvarsType,
    terraform_tfvars_module_any.render_tfvars,
)


def test_convert_interfaces_to_networks_raises_for_unmapped_network() -> None:
    """未登録 network を node.interfaces で検出した場合は失敗する。"""
    node: dict[str, Any] = {
        "name": "node01",
        "interfaces": [
            {"network": "mgmt_external", "mac": "00:11:22:33:44:55"},
            {"network": "unknown_net", "mac": "00:11:22:33:44:66"},
        ],
    }
    network_key_map: dict[str, str] = {"mgmt_external": "ext_mgmt"}

    with pytest.raises(ValueError, match="network_key_map"):
        convert_interfaces_to_networks(node, network_key_map)


def test_build_network_roles_skips_unmapped_globals_networks() -> None:
    """globals.networks 側の未登録 network は role 集約結果に含めない。"""
    globals_networks: dict[str, Any] = {
        "mgmt_external": {"role": "external_control_plane_network"},
        "orphan_network": {"role": "external_control_plane_network"},
    }
    network_key_map: dict[str, str] = {"mgmt_external": "ext_mgmt"}

    actual_roles: dict[str, list[str]] = build_network_roles(globals_networks, network_key_map)

    assert actual_roles == {"external_control_plane_network": ["ext_mgmt"]}


def test_render_tfvars_includes_network_roles_block() -> None:
    """render_tfvars は network_roles を HCL 出力へ含める。"""
    env_config: dict[str, Any] = {
        "xoa_url": "ws://xoa.example.local",
        "xoa_username": "admin@admin.net",
        "xoa_insecure": True,
        "xcpng_pool_name": "pool01",
        "xcpng_sr_name": "Local storage",
        "xcpng_template_ubuntu": "ubuntu-vm",
        "xcpng_template_rhel": "rhel-vm",
        "xcpng_vm_vcpus": 4,
        "xcpng_vm_mem_mb": 4096,
        "xcpng_vm_disk_gb": 25,
        "network_names": {"ext_mgmt": "External Mgmt"},
        "network_options": {},
        "vm_group_defaults": {
            "infrastructure": {
                "default_template_type": "ubuntu",
                "default_firmware": "uefi",
            }
        },
    }
    vm_groups: dict[str, dict[str, Any]] = {}
    network_roles: dict[str, list[str]] = {
        "external_control_plane_network": ["ext_mgmt"]
    }

    rendered_hcl: str = render_tfvars(env_config, vm_groups, network_roles)

    assert "network_roles = {" in rendered_hcl
    assert 'external_control_plane_network = ["ext_mgmt"]' in rendered_hcl
