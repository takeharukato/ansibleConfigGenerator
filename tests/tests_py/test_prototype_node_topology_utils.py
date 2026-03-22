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
"""node_topology_utils の単体テスト。"""

from __future__ import annotations

from typing import Any

from src.genAnsibleConf.lib.node_topology_utils import (
    get_globals_mapping,
    get_globals_networks,
    get_globals_services,
    get_node_interfaces,
    get_node_map,
    get_node_roles,
    node_has_role,
)


def test_node_has_role_returns_false_for_non_list_roles() -> None:
    """roles が list でない場合は False を返す。"""
    node: dict[str, Any] = {"roles": "k8s_control_plane"}

    assert node_has_role(node, "k8s_control_plane") is False


def test_get_globals_mapping_returns_empty_when_missing() -> None:
    """globals 欠落時は空辞書を返す。"""
    topology: dict[str, Any] = {}

    assert get_globals_mapping(topology) == {}


def test_get_globals_networks_returns_empty_for_non_dict() -> None:
    """globals.networks が dict でない場合は空辞書を返す。"""
    topology: dict[str, Any] = {"globals": {"networks": []}}

    assert get_globals_networks(topology) == {}


def test_get_globals_services_returns_empty_for_non_dict() -> None:
    """globals.services が dict でない場合は空辞書を返す。"""
    topology: dict[str, Any] = {"globals": {"services": []}}

    assert get_globals_services(topology) == {}


def test_get_node_map_builds_name_keyed_mapping() -> None:
    """name キーを使ってノードマップ化できる。"""
    nodes: list[dict[str, Any]] = [{"name": "n1"}, {"name": "n2"}]

    actual_map: dict[str, dict[str, Any]] = get_node_map(nodes)

    assert sorted(actual_map.keys()) == ["n1", "n2"]


def test_get_node_interfaces_returns_empty_when_missing() -> None:
    """interfaces 欠落時は空リストを返す。"""
    node: dict[str, Any] = {}

    assert get_node_interfaces(node) == []


def test_get_node_roles_filters_non_string_items() -> None:
    """roles は文字列のみを返す。"""
    node: dict[str, Any] = {"roles": ["k8s_worker", 1, None]}

    assert get_node_roles(node) == ["k8s_worker"]
