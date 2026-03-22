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
"""topology 辞書アクセス用の軽量 helper 群を提供するモジュールである。"""

from __future__ import annotations

from typing import Any, cast


def get_node_roles(node: dict[str, Any]) -> list[str]:
    """ノード定義から roles を文字列配列として抽出する。

    Args:
        node (dict[str, Any]): ノード定義である。

    Returns:
        list[str]: 文字列 role 名配列である。型不正時は空配列である。

    Examples:
        >>> get_node_roles({"roles": ["k8s_worker", 1]})
        ['k8s_worker']
    """
    roles_raw: Any = node.get("roles", [])
    if not isinstance(roles_raw, list):
        return []
    roles_list: list[Any] = cast(list[Any], roles_raw)
    result_roles: list[str] = []
    role_item: Any
    for role_item in roles_list:
        if isinstance(role_item, str):
            result_roles.append(role_item)
    return result_roles


def node_has_role(node: dict[str, Any], role_name: str) -> bool:
    """ノードが指定 role を持つか判定する。

    Args:
        node (dict[str, Any]): 判定対象ノードである。
        role_name (str): 判定対象 role 名である。

    Returns:
        bool: role を持つ場合は True である。

    Examples:
        >>> node_has_role({"roles": ["a", "b"]}, "b")
        True
    """
    return role_name in get_node_roles(node)


def get_node_interfaces(node: dict[str, Any]) -> list[dict[str, Any]]:
    """ノード定義から interfaces を辞書配列として抽出する。

    Args:
        node (dict[str, Any]): ノード定義である。

    Returns:
        list[dict[str, Any]]: インターフェース辞書配列である。型不正時は空配列である。

    Examples:
        >>> get_node_interfaces({"interfaces": [{"netif": "eth0"}, "x"]})
        [{'netif': 'eth0'}]
    """
    interfaces_raw: Any = node.get("interfaces", [])
    if not isinstance(interfaces_raw, list):
        return []
    interfaces_list: list[Any] = cast(list[Any], interfaces_raw)
    result_interfaces: list[dict[str, Any]] = []
    interface_item: Any
    for interface_item in interfaces_list:
        if isinstance(interface_item, dict):
            result_interfaces.append(cast(dict[str, Any], interface_item))
    return result_interfaces


def get_node_map(nodes: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """ノード名をキーにした辞書を生成する。

    Args:
        nodes (list[dict[str, Any]]): ノード定義配列である。

    Returns:
        dict[str, dict[str, Any]]: ノード名をキーにしたノード辞書である。

    Examples:
        >>> get_node_map([{"name": "n1"}, {"name": "n2"}])["n2"]["name"]
        'n2'
    """
    node_map: dict[str, dict[str, Any]] = {}
    for node in nodes:
        node_name_raw: Any = node.get("name")
        if isinstance(node_name_raw, str) and node_name_raw:
            node_map[node_name_raw] = node
    return node_map


def derive_dns_domain_for_node(
    node: dict[str, Any],
    networks: dict[str, dict[str, Any]],
    dns_domain_fallback: str | None,
    role_priority: dict[str, int],
) -> str | None:
    """ノード向け dns_domain を優先順位付きで導出する。

    Args:
        node (dict[str, Any]): 対象ノードである。
        networks (dict[str, dict[str, Any]]): ネットワーク定義マップである。
        dns_domain_fallback (str | None): 最終フォールバック値である。
        role_priority (dict[str, int]): role ごとの優先順位である。

    Returns:
        str | None: 導出したドメイン名, 未導出時は None である。

    Examples:
        >>> node = {"interfaces": [{"network": "n1"}]}
        >>> nets = {"n1": {"role": "r", "dns_search": "example.local"}}
        >>> derive_dns_domain_for_node(node, nets, None, {"r": 1})
        'example.local'
    """
    candidates: list[tuple[int, int, str]] = []

    for index, interface in enumerate(node.get('interfaces', [])):
        network_id: Any = interface.get('network')
        if not isinstance(network_id, str) or not network_id:
            continue
        network: dict[str, Any] = networks.get(network_id, {})
        role_raw: Any = network.get('role')
        if not isinstance(role_raw, str) or role_raw not in role_priority:
            continue

        dns_search_raw: Any = interface.get('dns_search')
        if not isinstance(dns_search_raw, str) or not dns_search_raw.strip():
            dns_search_raw = network.get('dns_search')
        if not isinstance(dns_search_raw, str):
            continue

        dns_search: str = dns_search_raw.strip()
        if dns_search:
            candidates.append((role_priority[role_raw], index, dns_search))

    if candidates:
        candidates.sort(key=lambda item: (item[0], item[1]))
        return candidates[0][2]

    if isinstance(dns_domain_fallback, str):
        fallback: str = dns_domain_fallback.strip()
        if fallback:
            return fallback

    return None


def get_globals_mapping(topology: dict[str, Any]) -> dict[str, Any]:
    """topology から globals マッピングを取得する。

    Args:
        topology (dict[str, Any]): トポロジー辞書である。

    Returns:
        dict[str, Any]: globals 辞書である。型不正時は空辞書である。

    Examples:
        >>> get_globals_mapping({"globals": {"a": 1}})["a"]
        1
    """
    globals_raw: Any = topology.get("globals", {})
    if not isinstance(globals_raw, dict):
        return {}
    return cast(dict[str, Any], globals_raw)


def get_globals_networks(topology: dict[str, Any]) -> dict[str, Any]:
    """topology から globals.networks マッピングを取得する。

    Args:
        topology (dict[str, Any]): トポロジー辞書である。

    Returns:
        dict[str, Any]: networks 辞書である。型不正時は空辞書である。

    Examples:
        >>> get_globals_networks({"globals": {"networks": {"n1": {}}}})["n1"]
        {}
    """
    globals_map: dict[str, Any] = get_globals_mapping(topology)
    networks_raw: Any = globals_map.get("networks", {})
    if not isinstance(networks_raw, dict):
        return {}
    return cast(dict[str, Any], networks_raw)


def get_globals_services(topology: dict[str, Any]) -> dict[str, Any]:
    """topology から globals.services マッピングを取得する。

    Args:
        topology (dict[str, Any]): トポロジー辞書である。

    Returns:
        dict[str, Any]: services 辞書である。型不正時は空辞書である。

    Examples:
        >>> get_globals_services({"globals": {"services": {"dns-server": {}}}})["dns-server"]
        {}
    """
    globals_map: dict[str, Any] = get_globals_mapping(topology)
    services_raw: Any = globals_map.get("services", {})
    if not isinstance(services_raw, dict):
        return {}
    return cast(dict[str, Any], services_raw)
