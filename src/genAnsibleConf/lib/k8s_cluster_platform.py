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
"""Kubernetes 向け ClusterPlatform 実装を提供するモジュールである。"""

from __future__ import annotations

from typing import Any

from .cluster_platform import ClusterPlatform, ClusterRoutingCapability
from .k8s_neighbor import K8sNeighborProvider
from .k8s_normalize import (
    build_default_k8s_bgp,
    build_k8s_cluster_membership,
    normalize_k8s_nodes,
)
from .routing_frr import (
    apply_worker_frr_autocalculated_fields,
    build_default_k8s_worker_frr,
)


class K8sClusterPlatform(ClusterPlatform, ClusterRoutingCapability):
    """Kubernetes 固有ルールでクラスタ推論と iBGP 提供を行う実装である。"""

    def infer_cluster_membership(
        self,
        nodes: list[dict[str, Any]],
        node_map: dict[str, dict[str, Any]],
    ) -> dict[str, dict[str, Any]]:
        """Kubernetes ノード定義からクラスタ所属情報を導出する。"""
        return build_k8s_cluster_membership(nodes, node_map)

    def normalize_cluster_nodes(
        self,
        nodes: list[dict[str, Any]],
        node_map: dict[str, dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Kubernetes ノードを正規化する。"""
        return normalize_k8s_nodes(nodes, node_map)

    def build_cluster_bgp_defaults(
        self,
        node: dict[str, Any],
        datacenters: dict[str, dict[str, Any]],
        cluster_membership: dict[str, dict[str, Any]],
        node_map: dict[str, dict[str, Any]],
        networks: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        """Kubernetes 向け `k8s_bgp` 既定値を生成する。"""
        return build_default_k8s_bgp(node, datacenters, cluster_membership, node_map, networks)

    def build_cluster_worker_frr_defaults(
        self,
        node: dict[str, Any],
        datacenters: dict[str, dict[str, Any]],
        node_map: dict[str, dict[str, Any]],
        networks: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        """Kubernetes worker 向け `k8s_worker_frr` 既定値を生成する。"""
        return build_default_k8s_worker_frr(node, datacenters, node_map, networks)

    def apply_cluster_worker_frr_autocalculated_fields(
        self,
        node: dict[str, Any],
        worker_frr: dict[str, Any],
        datacenters: dict[str, dict[str, Any]],
        node_map: dict[str, dict[str, Any]],
        networks: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        """Kubernetes worker 向け `k8s_worker_frr` の自動計算項目を補完する。"""
        return apply_worker_frr_autocalculated_fields(
            node,
            worker_frr,
            datacenters,
            node_map,
            networks,
        )

    def add_cluster_ibgp_neighbors(
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
        """Kubernetes クラスタ所属ノードの iBGP ネイバーを追加する。"""
        neighbor_provider: K8sNeighborProvider = K8sNeighborProvider()
        neighbor_provider.add_ibgp_neighbors(
            target_node,
            networks,
            asn,
            cluster_id,
            cluster_name,
            ibgp_v4,
            ibgp_v6,
            role_desc,
        )
