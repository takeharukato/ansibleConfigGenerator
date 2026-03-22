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
"""globals.roles 定義に基づくサービス供給先マップ構築を提供するモジュールである。"""

from __future__ import annotations

from typing import Any, cast


def build_supply_map(
    nodes: list[dict[str, Any]],
    globals_roles: dict[str, list[str]],
) -> dict[str, list[str]]:
    """globals.roles 定義からサービス供給先マップを構築する。

    Args:
        nodes (list[dict[str, Any]]): ノード一覧である。
        globals_roles (dict[str, list[str]]): roles 定義である。

    Returns:
        dict[str, list[str]]: サービス名から供給対象ノード名一覧への写像である。

    Examples:
        >>> build_supply_map([], {})
        {}
    """
    supply_map: dict[str, list[str]] = {}
    role_to_nodes: dict[str, list[str]] = {}
    for node in nodes:
        for role_name in cast(list[str], node.get('roles', [])):
            role_to_nodes.setdefault(role_name, []).append(node['name'])

    for role_name, service_list in globals_roles.items():
        role_nodes: list[str] = role_to_nodes.get(role_name, [])
        for service_name in service_list:
            current: set[str] = set(supply_map.get(service_name, []))
            supply_map[service_name] = list(current | set(role_nodes))

    return supply_map
