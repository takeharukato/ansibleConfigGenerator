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
"""internal_network_list の統合と適用条件を検証する。"""

from __future__ import annotations

from typing import Any

from src.genAnsibleConf.lib.global_params import build_global_scalars
from src.genAnsibleConf.lib.hostvars_node_pipeline import initialize_node_entry_and_scalars


def test_build_global_scalars_merges_and_dedupes_internal_network_list() -> None:
    """static と dynamic の internal_network_list を統合し重複除去する。"""
    globals_def: dict[str, Any] = {
        "scalars": {
            "internal_network_list": [
                {"ipv4": "10.0.0.0/24"},
                {"ipv6": "fd00::/64"},
            ],
            "sample": "value",
        }
    }
    dynamic_internal_network_list: list[dict[str, str]] = [
        {"ipv4": "10.0.0.0/24"},
        {"ipv4": "192.168.1.0/24"},
    ]

    actual: dict[str, Any] = build_global_scalars(
        globals_def,
        dynamic_internal_network_list=dynamic_internal_network_list,
    )

    assert actual["sample"] == "value"
    assert actual["internal_network_list"] == [
        {"ipv4": "10.0.0.0/24"},
        {"ipv6": "fd00::/64"},
        {"ipv4": "192.168.1.0/24"},
    ]


def test_initialize_node_entry_and_scalars_does_not_leak_internal_network_list() -> None:
    """internal_network_list はノード初期化段階では無条件注入しない。"""
    node: dict[str, Any] = {
        "name": "node01",
        "hostname_fqdn": "node01.example.local",
        "interfaces": [],
        "scalars": {},
    }
    global_scalars: dict[str, Any] = {
        "internal_network_list": [{"ipv4": "10.0.0.0/24"}],
        "ntp_servers_list": ["ntp1.example.local"],
    }

    _host_entry: dict[str, Any]
    scalars: dict[str, Any]
    _connected: bool
    _host_entry, scalars, _connected = initialize_node_entry_and_scalars(
        node,
        {},
        "private_control_plane_network",
        global_scalars,
        {},
        None,
    )

    assert "internal_network_list" not in scalars
    assert scalars["ntp_servers_list"] == ["ntp1.example.local"]
