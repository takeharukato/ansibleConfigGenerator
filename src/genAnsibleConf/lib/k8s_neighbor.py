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
"""Kubernetes クラスタ向け iBGP ネイバー追加実装を提供するモジュールである。"""

from __future__ import annotations

from typing import Any

from .neighbor_provider import NeighborProvider


def _add_ibgp_k8s_cluster_neighbors(
    target_node: dict[str, Any],
    networks: dict[str, dict[str, Any]],
    asn: int,
    cluster_id: str,
    cluster_name: str,
    ibgp_v4: list[dict[str, Any]],
    ibgp_v6: list[dict[str, Any]],
    role_desc: str,
) -> None:
    """Kubernetes クラスタ所属ノードの iBGP ネイバーを追加する内部 helper である。

    Args:
        target_node (dict[str, Any]): 追加対象ノードである。
        networks (dict[str, dict[str, Any]]): ネットワーク定義マップである。
        asn (int): 付与する ASN である。
        cluster_id (str): クラスタ識別子である。
        cluster_name (str): クラスタ表示名である。
        ibgp_v4 (list[dict[str, Any]]): IPv4 ネイバー追加先配列である。
        ibgp_v6 (list[dict[str, Any]]): IPv6 ネイバー追加先配列である。
        role_desc (str): 呼び出し元役割である。

    Examples:
        >>> v4, v6 = [], []
        >>> node = {'hostname_fqdn': 'n.local', 'datacenter': 'dc1', 'interfaces': []}
        >>> _add_ibgp_k8s_cluster_neighbors(node, {}, 65000, 'c1', 'cluster1', v4, v6, 'worker')
        >>> len(v4)
        0
    """
    del role_desc

    for interface in target_node.get('interfaces', []):
        network_id: str = interface['network']
        network: dict[str, Any] = networks.get(network_id, {})

        if (
            network.get('role') == 'data_plane_network'
            and network.get('datacenter') == target_node.get('datacenter')
            and network.get('cluster') == cluster_id
        ):
            target_hostname: str = target_node['hostname_fqdn']
            if 'static_ipv4_addr' in interface:
                ibgp_v4.append({
                    'addr': interface['static_ipv4_addr'],
                    'asn': asn,
                    'desc': f"ID:{cluster_id} {cluster_name} {target_hostname}",
                })

            if 'static_ipv6_addr' in interface:
                ibgp_v6.append({
                    'addr': interface['static_ipv6_addr'],
                    'asn': asn,
                    'desc': f"ID:{cluster_id} {cluster_name} {target_hostname}",
                })


class K8sNeighborProvider(NeighborProvider):
    """Kubernetes クラスタ所属ノードから iBGP ネイバーを追加する実装である。

    Examples:
        >>> provider = K8sNeighborProvider()
        >>> v4, v6 = [], []
        >>> provider.add_ibgp_neighbors({}, {}, 65000, 'c1', 'cluster1', v4, v6, 'worker')
        >>> v4
        []
    """

    def add_ibgp_neighbors(
        self,
        target_node: dict[str, Any],
        networks: dict[str, dict[str, Any]],
        asn: int,
        cluster_id: str,
        cluster_name: str,
        ibgp_v4: list[dict[str, Any]],
        ibgp_v6: list[dict[str, Any]],
        role_desc: str,
    ) -> None:
        """Kubernetes クラスタ所属ノードから iBGP ネイバーを追加する。

        Args:
            target_node (dict[str, Any]): 追加対象ノードである。
            networks (dict[str, dict[str, Any]]): ネットワーク定義マップである。
            asn (int): 付与する ASN である。
            cluster_id (str): クラスタ識別子である。
            cluster_name (str): クラスタ表示名である。
            ibgp_v4 (list[dict[str, Any]]): IPv4 ネイバー追加先配列である。
            ibgp_v6 (list[dict[str, Any]]): IPv6 ネイバー追加先配列である。
            role_desc (str): 呼び出し元役割である。

        Examples:
            >>> provider = K8sNeighborProvider()
            >>> v4, v6 = [], []
            >>> provider.add_ibgp_neighbors({}, {}, 65000, 'c1', 'cluster1', v4, v6, 'worker')
            >>> len(v4)
            0
        """
        _add_ibgp_k8s_cluster_neighbors(
            target_node,
            networks,
            asn,
            cluster_id,
            cluster_name,
            ibgp_v4,
            ibgp_v6,
            role_desc,
        )
