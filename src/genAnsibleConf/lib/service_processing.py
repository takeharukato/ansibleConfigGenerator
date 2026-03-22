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
"""サービス設定変換と自動導出注入を提供するモジュールである。"""

from __future__ import annotations

import ipaddress
from typing import Any, cast


from .network_core import calculate_prefix_len
from .service_rules import map_service_config_to_scalars


def service_settings_to_scalars(
    merged_services: dict[str, Any],
    service_settings_rules: dict[str, Any],
) -> dict[str, Any]:
    """サービス設定を all-config 互換スカラーへ変換する。

    Args:
        merged_services (dict[str, Any]): マージ済みサービス設定である。
        service_settings_rules (dict[str, Any]): service_settings 変換ルールである。

    Returns:
        dict[str, Any]: 変換後スカラー辞書である。

    Examples:
        >>> service_settings_to_scalars({}, {})
        {}
    """
    out: dict[str, Any] = {}

    service_name: str
    service_entry_raw: Any
    for service_name, service_entry_raw in merged_services.items():
        service_entry: dict[str, Any] = (
            cast(dict[str, Any], service_entry_raw)
            if isinstance(service_entry_raw, dict)
            else {}
        )
        mapped_scalars: dict[str, Any] = map_service_config_to_scalars(
            service_name,
            service_entry,
            service_settings_rules,
        )
        if mapped_scalars:
            out.update(mapped_scalars)

    return out


def derive_radvd_auto_config(
    node: dict[str, Any],
    networks: dict[str, dict[str, Any]],
    internal_mgmt_role: str,
) -> dict[str, Any]:
    """`radvd` サービス向け自動設定を導出する。

    Args:
        node (dict[str, Any]): 対象ノードである。
        networks (dict[str, dict[str, Any]]): ネットワーク定義マップである。
        internal_mgmt_role (str): 内部管理 role 名である。

    Returns:
        dict[str, Any]: 自動導出した `radvd` 設定辞書である。

    Examples:
        >>> node = {"interfaces": [{"network": "n1"}]}
        >>> nets = {"n1": {"role": "private_control_plane_network", "ipv6_cidr": "fd00::/64"}}
        >>> derive_radvd_auto_config(node, nets, "private_control_plane_network")["radvd_router_advertisement_prefix"]
        'fd00::/64'
    """
    for interface in node.get('interfaces', []):
        network_id: str | None = interface.get('network')
        if not network_id:
            continue
        network: dict[str, Any] = networks.get(network_id, {})
        if network.get('role') != internal_mgmt_role:
            continue

        result: dict[str, Any] = {}

        ipv6_cidr: str | None = network.get('ipv6_cidr')
        if ipv6_cidr:
            result['radvd_router_advertisement_prefix'] = ipv6_cidr

        name_servers_ipv6: list[Any] = network.get('name_servers_ipv6', [])
        if name_servers_ipv6:
            result['radvd_dns_servers'] = list(name_servers_ipv6)

        dns_search: str | None = network.get('dns_search')
        if dns_search:
            result['radvd_search_domains'] = [dns_search]

        return result

    return {}


def derive_internal_router_auto_config(
    node: dict[str, Any],
    networks: dict[str, dict[str, Any]],
    internal_mgmt_role: str,
    external_mgmt_role: str,
) -> dict[str, Any]:
    """`internal_router` サービス向け自動設定を導出する。

    Args:
        node (dict[str, Any]): 対象ノードである。
        networks (dict[str, dict[str, Any]]): ネットワーク定義マップである。
        internal_mgmt_role (str): 内部管理 role 名である。
        external_mgmt_role (str): 外部管理 role 名である。

    Returns:
        dict[str, Any]: 自動導出した `internal_router` 設定辞書である。

    Examples:
        >>> node = {"interfaces": [{"network": "i"}, {"network": "e"}]}
        >>> nets = {"i": {"role": "private_control_plane_network", "ipv4_cidr": "192.168.1.0/24"}, "e": {"role": "external_control_plane_network", "ipv4_cidr": "10.0.0.0/24"}}
        >>> out = derive_internal_router_auto_config(node, nets, "private_control_plane_network", "external_control_plane_network")
        >>> out["network_ipv4_prefix_len"]
        24
    """
    private_network: dict[str, Any] | None = None
    external_network: dict[str, Any] | None = None

    for interface in node.get('interfaces', []):
        network_id: str | None = interface.get('network')
        if not network_id:
            continue
        network: dict[str, Any] = networks.get(network_id, {})
        role: str | None = network.get('role')
        if role == internal_mgmt_role and private_network is None:
            private_network = network
        elif role == external_mgmt_role and external_network is None:
            external_network = network

        if private_network is not None and external_network is not None:
            break

    result: dict[str, Any] = {}

    if private_network is not None:
        private_ipv4_cidr: str | None = private_network.get('ipv4_cidr')
        private_ipv6_cidr: str | None = private_network.get('ipv6_cidr')
        if private_ipv4_cidr:
            result['gpm_mgmt_ipv4_network_cidr'] = private_ipv4_cidr
            private_ipv4_network: ipaddress.IPv4Network | ipaddress.IPv6Network = ipaddress.ip_network(
                private_ipv4_cidr,
                strict=False,
            )
            if isinstance(private_ipv4_network, ipaddress.IPv4Network):
                octets: list[str] = str(private_ipv4_network.network_address).split('.')
                if len(octets) == 4:
                    result['gpm_mgmt_ipv4_prefix'] = '.'.join(octets[:3])
            private_gateway4: str | None = private_network.get('gateway4')
            if private_gateway4:
                result['gpm_mgmt_ipv4_network_gateway'] = private_gateway4
        if private_ipv6_cidr:
            result['gpm_mgmt_ipv6_network_cidr'] = private_ipv6_cidr

    if external_network is not None:
        external_ipv4_cidr: str | None = external_network.get('ipv4_cidr')
        external_ipv6_cidr: str | None = external_network.get('ipv6_cidr')

        if external_ipv4_cidr:
            external_ipv4_network: ipaddress.IPv4Network | ipaddress.IPv6Network = ipaddress.ip_network(
                external_ipv4_cidr,
                strict=False,
            )
            result['network_ipv4_network_address'] = str(external_ipv4_network.network_address)
            result['network_ipv4_prefix_len'] = calculate_prefix_len(external_ipv4_cidr)

        if external_ipv6_cidr:
            external_ipv6_network: ipaddress.IPv4Network | ipaddress.IPv6Network = ipaddress.ip_network(
                external_ipv6_cidr,
                strict=False,
            )
            result['network_ipv6_network_address'] = str(external_ipv6_network.network_address)
            result['network_ipv6_prefix_len'] = calculate_prefix_len(external_ipv6_cidr)

    return result


def merge_auto_config_into_service(
    merged_services: dict[str, Any],
    service_name: str,
    auto_config: dict[str, Any],
) -> dict[str, Any]:
    """自動導出設定をサービス定義へ注入する。

    Args:
        merged_services (dict[str, Any]): サービス定義辞書である。
        service_name (str): 注入対象サービス名である。
        auto_config (dict[str, Any]): 自動導出設定である。

    Returns:
        dict[str, Any]: 注入後のサービス定義辞書である。

    Examples:
        >>> merge_auto_config_into_service({"svc": {"config": {"a": 1}}}, "svc", {"b": 2})["svc"]["config"]
        {'b': 2, 'a': 1}
    """
    if not auto_config:
        return merged_services

    service_entry_raw: Any = merged_services.get(service_name, {})
    service_entry: dict[str, Any] = (
        cast(dict[str, Any], service_entry_raw)
        if isinstance(service_entry_raw, dict)
        else {}
    )
    existing_config_raw: Any = service_entry.get('config', {})
    existing_config: dict[str, Any] = (
        cast(dict[str, Any], existing_config_raw)
        if isinstance(existing_config_raw, dict)
        else {}
    )

    updated_services: dict[str, Any] = dict(merged_services)
    updated_services[service_name] = {
        **service_entry,
        'config': {**auto_config, **existing_config},
    }
    return updated_services


def is_service_enabled_for_node(
    service_name: str,
    node_name: str,
    supply_map: dict[str, list[str]],
) -> bool:
    """指定ノードでサービスが有効か判定する。

    Args:
        service_name (str): 判定対象サービス名である。
        node_name (str): ノード名である。
        supply_map (dict[str, list[str]]): サービス供給先マップである。

    Returns:
        bool: サービスが有効なら True である。

    Examples:
        >>> is_service_enabled_for_node("svc", "n1", {"svc": ["n1"]})
        True
    """
    supply_nodes: list[str] = supply_map.get(service_name, [])
    return node_name in supply_nodes


def apply_auto_service_configs(
    node: dict[str, Any],
    merged_services: dict[str, Any],
    networks: dict[str, dict[str, Any]],
    supply_map: dict[str, list[str]],
    internal_mgmt_role: str,
    external_mgmt_role: str,
) -> dict[str, Any]:
    """自動導出対象サービスの設定をまとめて注入する。

    Args:
        node (dict[str, Any]): 対象ノードである。
        merged_services (dict[str, Any]): マージ済みサービス設定である。
        networks (dict[str, dict[str, Any]]): ネットワーク定義マップである。
        supply_map (dict[str, list[str]]): サービス供給先マップである。
        internal_mgmt_role (str): 内部管理 role 名である。
        external_mgmt_role (str): 外部管理 role 名である。

    Returns:
        dict[str, Any]: 自動設定注入後のサービス辞書である。

    Examples:
        >>> apply_auto_service_configs({"name": "n1", "interfaces": []}, {}, {}, {}, "private_control_plane_network", "external_control_plane_network")
        {}
    """
    updated_services: dict[str, Any] = dict(merged_services)

    if is_service_enabled_for_node('radvd', node['name'], supply_map):
        radvd_auto_config: dict[str, Any] = derive_radvd_auto_config(
            node,
            networks,
            internal_mgmt_role,
        )
        updated_services = merge_auto_config_into_service(
            updated_services,
            'radvd',
            radvd_auto_config,
        )

    if is_service_enabled_for_node('internal_router', node['name'], supply_map):
        internal_router_auto_config: dict[str, Any] = derive_internal_router_auto_config(
            node,
            networks,
            internal_mgmt_role,
            external_mgmt_role,
        )
        updated_services = merge_auto_config_into_service(
            updated_services,
            'internal_router',
            internal_router_auto_config,
        )

    return updated_services


def derive_internal_network_list(
    networks: dict[str, dict[str, Any]],
    internal_network_list_roles: set[str],
) -> list[dict[str, str]]:
    """ネットワーク定義から `internal_network_list` を導出する。

    Args:
        networks (dict[str, dict[str, Any]]): ネットワーク定義マップである。
        internal_network_list_roles (set[str]): 抽出対象 role 名集合である。

    Returns:
        list[dict[str, str]]: `ipv4`/`ipv6` を含む内部ネットワーク定義配列である。

    Examples:
        >>> derive_internal_network_list({"n1": {"role": "r", "ipv4_cidr": "10.0.0.0/24"}}, {"r"})
        [{'ipv4': '10.0.0.0/24'}]
    """
    result: list[dict[str, str]] = []
    for _net_id, network in networks.items():
        if network.get('role') not in internal_network_list_roles:
            continue

        entry: dict[str, str] = {}
        if 'ipv4_cidr' in network:
            entry['ipv4'] = cast(str, network['ipv4_cidr'])
        if 'ipv6_cidr' in network:
            entry['ipv6'] = cast(str, network['ipv6_cidr'])

        if entry:
            result.append(entry)

    return result
