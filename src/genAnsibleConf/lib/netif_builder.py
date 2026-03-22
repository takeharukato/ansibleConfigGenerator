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
"""NIC 変数導出と `netif_list` 構築を提供するモジュールである。"""

from __future__ import annotations

from typing import Any

from .network_core import calculate_prefix_len
from .node_topology_utils import node_has_role


def is_internal_mgmt_connected(
    node: dict[str, Any],
    networks: dict[str, dict[str, Any]],
    internal_mgmt_role: str,
) -> bool:
    """ノードが内部管理ネットワークへ接続しているか判定する。

    Args:
        node (dict[str, Any]): 判定対象ノードである。
        networks (dict[str, dict[str, Any]]): ネットワーク定義マップである。
        internal_mgmt_role (str): 内部管理ネットワークの role 名である。

    Returns:
        bool: 接続していれば True である。

    Examples:
        >>> n = {"interfaces": [{"network": "n1"}]}
        >>> nets = {"n1": {"role": "private_control_plane_network"}}
        >>> is_internal_mgmt_connected(n, nets, "private_control_plane_network")
        True
    """
    for interface in node.get('interfaces', []):
        network_id: str | None = interface.get('network')
        if network_id is None:
            continue
        network: dict[str, Any] = networks.get(network_id, {})
        if network.get('role') == internal_mgmt_role:
            return True
    return False


def validate_reserved_nic_names(
    mgmt_nic: str,
    gpm_mgmt_nic: str | None,
    node_name: str,
    reserved_pairs: list[tuple[str, str]],
) -> None:
    """管理 NIC 名が予約ルールに従っているか検証する。

    Args:
        mgmt_nic (str): 主管理 NIC 名である。
        gpm_mgmt_nic (str | None): 2 本目の管理 NIC 名である。
        node_name (str): ノード名である。
        reserved_pairs (list[tuple[str, str]]): 許容される NIC 名ペアである。

    Raises:
        ValueError: NIC 名が予約ルールに一致しない場合に送出する。

    Examples:
        >>> validate_reserved_nic_names("eth0", None, "n1", [("eth0", "eth1")])
    """
    if gpm_mgmt_nic is not None:
        pair_valid: bool = any(
            (mgmt_nic == pair[0] and gpm_mgmt_nic == pair[1])
            for pair in reserved_pairs
        )
        if not pair_valid:
            pair_strs: str = ", ".join(f"({p[0]}, {p[1]})" for p in reserved_pairs)
            raise ValueError(
                f"Node {node_name}: dual management NIC pair ({mgmt_nic}, {gpm_mgmt_nic}) "
                f"does not match reserved pairs: {pair_strs}"
            )
    else:
        reserved_names: set[str] = {name for pair in reserved_pairs for name in pair}
        if mgmt_nic not in reserved_names:
            raise ValueError(
                f"Node {node_name}: management NIC {mgmt_nic} is not in reserved set: "
                f"{sorted(reserved_names)}"
            )


def derive_nic_variables(
    node: dict[str, Any],
    networks: dict[str, dict[str, Any]],
    reserved_pairs: list[tuple[str, str]],
    internal_mgmt_role: str,
    external_mgmt_role: str,
    data_plane_roles: set[str],
) -> dict[str, str]:
    """インターフェース定義から Ansible 用 NIC 変数を導出する。

    Args:
        node (dict[str, Any]): 対象ノードである。
        networks (dict[str, dict[str, Any]]): ネットワーク定義マップである。
        reserved_pairs (list[tuple[str, str]]): 管理 NIC の許容ペアである。
        internal_mgmt_role (str): 内部管理 role 名である。
        external_mgmt_role (str): 外部管理 role 名である。
        data_plane_roles (set[str]): データプレーン role 集合である。

    Returns:
        dict[str, str]: 導出した NIC 変数辞書である。

    Raises:
        ValueError: 管理インターフェースが見つからない場合, または予約ルール違反時に送出する。

    Examples:
        >>> node = {"name": "n1", "interfaces": [{"netif": "eth0", "network": "m"}]}
        >>> nets = {"m": {"role": "external_control_plane_network"}}
        >>> derive_nic_variables(node, nets, [("eth0", "eth1")], "private_control_plane_network", "external_control_plane_network", set())["mgmt_nic"]
        'eth0'
    """
    nic_vars: dict[str, str] = {}
    mgmt_external_netif: str | None = None
    mgmt_internal_netif: str | None = None
    k8s_netif: str | None = None

    for interface in node.get('interfaces', []):
        netif: str = interface['netif']
        network_id: str = interface['network']
        network: dict[str, Any] = networks.get(network_id, {})
        role: str = network.get('role', '')

        if role == external_mgmt_role:
            mgmt_external_netif = netif
        elif role == internal_mgmt_role:
            mgmt_internal_netif = netif
        elif role in data_plane_roles:
            node_dc: str | None = node.get('datacenter')
            node_cluster: str | None = node.get('cluster')
            if network.get('datacenter') == node_dc and network.get('cluster') == node_cluster:
                k8s_netif = netif

    if mgmt_external_netif is not None:
        nic_vars['mgmt_nic'] = mgmt_external_netif
    elif mgmt_internal_netif is not None:
        nic_vars['mgmt_nic'] = mgmt_internal_netif
    else:
        raise ValueError(f"Node {node['name']}: no management interface found")

    if mgmt_external_netif is not None and mgmt_internal_netif is not None:
        nic_vars['gpm_mgmt_nic'] = mgmt_internal_netif

    validate_reserved_nic_names(
        nic_vars['mgmt_nic'],
        nic_vars.get('gpm_mgmt_nic'),
        node['name'],
        reserved_pairs,
    )

    if node_has_role(node, 'k8s_control_plane') or node_has_role(node, 'k8s_worker'):
        if k8s_netif is not None:
            nic_vars['k8s_nic'] = k8s_netif
        nic_vars['k8s_kubelet_nic'] = nic_vars['mgmt_nic']

    return nic_vars


def resolve_gateway_from_gateway_node(
    interface: dict[str, Any],
    network: dict[str, Any],
    node_map: dict[str, dict[str, Any]],
    networks: dict[str, dict[str, Any]],
    ip_version: str,
) -> str | None:
    """`gateway_node` 設定に基づいてゲートウェイアドレスを解決する。

    Args:
        interface (dict[str, Any]): 対象インターフェースである。
        network (dict[str, Any]): 対象インターフェースのネットワーク定義である。
        node_map (dict[str, dict[str, Any]]): ノード名マップである。
        networks (dict[str, dict[str, Any]]): ネットワーク定義マップである。
        ip_version (str): `ipv4` または `ipv6` である。

    Returns:
        str | None: 解決したゲートウェイアドレス, 未解決時は None である。

    Examples:
        >>> iface = {"network": "n1"}
        >>> net = {"gateway_node": "gw", "role": "private_control_plane_network"}
        >>> gw_node = {"interfaces": [{"network": "n1", "static_ipv4_addr": "10.0.0.1"}]}
        >>> resolve_gateway_from_gateway_node(iface, net, {"gw": gw_node}, {"n1": {"role": "private_control_plane_network"}}, "ipv4")
        '10.0.0.1'
    """
    gateway_node_name: str | None = network.get('gateway_node')
    if not gateway_node_name:
        return None

    gateway_node: dict[str, Any] | None = node_map.get(gateway_node_name)
    if not gateway_node:
        return None

    network_id: str = interface['network']
    network_role: str = network.get('role', '')

    for gw_interface in gateway_node.get('interfaces', []):
        gw_network_id: str = gw_interface['network']
        gw_network: dict[str, Any] = networks.get(gw_network_id, {})

        if gw_network_id == network_id and gw_network.get('role') == network_role:
            if ip_version == 'ipv4':
                return gw_interface.get('static_ipv4_addr')
            return gw_interface.get('static_ipv6_addr')

    return None


def build_netif_list(
    node: dict[str, Any],
    networks: dict[str, dict[str, Any]],
    node_map: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """インターフェース定義から `netif_list` を生成する。

    Args:
        node (dict[str, Any]): 対象ノードである。
        networks (dict[str, dict[str, Any]]): ネットワーク定義マップである。
        node_map (dict[str, dict[str, Any]]): ノード名マップである。

    Returns:
        list[dict[str, Any]]: 生成された `netif_list` エントリ配列である。

    Examples:
        >>> node = {"interfaces": [{"netif": "eth0", "network": "n1", "static_ipv4_addr": "10.0.0.10"}]}
        >>> nets = {"n1": {"role": "external_control_plane_network", "ipv4_cidr": "10.0.0.0/24", "gateway4": "10.0.0.1"}}
        >>> build_netif_list(node, nets, {})[0]["netif"]
        'eth0'
    """
    netif_list: list[dict[str, Any]] = []

    has_mgmt_external: bool = any(
        networks.get(iface['network'], {}).get('role') == 'external_control_plane_network'
        for iface in node.get('interfaces', [])
    )

    for interface in node.get('interfaces', []):
        network_id: str = interface['network']
        network: dict[str, Any] = networks.get(network_id, {})
        role: str = network.get('role', '')

        netif_entry: dict[str, Any] = {
            'netif': interface['netif']
        }

        if 'mac' in interface:
            netif_entry['mac'] = interface['mac']

        if 'static_ipv4_addr' in interface:
            netif_entry['static_ipv4_addr'] = interface['static_ipv4_addr']
            if 'ipv4_cidr' in network:
                netif_entry['network_ipv4_prefix_len'] = calculate_prefix_len(network['ipv4_cidr'])

        if 'static_ipv6_addr' in interface:
            netif_entry['static_ipv6_addr'] = interface['static_ipv6_addr']
            if 'ipv6_cidr' in network:
                netif_entry['network_ipv6_prefix_len'] = calculate_prefix_len(network['ipv6_cidr'])

        gateway4: str | None = interface.get('gateway4')
        if gateway4 is None:
            if role == 'private_control_plane_network' and not has_mgmt_external:
                gateway4 = resolve_gateway_from_gateway_node(
                    interface,
                    network,
                    node_map,
                    networks,
                    'ipv4',
                )
            if gateway4 is None and role == 'external_control_plane_network':
                gateway4 = network.get('gateway4')
        if gateway4:
            netif_entry['gateway4'] = gateway4

        gateway6: str | None = interface.get('gateway6')
        if gateway6 is None:
            if role == 'private_control_plane_network' and not has_mgmt_external:
                gateway6 = resolve_gateway_from_gateway_node(
                    interface,
                    network,
                    node_map,
                    networks,
                    'ipv6',
                )
            if gateway6 is None and role == 'external_control_plane_network':
                gateway6 = network.get('gateway6')
        if gateway6:
            netif_entry['gateway6'] = gateway6

        dns_search: str | None = interface.get('dns_search') or network.get('dns_search')
        if dns_search:
            netif_entry['dns_search'] = dns_search

        if 'name_server_ipv4_1' in interface:
            netif_entry['name_server_ipv4_1'] = interface['name_server_ipv4_1']
        elif 'name_servers_ipv4' in network and len(network['name_servers_ipv4']) > 0:
            netif_entry['name_server_ipv4_1'] = network['name_servers_ipv4'][0]

        if 'name_server_ipv4_2' in interface:
            netif_entry['name_server_ipv4_2'] = interface['name_server_ipv4_2']
        elif 'name_servers_ipv4' in network and len(network['name_servers_ipv4']) > 1:
            netif_entry['name_server_ipv4_2'] = network['name_servers_ipv4'][1]

        if 'name_server_ipv6_1' in interface:
            netif_entry['name_server_ipv6_1'] = interface['name_server_ipv6_1']
        elif 'name_servers_ipv6' in network and len(network['name_servers_ipv6']) > 0:
            netif_entry['name_server_ipv6_1'] = network['name_servers_ipv6'][0]

        if 'name_server_ipv6_2' in interface:
            netif_entry['name_server_ipv6_2'] = interface['name_server_ipv6_2']
        elif 'name_servers_ipv6' in network and len(network['name_servers_ipv6']) > 1:
            netif_entry['name_server_ipv6_2'] = network['name_servers_ipv6'][1]

        if 'ignore_auto_ipv4_dns' in interface:
            netif_entry['ignore_auto_ipv4_dns'] = interface['ignore_auto_ipv4_dns']
        elif 'ignore_auto_ipv4_dns' in network:
            netif_entry['ignore_auto_ipv4_dns'] = network['ignore_auto_ipv4_dns']

        if 'ignore_auto_ipv6_dns' in interface:
            netif_entry['ignore_auto_ipv6_dns'] = interface['ignore_auto_ipv6_dns']
        elif 'ignore_auto_ipv6_dns' in network:
            netif_entry['ignore_auto_ipv6_dns'] = network['ignore_auto_ipv6_dns']

        if 'route_metric_ipv4' in interface:
            netif_entry['route_metric_ipv4'] = interface['route_metric_ipv4']
        elif 'route_metric_ipv4' in network:
            netif_entry['route_metric_ipv4'] = network['route_metric_ipv4']

        if 'route_metric_ipv6' in interface:
            netif_entry['route_metric_ipv6'] = interface['route_metric_ipv6']
        elif 'route_metric_ipv6' in network:
            netif_entry['route_metric_ipv6'] = network['route_metric_ipv6']

        netif_list.append(netif_entry)

    return netif_list


def derive_gateway_dns_fallback_scalars(netif_list: list[dict[str, Any]]) -> dict[str, Any]:
    """gateway 設定を持つ NIC から fallback スカラーを導出する。

    Args:
        netif_list (list[dict[str, Any]]): netif エントリ配列である。

    Returns:
        dict[str, Any]: fallback 用 gateway/DNS スカラー辞書である。

    Examples:
        >>> derive_gateway_dns_fallback_scalars([{"gateway4": "10.0.0.1", "name_server_ipv4_1": "8.8.8.8"}])["ipv4_name_server1"]
        '8.8.8.8'
    """
    source: dict[str, Any] | None = None
    for netif in netif_list:
        if 'gateway4' in netif or 'gateway6' in netif:
            source = netif
            break

    if source is None:
        return {}

    out: dict[str, Any] = {}
    direct_keys: tuple[str, ...] = ('gateway4', 'gateway6', 'dns_search')
    for key in direct_keys:
        if key in source:
            out[key] = source[key]

    mapping: dict[str, str] = {
        'name_server_ipv4_1': 'ipv4_name_server1',
        'name_server_ipv4_2': 'ipv4_name_server2',
        'name_server_ipv6_1': 'ipv6_name_server1',
        'name_server_ipv6_2': 'ipv6_name_server2',
    }
    for src_key, dst_key in mapping.items():
        if src_key in source:
            out[dst_key] = source[src_key]

    return out
