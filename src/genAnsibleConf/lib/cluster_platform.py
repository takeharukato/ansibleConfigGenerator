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
"""クラスタプラットフォーム抽象インターフェースを定義するモジュールである。"""

from __future__ import annotations

from typing import Any, Protocol


class ClusterPlatform(Protocol):
    """クラスタ推論と既定値生成を提供する抽象インターフェースである。"""

    def infer_cluster_membership(
        self,
        nodes: list[dict[str, Any]],
        node_map: dict[str, dict[str, Any]],
    ) -> dict[str, dict[str, Any]]:
        """ノード定義からクラスタ所属情報を導出する。"""
        ...

    def normalize_cluster_nodes(
        self,
        nodes: list[dict[str, Any]],
        node_map: dict[str, dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """クラスタノード定義を正規化する。"""
        ...

    def build_cluster_bgp_defaults(
        self,
        node: dict[str, Any],
        datacenters: dict[str, dict[str, Any]],
        cluster_membership: dict[str, dict[str, Any]],
        node_map: dict[str, dict[str, Any]],
        networks: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        """クラスタ向け BGP 既定値を生成する。"""
        ...

    def build_cluster_worker_frr_defaults(
        self,
        node: dict[str, Any],
        datacenters: dict[str, dict[str, Any]],
        node_map: dict[str, dict[str, Any]],
        networks: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        """クラスタ worker 向け FRR 既定値を生成する。"""
        ...

    def apply_cluster_worker_frr_autocalculated_fields(
        self,
        node: dict[str, Any],
        worker_frr: dict[str, Any],
        datacenters: dict[str, dict[str, Any]],
        node_map: dict[str, dict[str, Any]],
        networks: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        """クラスタ worker FRR の自動計算フィールドを補完する。"""
        ...


class ClusterRoutingCapability(Protocol):
    """DC 内 iBGP ネイバー提供を担うサブインターフェースである。"""

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
        """クラスタ所属ノードの iBGP ネイバーを追加する。"""
        ...
