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
"""自動導出サービス設定注入の単体テスト。"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable

from src.genAnsibleConf.lib.service_processing import (
    apply_auto_service_configs,
    merge_auto_config_into_service,
)

PROTOTYPE_DIR: Path = Path(__file__).resolve().parents[2] / "src" / "genAnsibleConf"
if str(PROTOTYPE_DIR) not in sys.path:
    sys.path.insert(0, str(PROTOTYPE_DIR))


MergeAutoConfigType = Callable[[dict[str, Any], str, dict[str, Any]], dict[str, Any]]
ApplyAutoConfigType = Callable[
    [
        dict[str, Any],
        dict[str, Any],
        dict[str, dict[str, Any]],
        dict[str, list[str]],
        str,
        str,
    ],
    dict[str, Any],
]

merge_auto_config_into_service_typed: MergeAutoConfigType = merge_auto_config_into_service
apply_auto_service_configs_typed: ApplyAutoConfigType = apply_auto_service_configs


def test_merge_auto_config_into_service_preserves_explicit_values() -> None:
    """自動導出値より既存明示値を優先してマージする。"""
    merged_services: dict[str, Any] = {
        "internal_router": {
            "config": {
                "network_ipv4_prefix_len": 28,
                "custom_key": "keep",
            }
        }
    }
    auto_config: dict[str, Any] = {
        "network_ipv4_network_address": "192.168.20.0",
        "network_ipv4_prefix_len": 24,
    }

    actual: dict[str, Any] = merge_auto_config_into_service_typed(
        merged_services,
        "internal_router",
        auto_config,
    )

    config: dict[str, Any] = actual["internal_router"]["config"]
    assert config["network_ipv4_network_address"] == "192.168.20.0"
    assert config["network_ipv4_prefix_len"] == 28
    assert config["custom_key"] == "keep"


def test_apply_auto_service_configs_injects_radvd_when_enabled() -> None:
    """radvd が有効なノードで自動導出設定を注入する。"""
    node: dict[str, Any] = {
        "name": "node01",
        "interfaces": [{"network": "mgmt_internal"}],
        "services": {
            "radvd": {
                "config": {
                    "radvd_search_domains": ["override.example.local"],
                }
            }
        },
    }
    merged_services: dict[str, Any] = dict(node["services"])
    networks: dict[str, dict[str, Any]] = {
        "mgmt_internal": {
            "role": "private_control_plane_network",
            "ipv6_cidr": "fdad:ba50:248b:1::/64",
            "name_servers_ipv6": ["fd69:6684:61a:1::11"],
            "dns_search": "example.local",
        }
    }
    supply_map: dict[str, list[str]] = {"radvd": ["node01"]}

    actual: dict[str, Any] = apply_auto_service_configs_typed(
        node,
        merged_services,
        networks,
        supply_map,
        "private_control_plane_network",
        "external_control_plane_network",
    )

    radvd_config: dict[str, Any] = actual["radvd"]["config"]
    assert radvd_config["radvd_router_advertisement_prefix"] == "fdad:ba50:248b:1::/64"
    assert radvd_config["radvd_dns_servers"] == ["fd69:6684:61a:1::11"]
    assert radvd_config["radvd_search_domains"] == ["override.example.local"]


def test_apply_auto_service_configs_skips_when_service_not_enabled() -> None:
    """供給対象でないサービスは注入しない。"""
    node: dict[str, Any] = {
        "name": "node01",
        "interfaces": [{"network": "mgmt_external"}],
    }
    merged_services: dict[str, Any] = {}
    networks: dict[str, dict[str, Any]] = {
        "mgmt_external": {
            "role": "external_control_plane_network",
            "ipv4_cidr": "192.168.20.0/24",
        }
    }
    supply_map: dict[str, list[str]] = {}

    actual: dict[str, Any] = apply_auto_service_configs_typed(
        node,
        merged_services,
        networks,
        supply_map,
        "private_control_plane_network",
        "external_control_plane_network",
    )

    assert actual == {}
