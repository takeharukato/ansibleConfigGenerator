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
"""k8s_cluster_platform の単体テスト。"""

from __future__ import annotations

from typing import Any

from src.genAnsibleConf.lib.k8s_cluster_platform import K8sClusterPlatform


def test_infer_cluster_membership_and_normalize_nodes_for_k8s() -> None:
    """K8s 実装で cluster 推論とノード正規化が行えることを検証する。"""
    platform: K8sClusterPlatform = K8sClusterPlatform()

    cp: dict[str, Any] = {
        "name": "cp1",
        "roles": ["k8s_control_plane"],
        "cluster": "c1",
        "datacenter": "dc1",
        "hostname_fqdn": "cp1.local",
        "scalars": {"k8s_cilium_cm_cluster_id": "1"},
    }
    wk: dict[str, Any] = {
        "name": "wk1",
        "roles": ["k8s_worker"],
        "control_plane": "cp1",
        "hostname_fqdn": "wk1.local",
        "scalars": {},
    }

    normalized_nodes: list[dict[str, Any]] = platform.normalize_cluster_nodes(
        [cp, wk],
        {"cp1": cp, "wk1": wk},
    )
    normalized_map: dict[str, dict[str, Any]] = {
        node["name"]: node for node in normalized_nodes
    }
    membership: dict[str, dict[str, Any]] = platform.infer_cluster_membership(
        normalized_nodes,
        normalized_map,
    )

    assert normalized_map["wk1"]["cluster"] == "c1"
    assert membership["c1"]["control_plane"] == "cp1"
    assert membership["c1"]["workers"] == ["wk1"]


def test_add_cluster_ibgp_neighbors_adds_k8s_data_plane_peers() -> None:
    """ClusterRoutingCapability 実装として K8s iBGP ネイバーを追加できることを検証する。"""
    platform: K8sClusterPlatform = K8sClusterPlatform()

    target_node: dict[str, Any] = {
        "name": "wk1",
        "hostname_fqdn": "wk1.local",
        "datacenter": "dc1",
        "interfaces": [
            {
                "network": "dp1",
                "static_ipv4_addr": "10.10.0.20",
                "static_ipv6_addr": "fd10::20",
            }
        ],
    }
    networks: dict[str, dict[str, Any]] = {
        "dp1": {"role": "data_plane_network", "datacenter": "dc1", "cluster": "c1"}
    }
    ibgp_v4: list[dict[str, Any]] = []
    ibgp_v6: list[dict[str, Any]] = []

    platform.add_cluster_ibgp_neighbors(
        target_node,
        networks,
        65100,
        "c1",
        "cluster1",
        ibgp_v4,
        ibgp_v6,
        "worker",
    )

    assert ibgp_v4 == [{"addr": "10.10.0.20", "asn": 65100, "desc": "ID:c1 cluster1 wk1.local"}]
    assert ibgp_v6 == [{"addr": "fd10::20", "asn": 65100, "desc": "ID:c1 cluster1 wk1.local"}]