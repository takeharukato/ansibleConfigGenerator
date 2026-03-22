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
"""Kubernetes ノード正規化と K8s BGP コントロールプレーン設定生成を提供するモジュールである。"""

from __future__ import annotations

from typing import Any

from .node_topology_utils import node_has_role


def normalize_cluster_id(value: Any) -> int:
    """クラスタ識別子を整数へ正規化する。

    Args:
        value (Any): 正規化対象のクラスタ識別子である。

    Returns:
        int: 正規化後のクラスタ識別子である。

    Raises:
        ValueError: 整数互換でない値が与えられた場合に送出する。

    Examples:
        >>> normalize_cluster_id(10)
        10
        >>> normalize_cluster_id("20")
        20
    """
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    raise ValueError(f"k8s_cilium_cm_cluster_id must be integer-compatible: {value}")


def build_k8s_cluster_membership(
    nodes: list[dict[str, Any]],
    node_map: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """ノード定義から Kubernetes クラスタ所属情報を導出する。

    Args:
        nodes (list[dict[str, Any]]): ノード定義配列である。
        node_map (dict[str, dict[str, Any]]): ノード名をキーにした参照マップである。

    Returns:
        dict[str, dict[str, Any]]: クラスタ ID ごとの所属情報である。

    Raises:
        ValueError: control-plane または worker の必須属性が不足している場合に送出する。

    Examples:
        >>> cp = {"name": "cp1", "roles": ["k8s_control_plane"], "cluster": "c1", "datacenter": "dc1"}
        >>> wk = {"name": "wk1", "roles": ["k8s_worker"], "control_plane": "cp1"}
        >>> result = build_k8s_cluster_membership([cp, wk], {"cp1": cp, "wk1": wk})
        >>> result["c1"]["control_plane"]
        'cp1'
    """
    membership: dict[str, dict[str, Any]] = {}

    # control-plane ノードをクラスタの起点として登録する。
    for node in nodes:
        if not node_has_role(node, 'k8s_control_plane'):
            continue
        cluster_id: str | None = node.get('cluster')
        if not cluster_id:
            raise ValueError(f"Node {node['name']}: k8s_control_plane requires cluster")
        membership[cluster_id] = {
            'control_plane': node['name'],
            'workers': [],
            'datacenter': node.get('datacenter'),
        }

    # worker ノードは control_plane 参照経由で所属クラスタを確定する。
    for node in nodes:
        if not node_has_role(node, 'k8s_worker'):
            continue
        cp_name: str | None = node.get('control_plane')
        if not cp_name:
            raise ValueError(f"Node {node['name']}: k8s_worker requires control_plane")

        cp_node: dict[str, Any] | None = node_map.get(cp_name)
        if cp_node is None or not node_has_role(cp_node, 'k8s_control_plane'):
            raise ValueError(
                f"Node {node['name']}: control_plane {cp_name} is missing or not k8s_control_plane"
            )

        cp_cluster_id: str | None = cp_node.get('cluster')
        if not cp_cluster_id:
            raise ValueError(f"Node {cp_name}: k8s_control_plane requires cluster")

        effective_cluster_id: str = node.get('cluster', cp_cluster_id)
        effective_datacenter: str | None = node.get('datacenter', cp_node.get('datacenter'))

        cluster_members: dict[str, Any] = membership.setdefault(
            effective_cluster_id,
            {
                'control_plane': cp_name,
                'workers': [],
                'datacenter': effective_datacenter,
            },
        )
        cluster_members['workers'].append(node['name'])

    return membership


def normalize_k8s_nodes(
    nodes: list[dict[str, Any]],
    node_map: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Kubernetes ノードの未指定値を補完し, 生成前に正規化する。

    Args:
        nodes (list[dict[str, Any]]): 入力ノード定義の配列である。
        node_map (dict[str, dict[str, Any]]): ノード名をキーにした参照マップである。

    Returns:
        list[dict[str, Any]]: 補完済みノード定義の配列である。

    Raises:
        ValueError: worker ノードの control_plane 参照が不正な場合に送出する。

    Examples:
        >>> cp = {"name": "cp1", "roles": ["k8s_control_plane"], "hostname_fqdn": "cp1.local", "scalars": {"k8s_cilium_cm_cluster_id": "1"}}
        >>> wk = {"name": "wk1", "roles": ["k8s_worker"], "control_plane": "cp1", "hostname_fqdn": "wk1.local", "scalars": {}}
        >>> normalized = normalize_k8s_nodes([cp, wk], {"cp1": cp, "wk1": wk})
        >>> len(normalized)
        2
    """
    keys_from_cp: tuple[str, ...] = (
        'k8s_ctrlplane_endpoint',
        'k8s_cilium_cm_cluster_name',
        'k8s_cilium_cm_cluster_id',
        'k8s_pod_ipv4_network_cidr',
        'k8s_pod_ipv6_network_cidr',
        'k8s_pod_ipv4_service_subnet',
        'k8s_pod_ipv6_service_subnet',
    )

    normalized_nodes: list[dict[str, Any]] = []

    for node in nodes:
        normalized: dict[str, Any] = dict(node)
        scalars: dict[str, Any] = dict(node.get('scalars', {}))

        if node_has_role(normalized, 'k8s_control_plane'):
            if 'k8s_cilium_cm_cluster_id' in scalars:
                scalars['k8s_cilium_cm_cluster_id'] = normalize_cluster_id(
                    scalars['k8s_cilium_cm_cluster_id']
                )
            normalized['scalars'] = scalars
            normalized_nodes.append(normalized)
            continue

        if node_has_role(normalized, 'k8s_worker'):
            cp_name: str | None = normalized.get('control_plane')
            if cp_name is None:
                raise ValueError(f"Node {normalized['name']}: k8s_worker requires control_plane")

            cp_node: dict[str, Any] | None = node_map.get(cp_name)
            if cp_node is None or not node_has_role(cp_node, 'k8s_control_plane'):
                raise ValueError(
                    f"Node {normalized['name']}: control_plane {cp_name} is missing or not k8s_control_plane"
                )

            cp_scalars: dict[str, Any] = cp_node.get('scalars', {})

            if 'datacenter' not in normalized and cp_node.get('datacenter') is not None:
                normalized['datacenter'] = cp_node['datacenter']
            if 'cluster' not in normalized and cp_node.get('cluster') is not None:
                normalized['cluster'] = cp_node['cluster']

            if 'k8s_ctrlplane_host_fqdn' not in scalars:
                scalars['k8s_ctrlplane_host_fqdn'] = cp_scalars.get(
                    'k8s_ctrlplane_host_fqdn',
                    cp_node['hostname_fqdn'],
                )

            for key in keys_from_cp:
                if key not in scalars and key in cp_scalars:
                    scalars[key] = cp_scalars[key]

            if 'k8s_cilium_cm_cluster_id' in scalars:
                scalars['k8s_cilium_cm_cluster_id'] = normalize_cluster_id(
                    scalars['k8s_cilium_cm_cluster_id']
                )

            normalized['scalars'] = scalars

        normalized_nodes.append(normalized)

    return normalized_nodes


def collect_k8s_interface_addrs(
    target_node: dict[str, Any],
    networks: dict[str, dict[str, Any]],
    datacenter_id: str | None,
    cluster_id: str | None,
) -> tuple[list[str], list[str]]:
    """ノードの Kubernetes データプレーン向け IP アドレスを収集する。

    Args:
        target_node (dict[str, Any]): 収集対象ノードである。
        networks (dict[str, dict[str, Any]]): ネットワーク定義マップである。
        datacenter_id (str | None): 収集対象のデータセンタ ID である。
        cluster_id (str | None): 収集対象のクラスタ ID である。

    Returns:
        tuple[list[str], list[str]]: IPv4 アドレス群と IPv6 アドレス群である。

    Examples:
        >>> node = {"interfaces": [{"network": "dp", "static_ipv4_addr": "10.0.0.10"}]}
        >>> nets = {"dp": {"role": "data_plane_network"}}
        >>> collect_k8s_interface_addrs(node, nets, None, None)[0]
        ['10.0.0.10']
    """
    ipv4_addrs: list[str] = []
    ipv6_addrs: list[str] = []

    for interface in target_node.get('interfaces', []):
        network: dict[str, Any] = networks.get(interface['network'], {})
        if network.get('role') != 'data_plane_network':
            continue
        if datacenter_id is not None and network.get('datacenter') != datacenter_id:
            continue
        if cluster_id is not None and network.get('cluster') != cluster_id:
            continue

        ipv4: str | None = interface.get('static_ipv4_addr')
        ipv6: str | None = interface.get('static_ipv6_addr')
        if ipv4 is not None:
            ipv4_addrs.append(ipv4)
        if ipv6 is not None:
            ipv6_addrs.append(ipv6)

    return ipv4_addrs, ipv6_addrs


def build_default_k8s_bgp(
    node: dict[str, Any],
    datacenters: dict[str, dict[str, Any]],
    cluster_membership: dict[str, dict[str, Any]],
    node_map: dict[str, dict[str, Any]],
    networks: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """`k8s_bgp` 未指定ノード向けの既定 BGP 設定を生成する。

    Args:
        node (dict[str, Any]): 対象ノードである。
        datacenters (dict[str, dict[str, Any]]): データセンタ定義マップである。
        cluster_membership (dict[str, dict[str, Any]]): クラスタ所属情報である。
        node_map (dict[str, dict[str, Any]]): ノード名マップである。
        networks (dict[str, dict[str, Any]]): ネットワーク定義マップである。

    Returns:
        dict[str, Any]: `k8s_bgp` セクションの既定値である。

    Examples:
        >>> build_default_k8s_bgp({"name": "n1", "datacenter": "dc1"}, {"dc1": {"asn": 65000}}, {}, {}, {})["local_asn"]
        65000
    """
    my_dc_id: str | None = node.get('datacenter')
    my_dc: dict[str, Any] = datacenters.get(my_dc_id, {}) if my_dc_id else {}
    my_asn: int = my_dc.get('asn', 0)

    neighbor_candidates_v4: list[str] = []
    neighbor_candidates_v6: list[str] = []

    rr_name: str | None = my_dc.get('route_reflector')
    my_cluster_id: str | None = node.get('cluster')
    if rr_name:
        rr_node: dict[str, Any] | None = node_map.get(rr_name)
        if rr_node is not None:
            rr_v4, rr_v6 = collect_k8s_interface_addrs(rr_node, networks, my_dc_id, my_cluster_id)
            neighbor_candidates_v4.extend(rr_v4)
            neighbor_candidates_v6.extend(rr_v6)

    if node_has_role(node, 'k8s_control_plane') and my_cluster_id is not None:
        members: dict[str, Any] = cluster_membership.get(my_cluster_id, {})
        for worker_name in members.get('workers', []):
            worker_node: dict[str, Any] | None = node_map.get(worker_name)
            if worker_node is None:
                continue
            worker_v4, worker_v6 = collect_k8s_interface_addrs(
                worker_node,
                networks,
                my_dc_id,
                my_cluster_id,
            )
            neighbor_candidates_v4.extend(worker_v4)
            neighbor_candidates_v6.extend(worker_v6)

    neighbors: list[dict[str, Any]] = []
    seen_peer_addresses: set[str] = set()

    for ipv4 in neighbor_candidates_v4:
        peer_address: str = f"{ipv4}/32"
        if peer_address in seen_peer_addresses:
            continue
        seen_peer_addresses.add(peer_address)
        neighbors.append({
            'peer_address': peer_address,
            'peer_asn': my_asn,
            'peer_port': 179,
            'hold_time_seconds': 90,
            'connect_retry_seconds': 15,
        })

    for ipv6 in neighbor_candidates_v6:
        peer_address = f"{ipv6}/128"
        if peer_address in seen_peer_addresses:
            continue
        seen_peer_addresses.add(peer_address)
        neighbors.append({
            'peer_address': peer_address,
            'peer_asn': my_asn,
            'peer_port': 179,
            'hold_time_seconds': 90,
            'connect_retry_seconds': 15,
        })

    return {
        'enabled': False,
        'node_name': node['name'],
        'local_asn': my_asn,
        'kubeconfig': '/etc/kubernetes/admin.conf',
        'export_pod_cidr': True,
        'advertise_services': False,
        'address_families': ['ipv4', 'ipv6'],
        'neighbors': neighbors,
    }
