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
"""FRR 向け eBGP/iBGP ネイバーと広報ネットワーク生成, K8s worker FRR 設定生成を提供するモジュールである。"""

from __future__ import annotations

from typing import Any

from .cluster_platform import ClusterRoutingCapability
from .k8s_normalize import collect_k8s_interface_addrs
from .node_topology_utils import node_has_role


def build_frr_ebgp_neighbors(
    node: dict[str, Any],
    datacenters: dict[str, dict[str, Any]],
    node_map: dict[str, dict[str, Any]],
    networks: dict[str, dict[str, Any]],
    auto_meshed_ebgp_transport_enabled: bool,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """データセンタ間 eBGP ネイバーを生成する。

    Args:
        node (dict[str, Any]): 生成対象ノードである。
        datacenters (dict[str, dict[str, Any]]): データセンタ定義マップである。
        node_map (dict[str, dict[str, Any]]): ノード名マップである。
        networks (dict[str, dict[str, Any]]): ネットワーク定義マップである。
        auto_meshed_ebgp_transport_enabled (bool): eBGP 自動メッシュを有効にするフラグである。

    Returns:
        tuple[list[dict[str, Any]], list[dict[str, Any]]]: IPv4/IPv6 の eBGP ネイバー配列である。

    Examples:
        >>> build_frr_ebgp_neighbors({"name": "n1"}, {}, {}, {}, False)
        ([], [])
    """
    ebgp_v4: list[dict[str, Any]] = []
    ebgp_v6: list[dict[str, Any]] = []

    if not auto_meshed_ebgp_transport_enabled:
        return ebgp_v4, ebgp_v6

    my_dc_id: str | None = node.get('datacenter')
    if not my_dc_id:
        return ebgp_v4, ebgp_v6

    my_dc: dict[str, Any] = datacenters.get(my_dc_id, {})
    if my_dc.get('route_reflector') != node['name']:
        return ebgp_v4, ebgp_v6

    for dc_id, dc in datacenters.items():
        if dc_id == my_dc_id:
            continue

        rr_name: str | None = dc.get('route_reflector')
        if not rr_name:
            continue

        rr_node: dict[str, Any] | None = node_map.get(rr_name)
        if not rr_node:
            continue

        peer_asn: int = dc.get('asn', 0)

        for interface in rr_node.get('interfaces', []):
            network_id: str = interface['network']
            network: dict[str, Any] = networks.get(network_id, {})

            if network.get('role') == 'bgp_transport_network':
                if 'static_ipv4_addr' in interface:
                    ebgp_v4.append({
                        'addr': interface['static_ipv4_addr'],
                        'asn': peer_asn,
                        'desc': f"AS Number: {peer_asn} - {rr_node['name']}",
                    })

                if 'static_ipv6_addr' in interface:
                    ebgp_v6.append({
                        'addr': interface['static_ipv6_addr'],
                        'asn': peer_asn,
                        'desc': f"AS Number: {peer_asn} - {rr_node['name']}",
                    })

    return ebgp_v4, ebgp_v6


def build_frr_ibgp_neighbors(
    node: dict[str, Any],
    datacenters: dict[str, dict[str, Any]],
    cluster_membership: dict[str, dict[str, Any]],
    node_map: dict[str, dict[str, Any]],
    networks: dict[str, dict[str, Any]],
    cluster_routing_capability: ClusterRoutingCapability | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """データセンタ内 iBGP ネイバーを生成する。

    Args:
        node (dict[str, Any]): 生成対象ノードである。
        datacenters (dict[str, dict[str, Any]]): データセンタ定義マップである。
        cluster_membership (dict[str, dict[str, Any]]): クラスタ所属情報である。
        node_map (dict[str, dict[str, Any]]): ノード名マップである。
        networks (dict[str, dict[str, Any]]): ネットワーク定義マップである。
        cluster_routing_capability (ClusterRoutingCapability | None):
            DC 内 iBGP ネイバー追加実装である。未指定時は Kubernetes 実装を使う。

    Returns:
        tuple[list[dict[str, Any]], list[dict[str, Any]]]: IPv4/IPv6 の iBGP ネイバー配列である。

    Examples:
        >>> build_frr_ibgp_neighbors({"name": "n1"}, {}, {}, {}, {})
        ([], [])
    """
    ibgp_v4: list[dict[str, Any]] = []
    ibgp_v6: list[dict[str, Any]] = []

    active_cluster_routing_capability: ClusterRoutingCapability
    if cluster_routing_capability is None:
        from .k8s_cluster_platform import K8sClusterPlatform

        active_cluster_routing_capability = K8sClusterPlatform()
    else:
        active_cluster_routing_capability = cluster_routing_capability

    my_dc_id: str | None = node.get('datacenter')
    if not my_dc_id:
        return ibgp_v4, ibgp_v6

    my_dc: dict[str, Any] = datacenters.get(my_dc_id, {})
    my_asn: int = my_dc.get('asn', 0)

    if my_dc.get('route_reflector') == node['name']:
        for cluster_id, members in cluster_membership.items():
            cp_name: str | None = members.get('control_plane')
            if not cp_name:
                continue
            cp_node: dict[str, Any] | None = node_map.get(cp_name)
            if cp_node is None or cp_node.get('datacenter') != my_dc_id:
                continue

            cp_scalars: dict[str, Any] = cp_node.get('scalars', {})
            cluster_name: str = cp_scalars.get('k8s_cilium_cm_cluster_name', cluster_id)

            if cp_name and cp_node:
                active_cluster_routing_capability.add_cluster_ibgp_neighbors(
                    cp_node,
                    networks,
                    my_asn,
                    cluster_id,
                    cluster_name,
                    ibgp_v4,
                    ibgp_v6,
                    'control-plane',
                )

            for worker_name in members.get('workers', []):
                worker_node: dict[str, Any] | None = node_map.get(worker_name)
                if worker_node:
                    active_cluster_routing_capability.add_cluster_ibgp_neighbors(
                        worker_node,
                        networks,
                        my_asn,
                        cluster_id,
                        cluster_name,
                        ibgp_v4,
                        ibgp_v6,
                        'worker',
                    )

    elif node_has_role(node, 'k8s_control_plane') or node_has_role(node, 'k8s_worker'):
        rr_name: str | None = my_dc.get('route_reflector')
        if rr_name:
            rr_node: dict[str, Any] | None = node_map.get(rr_name)
            if rr_node:
                for interface in rr_node.get('interfaces', []):
                    network_id: str = interface['network']
                    network: dict[str, Any] = networks.get(network_id, {})

                    if (
                        network.get('role') == 'data_plane_network'
                        and network.get('datacenter') == my_dc_id
                        and network.get('cluster') == node.get('cluster')
                    ):
                        if 'static_ipv4_addr' in interface:
                            ibgp_v4.append({
                                'addr': interface['static_ipv4_addr'],
                                'asn': my_asn,
                                'desc': f"DC RR ({rr_node['hostname_fqdn']})",
                            })

                        if 'static_ipv6_addr' in interface:
                            ibgp_v6.append({
                                'addr': interface['static_ipv6_addr'],
                                'asn': my_asn,
                                'desc': f"DC RR ({rr_node['hostname_fqdn']})",
                            })

    return ibgp_v4, ibgp_v6


def build_frr_networks(
    node: dict[str, Any],
    datacenters: dict[str, dict[str, Any]],
    networks: dict[str, dict[str, Any]],
    nodes: list[dict[str, Any]],
    frr_advertise_roles: set[str],
) -> tuple[list[str], list[str]]:
    """FRR で広報するネットワークリストを生成する。

    Args:
        node (dict[str, Any]): 生成対象ノードである。
        datacenters (dict[str, dict[str, Any]]): データセンタ定義マップである。
        networks (dict[str, dict[str, Any]]): ネットワーク定義マップである。
        nodes (list[dict[str, Any]]): 全ノード定義配列である。
        frr_advertise_roles (set[str]): 広報対象 role 名集合である。

    Returns:
        tuple[list[str], list[str]]: IPv4/IPv6 の広報 CIDR 配列である。

    Examples:
        >>> build_frr_networks({"name": "n1"}, {}, {}, [], set())
        ([], [])
    """
    frr_nets_v4: list[str] = []
    frr_nets_v6: list[str] = []

    my_dc_id: str | None = node.get('datacenter')
    if not my_dc_id:
        return frr_nets_v4, frr_nets_v6

    my_dc: dict[str, Any] = datacenters.get(my_dc_id, {})

    if my_dc.get('route_reflector') != node['name']:
        return frr_nets_v4, frr_nets_v6

    selected_network_ids: set[str] = set()

    for target_node in nodes:
        if target_node.get('datacenter') != my_dc_id:
            continue
        for interface in target_node.get('interfaces', []):
            network_id: str = interface.get('network', '')
            network: dict[str, Any] = networks.get(network_id, {})
            if network.get('role') in frr_advertise_roles:
                selected_network_ids.add(network_id)

    for net_id in sorted(selected_network_ids):
        network = networks.get(net_id, {})
        if 'ipv4_cidr' in network:
            frr_nets_v4.append(network['ipv4_cidr'])
        if 'ipv6_cidr' in network:
            frr_nets_v6.append(network['ipv6_cidr'])

    return frr_nets_v4, frr_nets_v6


def build_default_k8s_worker_frr(
    node: dict[str, Any],
    datacenters: dict[str, dict[str, Any]],
    node_map: dict[str, dict[str, Any]],
    networks: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """`k8s_worker_frr` 未指定 worker ノード向け既定値を生成する。

    Args:
        node (dict[str, Any]): 対象ノードである。
        datacenters (dict[str, dict[str, Any]]): データセンタ定義マップである。
        node_map (dict[str, dict[str, Any]]): ノード名マップである。
        networks (dict[str, dict[str, Any]]): ネットワーク定義マップである。

    Returns:
        dict[str, Any]: `k8s_worker_frr` の既定設定である。

    Examples:
        >>> build_default_k8s_worker_frr({"datacenter": "dc1", "interfaces": [], "scalars": {}}, {"dc1": {"asn": 65000}}, {}, {})["local_asn"]
        65000
    """
    my_dc_id: str | None = node.get('datacenter')
    my_dc: dict[str, Any] = datacenters.get(my_dc_id, {}) if my_dc_id else {}
    my_asn: int = my_dc.get('asn', 0)

    worker_frr: dict[str, Any] = {
        'enabled': True,
        'local_asn': my_asn,
        'rfc5549_enabled': False,
        'ipv4_transport_ipv6_nlri_enabled': False,
    }

    scalars: dict[str, Any] = node.get('scalars', {})
    cluster_id: str | None = node.get('cluster')
    if cluster_id is not None:
        cluster_name: str = scalars.get('k8s_cilium_cm_cluster_name', cluster_id)
        worker_frr['cluster_name'] = cluster_name

        clusters_entry: dict[str, Any] = {cluster_name: {}}
        if 'k8s_pod_ipv4_network_cidr' in scalars and 'k8s_pod_ipv4_service_subnet' in scalars:
            clusters_entry[cluster_name]['pod_cidrs_v4'] = [scalars['k8s_pod_ipv4_network_cidr']]
            clusters_entry[cluster_name]['service_cidrs_v4'] = [scalars['k8s_pod_ipv4_service_subnet']]
        if 'k8s_pod_ipv6_network_cidr' in scalars and 'k8s_pod_ipv6_service_subnet' in scalars:
            clusters_entry[cluster_name]['pod_cidrs_v6'] = [scalars['k8s_pod_ipv6_network_cidr']]
            clusters_entry[cluster_name]['service_cidrs_v6'] = [scalars['k8s_pod_ipv6_service_subnet']]
        if clusters_entry[cluster_name]:
            worker_frr['clusters'] = clusters_entry

    rr_name: str | None = my_dc.get('route_reflector')
    my_cluster_id: str | None = node.get('cluster')
    if rr_name is not None:
        rr_node: dict[str, Any] | None = node_map.get(rr_name)
        if rr_node is not None:
            rr_hostname: str = rr_node['hostname_fqdn']
            rr_v4, rr_v6 = collect_k8s_interface_addrs(rr_node, networks, my_dc_id, my_cluster_id)
            if rr_v4:
                worker_frr['dc_frr_addresses'] = {rr_hostname: rr_v4[0]}
            if rr_v6:
                worker_frr['dc_frr_addresses_v6'] = {rr_hostname: rr_v6[0]}

    node_k8s_v4, node_k8s_v6 = collect_k8s_interface_addrs(node, networks, my_dc_id, my_cluster_id)
    if node_k8s_v4:
        worker_frr['advertise_host_route_ipv4'] = f"{node_k8s_v4[0]}/32"
    if node_k8s_v6:
        worker_frr['advertise_host_route_ipv6'] = f"{node_k8s_v6[0]}/128"

    for interface in node.get('interfaces', []):
        ipv4_addr: str | None = interface.get('static_ipv4_addr')
        if ipv4_addr is not None:
            worker_frr['router_id'] = ipv4_addr
            break

    worker_frr['prefix_filter'] = {
        'ipv4': {
            'pod_min_length': 24,
            'pod_max_length': 28,
            'service_min_length': 16,
            'service_max_length': 24,
        },
        'ipv6': {
            'pod_min_length': 56,
            'pod_max_length': 64,
            'service_min_length': 112,
            'service_max_length': 120,
        },
    }

    return worker_frr


def apply_worker_frr_autocalculated_fields(
    node: dict[str, Any],
    worker_frr: dict[str, Any],
    datacenters: dict[str, dict[str, Any]],
    node_map: dict[str, dict[str, Any]],
    networks: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """`k8s_worker_frr` に自動計算項目を不足分のみ補完する。

    Args:
        node (dict[str, Any]): 対象ノードである。
        worker_frr (dict[str, Any]): 入力された `k8s_worker_frr` 設定である。
        datacenters (dict[str, dict[str, Any]]): データセンタ定義マップである。
        node_map (dict[str, dict[str, Any]]): ノード名マップである。
        networks (dict[str, dict[str, Any]]): ネットワーク定義マップである。

    Returns:
        dict[str, Any]: 補完後の `k8s_worker_frr` 設定である。

    Examples:
        >>> apply_worker_frr_autocalculated_fields({"interfaces": [], "scalars": {}}, {}, {}, {}, {})
        {'cluster_name': None}
    """
    merged: dict[str, Any] = dict(worker_frr)

    my_dc_id: str | None = node.get('datacenter')
    my_dc: dict[str, Any] = datacenters.get(my_dc_id, {}) if my_dc_id else {}

    rr_name: str | None = my_dc.get('route_reflector')
    my_cluster_id: str | None = node.get('cluster')
    if rr_name is not None:
        rr_node: dict[str, Any] | None = node_map.get(rr_name)
        if rr_node is not None:
            rr_hostname: str = rr_node['hostname_fqdn']
            rr_v4, rr_v6 = collect_k8s_interface_addrs(rr_node, networks, my_dc_id, my_cluster_id)
            if rr_v4 and 'dc_frr_addresses' not in merged:
                merged['dc_frr_addresses'] = {rr_hostname: rr_v4[0]}
            if rr_v6 and 'dc_frr_addresses_v6' not in merged:
                merged['dc_frr_addresses_v6'] = {rr_hostname: rr_v6[0]}

    node_k8s_v4, node_k8s_v6 = collect_k8s_interface_addrs(node, networks, my_dc_id, my_cluster_id)
    if node_k8s_v4 and 'advertise_host_route_ipv4' not in merged:
        merged['advertise_host_route_ipv4'] = f"{node_k8s_v4[0]}/32"
    if node_k8s_v6 and 'advertise_host_route_ipv6' not in merged:
        merged['advertise_host_route_ipv6'] = f"{node_k8s_v6[0]}/128"

    if 'router_id' not in merged:
        for interface in node.get('interfaces', []):
            ipv4_addr: str | None = interface.get('static_ipv4_addr')
            if ipv4_addr is not None:
                merged['router_id'] = ipv4_addr
                break

    if 'cluster_name' not in merged:
        cluster_id: str | None = node.get('cluster')
        merged['cluster_name'] = node.get('scalars', {}).get('k8s_cilium_cm_cluster_name', cluster_id)

    if 'clusters' not in merged:
        cluster_name: str | None = merged.get('cluster_name')
        scalars: dict[str, Any] = node.get('scalars', {})
        cluster_entry: dict[str, Any] = {}
        if 'k8s_pod_ipv4_network_cidr' in scalars and 'k8s_pod_ipv4_service_subnet' in scalars:
            cluster_entry['pod_cidrs_v4'] = [scalars['k8s_pod_ipv4_network_cidr']]
            cluster_entry['service_cidrs_v4'] = [scalars['k8s_pod_ipv4_service_subnet']]
        if 'k8s_pod_ipv6_network_cidr' in scalars and 'k8s_pod_ipv6_service_subnet' in scalars:
            cluster_entry['pod_cidrs_v6'] = [scalars['k8s_pod_ipv6_network_cidr']]
            cluster_entry['service_cidrs_v6'] = [scalars['k8s_pod_ipv6_service_subnet']]
        if cluster_name and cluster_entry:
            merged['clusters'] = {cluster_name: cluster_entry}

    return merged


def prepare_frr_runtime_flags(globals_def: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], bool]:
    """FRR 処理で利用する datacenter 定義と実行フラグを準備する。

    Args:
        globals_def (dict[str, Any]): 入力トポロジーの globals セクションである。

    Returns:
        tuple[dict[str, dict[str, Any]], bool]: datacenters と自動eBGPフラグである。

    Examples:
        >>> prepare_frr_runtime_flags({'datacenters': {}})
        ({}, True)
    """
    datacenters: dict[str, dict[str, Any]] = globals_def['datacenters']
    auto_meshed_ebgp_transport_enabled: bool = bool(
        globals_def.get('auto_meshed_ebgp_transport_enabled', True)
    )
    return datacenters, auto_meshed_ebgp_transport_enabled
