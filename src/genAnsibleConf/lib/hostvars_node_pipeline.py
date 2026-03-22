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
"""host_vars_structured 生成で使うノード単位の組み立て処理を提供する。"""

from __future__ import annotations

from typing import Any, cast

from .cluster_platform import ClusterPlatform, ClusterRoutingCapability
from .netif_builder import (
    build_netif_list,
    derive_gateway_dns_fallback_scalars,
    derive_nic_variables,
    is_internal_mgmt_connected,
)
from .node_topology_utils import derive_dns_domain_for_node, node_has_role
from .routing_frr import (
    build_frr_ebgp_neighbors,
    build_frr_ibgp_neighbors,
    build_frr_networks,
)
from .service_processing import (
    apply_auto_service_configs,
    is_service_enabled_for_node,
    service_settings_to_scalars,
)
from .user_merge import (
    merge_users_authorized_keys,
    merge_users_list,
)


def merge_global_services_for_node(
    node: dict[str, Any],
    node_services: dict[str, Any],
    globals_services: dict[str, Any],
    supply_map: dict[str, list[str]],
) -> dict[str, Any]:
    """ノード定義サービスへ globals.services の既定値をマージする。

    Args:
        node (dict[str, Any]): 対象ノードである。
        node_services (dict[str, Any]): ノードローカルサービス設定である。
        globals_services (dict[str, Any]): グローバルサービス既定値である。
        supply_map (dict[str, list[str]]): サービス供給先マップである。

    Returns:
        dict[str, Any]: マージ後サービス設定である。

    Examples:
        >>> merge_global_services_for_node({'name': 'n1', 'services': {}}, {}, {}, {})
        {}
    """
    merged_node_services: dict[str, Any] = dict(node_services)

    for service_name in supply_map.keys():
        if service_name not in globals_services:
            continue
        node_is_supply_target: bool = (
            service_name in node.get('services', {})
            or is_service_enabled_for_node(service_name, node['name'], supply_map)
        )
        if not node_is_supply_target:
            continue
        if service_name not in merged_node_services:
            merged_node_services[service_name] = globals_services[service_name]
            continue

        global_entry: dict[str, Any] = cast(dict[str, Any], globals_services[service_name])
        node_entry: dict[str, Any] = cast(dict[str, Any], merged_node_services[service_name])
        global_config_raw: Any = global_entry.get('config', {})
        node_config_raw: Any = node_entry.get('config', {})
        if isinstance(global_config_raw, dict) and isinstance(node_config_raw, dict):
            merged_node_config: dict[str, Any] = {**global_config_raw, **node_config_raw}
            merged_node_services[service_name] = {**node_entry, 'config': merged_node_config}

    return merged_node_services


def filter_disabled_service_scalars(
    scalars: dict[str, Any],
    service_disabled_cleanup_keys: dict[str, set[str]],
    node_name: str,
    supply_map: dict[str, list[str]],
) -> None:
    """無効サービス専用スカラーを削除し, 有効サービス共有キーは保持する。

    Args:
        scalars (dict[str, Any]): ノードへ適用するスカラー辞書である。
        service_disabled_cleanup_keys (dict[str, set[str]]): サービス別スカラー集合である。
        node_name (str): 対象ノード名である。
        supply_map (dict[str, list[str]]): サービス供給先マップである。

    Examples:
        >>> data = {'x': 1}
        >>> filter_disabled_service_scalars(data, {}, 'n1', {})
        >>> data
        {'x': 1}
    """
    enabled_scoped_services: set[str] = {
        service_name
        for service_name in service_disabled_cleanup_keys
        if is_service_enabled_for_node(service_name, node_name, supply_map)
    }
    for service_name, scoped_keys in service_disabled_cleanup_keys.items():
        if service_name in enabled_scoped_services:
            continue
        for key in scoped_keys:
            key_required_by_enabled_service: bool = any(
                key in service_disabled_cleanup_keys[enabled_service_name]
                for enabled_service_name in enabled_scoped_services
            )
            if key_required_by_enabled_service:
                continue
            scalars.pop(key, None)


def initialize_node_entry_and_scalars(
    node: dict[str, Any],
    networks: dict[str, dict[str, Any]],
    internal_mgmt_role: str,
    global_scalars: dict[str, Any],
    role_priority: dict[str, int],
    dns_domain_default: str | None,
) -> tuple[dict[str, Any], dict[str, Any], bool]:
    """ノードの host_entry と初期スカラーを構築する。

    Args:
        node (dict[str, Any]): 対象ノードである。
        networks (dict[str, dict[str, Any]]): globals.networks 定義である。
        internal_mgmt_role (str): 内部管理ネットワークロール名である。
        global_scalars (dict[str, Any]): グローバルスカラー辞書である。
        role_priority (dict[str, int]): ネットワークロール優先度である。
        dns_domain_default (str | None): 既定DNSドメインである。

    Returns:
        tuple[dict[str, Any], dict[str, Any], bool]:
            host_entry, 初期化済みスカラー, 内部管理接続可否である。

    Examples:
        >>> initialize_node_entry_and_scalars(
        ...     {'hostname_fqdn': 'n1.example', 'scalars': {}},
        ...     {},
        ...     'private_control_plane_network',
        ...     {},
        ...     {},
        ...     None,
        ... )[0]['hostname']
        'n1.example'
    """
    host_entry: dict[str, Any] = {'hostname': node['hostname_fqdn']}

    node_scalars_raw: Any = node.get('scalars', {})
    node_scalars: dict[str, Any] = (
        cast(dict[str, Any], node_scalars_raw)
        if isinstance(node_scalars_raw, dict)
        else {}
    )
    scalars: dict[str, Any] = dict(node_scalars)
    internal_mgmt_connected: bool = is_internal_mgmt_connected(
        node,
        networks,
        internal_mgmt_role,
    )

    merged_scalars: dict[str, Any] = dict(global_scalars)
    merged_scalars.update(scalars)
    scalars = merged_scalars
    # internal_network_list は条件付きサービス供給でのみ設定する。
    scalars.pop('internal_network_list', None)

    if 'dns_domain' not in node_scalars:
        derived_dns_domain: str | None = derive_dns_domain_for_node(
            node,
            networks,
            dns_domain_default,
            role_priority,
        )
        if derived_dns_domain:
            scalars['dns_domain'] = derived_dns_domain

    if 'users_list' in global_scalars or 'users_list' in node_scalars:
        merged_users: list[dict[str, Any]] = merge_users_list(
            global_scalars.get('users_list', []),
            node_scalars.get('users_list', []),
        )
        if merged_users:
            scalars['users_list'] = merged_users

    if 'users_authorized_keys' in global_scalars or 'users_authorized_keys' in node_scalars:
        merged_authorized_keys: dict[str, list[str]] = merge_users_authorized_keys(
            global_scalars.get('users_authorized_keys', {}),
            node_scalars.get('users_authorized_keys', {}),
        )
        if merged_authorized_keys:
            scalars['users_authorized_keys'] = merged_authorized_keys

    if not internal_mgmt_connected:
        gpm_keys: list[str] = [key for key in scalars.keys() if key.startswith('gpm_')]
        for key in gpm_keys:
            scalars.pop(key, None)

    if 'k8s_ctrlplane_host_fqdn' in scalars:
        scalars['k8s_ctrlplane_host'] = scalars.pop('k8s_ctrlplane_host_fqdn')

    return host_entry, scalars, internal_mgmt_connected


def apply_node_network_interfaces(
    host_entry: dict[str, Any],
    scalars: dict[str, Any],
    node: dict[str, Any],
    networks: dict[str, dict[str, Any]],
    node_map: dict[str, dict[str, Any]],
    reserved_nic_pairs: list[tuple[str, str]],
    internal_mgmt_role: str,
    external_mgmt_role: str,
    data_plane_roles: set[str],
) -> None:
    """ノードの NIC 変数導出と netif_list 生成を適用する。

    Args:
        host_entry (dict[str, Any]): 出力ホストエントリである。
        scalars (dict[str, Any]): 更新対象スカラー辞書である。
        node (dict[str, Any]): 対象ノードである。
        networks (dict[str, dict[str, Any]]): globals.networks 定義である。
        node_map (dict[str, dict[str, Any]]): ノード名マップである。
        reserved_nic_pairs (list[tuple[str, str]]): 予約NICペア一覧である。
        internal_mgmt_role (str): 内部管理ロール名である。
        external_mgmt_role (str): 外部管理ロール名である。
        data_plane_roles (set[str]): データプレーンロール集合である。

    Examples:
        >>> host_entry, scalars = {}, {}
        >>> apply_node_network_interfaces(
        ...     host_entry,
        ...     scalars,
        ...     {'name': 'n1', 'interfaces': []},
        ...     {},
        ...     {},
        ...     [],
        ...     'private_control_plane_network',
        ...     'external_control_plane_network',
        ...     set(),
        ... )
    """
    nic_vars: dict[str, str] = derive_nic_variables(
        node,
        networks,
        reserved_nic_pairs,
        internal_mgmt_role,
        external_mgmt_role,
        data_plane_roles,
    )
    scalars.update(nic_vars)

    netif_list: list[dict[str, Any]] = build_netif_list(node, networks, node_map)
    if netif_list:
        host_entry['netif_list'] = netif_list
        fallback_scalars: dict[str, Any] = derive_gateway_dns_fallback_scalars(netif_list)
        if fallback_scalars:
            scalars.update(fallback_scalars)


def apply_node_routing_entries(
    host_entry: dict[str, Any],
    node: dict[str, Any],
    datacenters: dict[str, dict[str, Any]],
    cluster_membership: dict[str, dict[str, Any]],
    node_map: dict[str, dict[str, Any]],
    networks: dict[str, dict[str, Any]],
    nodes: list[dict[str, Any]],
    frr_advertise_roles: set[str],
    auto_meshed_ebgp_transport_enabled: bool,
    supply_map: dict[str, list[str]],
    cluster_platform: ClusterPlatform | None = None,
    cluster_routing_capability: ClusterRoutingCapability | None = None,
) -> None:
    """FRR と Kubernetes 関連の出力項目を host_entry へ適用する。

    Args:
        host_entry (dict[str, Any]): 出力ホストエントリである。
        node (dict[str, Any]): 対象ノードである。
        datacenters (dict[str, dict[str, Any]]): datacenter 定義である。
        cluster_membership (dict[str, dict[str, Any]]): K8sクラスタ所属情報である。
        node_map (dict[str, dict[str, Any]]): ノード名マップである。
        networks (dict[str, dict[str, Any]]): globals.networks 定義である。
        nodes (list[dict[str, Any]]): 正規化済みノード一覧である。
        frr_advertise_roles (set[str]): FRR広報対象ロール集合である。
        auto_meshed_ebgp_transport_enabled (bool): 自動eBGPトランスポート有効可否である。
        supply_map (dict[str, list[str]]): サービス供給先マップである。
        cluster_platform (ClusterPlatform | None): クラスタ処理実装である。
            未指定時は Kubernetes 実装を用いる。
        cluster_routing_capability (ClusterRoutingCapability | None):
            DC 内 iBGP ネイバー追加実装である。未指定時は cluster_platform を使う。

    Examples:
        >>> apply_node_routing_entries({}, {'name': 'n1', 'roles': []}, {}, {}, {}, {}, [], set(), True, {})
    """
    active_cluster_platform: ClusterPlatform
    if cluster_platform is None:
        from .k8s_cluster_platform import K8sClusterPlatform

        active_cluster_platform = K8sClusterPlatform()
    else:
        active_cluster_platform = cluster_platform

    active_cluster_routing_capability: ClusterRoutingCapability
    if cluster_routing_capability is None:
        active_cluster_routing_capability = cast(ClusterRoutingCapability, active_cluster_platform)
    else:
        active_cluster_routing_capability = cluster_routing_capability

    if is_service_enabled_for_node('frr_route_reflector', node['name'], supply_map):
        ebgp_v4, ebgp_v6 = build_frr_ebgp_neighbors(
            node,
            datacenters,
            node_map,
            networks,
            auto_meshed_ebgp_transport_enabled,
        )
        ibgp_v4, ibgp_v6 = build_frr_ibgp_neighbors(
            node,
            datacenters,
            cluster_membership,
            node_map,
            networks,
            cluster_routing_capability=active_cluster_routing_capability,
        )
        frr_nets_v4, frr_nets_v6 = build_frr_networks(
            node,
            datacenters,
            networks,
            nodes,
            frr_advertise_roles,
        )

        if 'frr_ebgp_neighbors' in node:
            host_entry['frr_ebgp_neighbors'] = node['frr_ebgp_neighbors']
        elif ebgp_v4:
            host_entry['frr_ebgp_neighbors'] = ebgp_v4
        if 'frr_ebgp_neighbors_v6' in node:
            host_entry['frr_ebgp_neighbors_v6'] = node['frr_ebgp_neighbors_v6']
        elif ebgp_v6:
            host_entry['frr_ebgp_neighbors_v6'] = ebgp_v6
        if ibgp_v4:
            host_entry['frr_ibgp_neighbors'] = ibgp_v4
        else:
            host_entry['frr_ibgp_neighbors'] = []
        if ibgp_v6:
            host_entry['frr_ibgp_neighbors_v6'] = ibgp_v6
        else:
            host_entry['frr_ibgp_neighbors_v6'] = []
        if frr_nets_v4:
            host_entry['frr_networks_v4'] = frr_nets_v4
        if frr_nets_v6:
            host_entry['frr_networks_v6'] = frr_nets_v6

    if node_has_role(node, 'k8s_control_plane') or node_has_role(node, 'k8s_worker'):
        _ibgp_v4, _ibgp_v6 = build_frr_ibgp_neighbors(
            node,
            datacenters,
            cluster_membership,
            node_map,
            networks,
            cluster_routing_capability=active_cluster_routing_capability,
        )

    if node_has_role(node, 'k8s_control_plane') or node_has_role(node, 'k8s_worker'):
        if 'k8s_bgp' in node:
            host_entry['k8s_bgp'] = node['k8s_bgp']
        else:
            host_entry['k8s_bgp'] = active_cluster_platform.build_cluster_bgp_defaults(
                node,
                datacenters,
                cluster_membership,
                node_map,
                networks,
            )

    if node_has_role(node, 'k8s_worker'):
        if 'k8s_worker_frr' in node:
            host_entry['k8s_worker_frr'] = active_cluster_platform.apply_cluster_worker_frr_autocalculated_fields(
                node,
                node['k8s_worker_frr'],
                datacenters,
                node_map,
                networks,
            )
        else:
            host_entry['k8s_worker_frr'] = active_cluster_platform.apply_cluster_worker_frr_autocalculated_fields(
                node,
                active_cluster_platform.build_cluster_worker_frr_defaults(
                    node,
                    datacenters,
                    node_map,
                    networks,
                ),
                datacenters,
                node_map,
                networks,
            )


def apply_node_service_scalars(
    scalars: dict[str, Any],
    node: dict[str, Any],
    globals_services: dict[str, Any],
    networks: dict[str, dict[str, Any]],
    supply_map: dict[str, list[str]],
    internal_mgmt_role: str,
    external_mgmt_role: str,
    active_service_settings_rules: dict[str, Any],
    dns_reverse_defaults: dict[str, Any],
    generate_internal_network_list: bool,
    internal_mgmt_connected: bool,
    derived_internal_network_list: list[dict[str, str]],
    service_disabled_cleanup_keys: dict[str, set[str]],
    global_scalars: dict[str, Any],
) -> None:
    """ノードのサービス設定からスカラーを導出し適用する。

    Args:
        scalars (dict[str, Any]): 更新対象スカラー辞書である。
        node (dict[str, Any]): 対象ノードである。
        globals_services (dict[str, Any]): globals.services 定義である。
        networks (dict[str, dict[str, Any]]): globals.networks 定義である。
        supply_map (dict[str, list[str]]): サービス供給先マップである。
        internal_mgmt_role (str): 内部管理ロール名である。
        external_mgmt_role (str): 外部管理ロール名である。
        active_service_settings_rules (dict[str, Any]): service_settings ルールである。
        dns_reverse_defaults (dict[str, Any]): 逆引き関連既定値である。
        generate_internal_network_list (bool): internal_network_list 自動生成可否である。
        internal_mgmt_connected (bool): 内部管理ネットワーク接続可否である。
        derived_internal_network_list (list[dict[str, str]]): 自動導出 internal_network_list である。
        service_disabled_cleanup_keys (dict[str, set[str]]): サービス別スカラー集合である。
        global_scalars (dict[str, Any]): グローバルスカラー辞書である。

    Examples:
        >>> scalars = {}
        >>> apply_node_service_scalars(
        ...     scalars,
        ...     {'name': 'n1', 'services': {}},
        ...     {},
        ...     {},
        ...     {},
        ...     'private_control_plane_network',
        ...     'external_control_plane_network',
        ...     {},
        ...     {},
        ...     False,
        ...     False,
        ...     [],
        ...     {},
        ...     {},
        ... )
    """
    node_services: dict[str, Any] = dict(node.get('services', {}))
    node_services = merge_global_services_for_node(
        node,
        node_services,
        globals_services,
        supply_map,
    )

    merged_services: dict[str, Any] = apply_auto_service_configs(
        node,
        node_services,
        networks,
        supply_map,
        internal_mgmt_role,
        external_mgmt_role,
    )

    service_scalars: dict[str, Any] = service_settings_to_scalars(
        merged_services,
        active_service_settings_rules,
    )
    if service_scalars:
        scalars.update(service_scalars)

    if is_service_enabled_for_node('nm_ddns', node['name'], supply_map):
        for key, value in dns_reverse_defaults.items():
            scalars.setdefault(key, value)

    if (
        generate_internal_network_list
        and is_service_enabled_for_node('dns-server', node['name'], supply_map)
        and internal_mgmt_connected
    ):
        internal_network_list: Any = global_scalars.get(
            'internal_network_list',
            derived_internal_network_list,
        )
        if isinstance(internal_network_list, list):
            scalars['internal_network_list'] = internal_network_list
        else:
            scalars['internal_network_list'] = derived_internal_network_list

    filter_disabled_service_scalars(
        scalars,
        service_disabled_cleanup_keys,
        node['name'],
        supply_map,
    )

    if 'ntp_servers_list' in global_scalars and 'ntp_servers_list' not in scalars:
        scalars['ntp_servers_list'] = global_scalars['ntp_servers_list']
