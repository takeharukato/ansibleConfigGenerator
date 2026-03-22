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
"""network_role_policy helper の単体テスト。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.genAnsibleConf.lib.network_role_policy import (
    get_role_priority,
    get_role_set,
    is_management_role,
    load_network_role_policy_from_section,
)


def _policy_path() -> Path:
    """convert-rule-config.yaml の絶対パスを返す。"""
    return Path(__file__).resolve().parents[2] / "src" / "genAnsibleConf" / "convert-rule-config.yaml"


def test_load_network_role_policy_reads_role_priority() -> None:
    """ポリシー読込で role_priority を取得できる。"""
    policy: dict[str, Any] = load_network_role_policy_from_section(
        _policy_path(),
        section_key="network_role",
    )

    priority: dict[str, int] = get_role_priority(policy)
    assert priority["private_control_plane_network"] == 0
    assert priority["external_control_plane_network"] == 1


def test_get_role_set_returns_frr_roles() -> None:
    """frr_advertise_roles を集合で返す。"""
    policy: dict[str, Any] = load_network_role_policy_from_section(
        _policy_path(),
        section_key="network_role",
    )

    frr_roles: set[str] = get_role_set(policy, "frr_advertise_roles")
    assert "bgp_transport_network" in frr_roles
    assert "data_plane_network" in frr_roles


def test_is_management_role_returns_true_for_private_role() -> None:
    """private_control_plane_network を管理 role と判定する。"""
    policy: dict[str, Any] = load_network_role_policy_from_section(
        _policy_path(),
        section_key="network_role",
    )

    assert is_management_role("private_control_plane_network", policy) is True
    assert is_management_role("data_plane_network", policy) is False
