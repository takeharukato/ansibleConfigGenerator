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
"""k8s_normalize の単体テスト。"""

from __future__ import annotations

from typing import Any

import pytest

from src.genAnsibleConf.lib.hostvars_runtime_context import prepare_k8s_runtime_context
from src.genAnsibleConf.lib.k8s_normalize import normalize_cluster_id


def test_normalize_cluster_id_accepts_numeric_string() -> None:
    """数値文字列を整数へ変換できることを検証する。"""
    assert normalize_cluster_id("42") == 42


def test_normalize_cluster_id_rejects_non_numeric_string() -> None:
    """整数互換でない文字列を拒否することを検証する。"""
    with pytest.raises(ValueError):
        normalize_cluster_id("cluster-a")


def test_prepare_k8s_runtime_context_fills_worker_cluster_from_cp() -> None:
    """worker の cluster/datacenter 補完と membership 生成を検証する。"""
    control_plane: dict[str, Any] = {
        "name": "cp1",
        "roles": ["k8s_control_plane"],
        "cluster": "c1",
        "datacenter": "dc1",
        "hostname_fqdn": "cp1.local",
        "scalars": {"k8s_cilium_cm_cluster_id": "1"},
    }
    worker: dict[str, Any] = {
        "name": "wk1",
        "roles": ["k8s_worker"],
        "control_plane": "cp1",
        "hostname_fqdn": "wk1.local",
        "scalars": {},
    }

    _, normalized_nodes, normalized_node_map, membership = prepare_k8s_runtime_context(
        {"nodes": [control_plane, worker]}
    )

    assert len(normalized_nodes) == 2
    assert normalized_node_map["wk1"]["cluster"] == "c1"
    assert normalized_node_map["wk1"]["datacenter"] == "dc1"
    assert membership["c1"]["control_plane"] == "cp1"
    assert membership["c1"]["workers"] == ["wk1"]
