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
"""iBGP ネイバー追加処理の抽象インターフェースを定義するモジュールである。"""

from __future__ import annotations

from typing import Any, Protocol


class NeighborProvider(Protocol):
    """iBGP ネイバー追加処理を提供する抽象インターフェースである。

    実装は, クラスタ所属ノードから IPv4/IPv6 の iBGP ネイバー情報を
    既存配列へ追加する責務のみを担う。

    Examples:
        >>> class DummyProvider:
        ...     def add_ibgp_neighbors(self, target_node, networks, asn, cluster_id, cluster_name, ibgp_v4, ibgp_v6, role_desc):
        ...         ibgp_v4.append({'addr': '10.0.0.1', 'asn': asn, 'desc': role_desc})
        >>> provider = DummyProvider()
        >>> neighbors_v4 = []
        >>> provider.add_ibgp_neighbors({}, {}, 65000, 'c1', 'cluster1', neighbors_v4, [], 'worker')
        >>> neighbors_v4[0]['asn']
        65000
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
        """クラスタ所属ノードの iBGP ネイバーを追加する。"""
