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
"""ネットワーク role 判定ポリシーの読込と検証を提供するモジュールである。"""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

from .yaml_io import load_yaml_mapping


def load_network_role_policy(path: str | Path) -> dict[str, Any]:
    """ネットワーク role 判定ポリシーを読み込む。

    Args:
        path (str | Path): ポリシーファイルのパスである。

    Returns:
        dict[str, Any]: 読み込んだポリシー辞書である。

    Raises:
        ValueError: ポリシー形式が不正な場合に送出する。

    Examples:
        >>> isinstance(load_network_role_policy_from_section("src/prototype/convert-rule-config.yaml"), dict)
        True
    """
    return load_network_role_policy_from_section(path)


def load_network_role_policy_from_section(
    path: str | Path,
    section_key: str = "network_role",
) -> dict[str, Any]:
    """統合設定ファイルから指定セクションのネットワーク role ポリシーを読み込む。

    Args:
        path (str | Path): 統合設定ファイルのパスである。
        section_key (str): 読み込むセクション名である。

    Returns:
        dict[str, Any]: 検証済みポリシー辞書である。

    Raises:
        ValueError: セクションがマッピングでない場合, または検証に失敗した場合に送出する。

    Examples:
        >>> policy = load_network_role_policy_from_section("src/prototype/convert-rule-config.yaml")
        >>> isinstance(policy, dict)
        True
    """
    root_policy: dict[str, Any] = load_yaml_mapping(path)
    section_raw: Any = root_policy.get(section_key, root_policy)
    if not isinstance(section_raw, dict):
        raise ValueError(f"network role policy: '{section_key}' must be a mapping")
    policy: dict[str, Any] = cast(dict[str, Any], section_raw)
    _validate_network_role_policy(policy)
    return policy


def get_role_priority(policy: dict[str, Any]) -> dict[str, int]:
    """role 優先順位マップを返す。

    Args:
        policy (dict[str, Any]): ネットワーク role ポリシーである。

    Returns:
        dict[str, int]: role 名から優先順位へのマップである。

    Examples:
        >>> get_role_priority({"role_priority": {"a": 1, "b": 2}})["a"]
        1
    """
    role_priority_raw: Any = policy.get("role_priority", {})
    if not isinstance(role_priority_raw, dict):
        return {}

    role_priority: dict[str, int] = {}
    role_name: Any
    priority: Any
    for role_name, priority in cast(dict[Any, Any], role_priority_raw).items():
        if isinstance(role_name, str) and isinstance(priority, int):
            role_priority[role_name] = priority

    return role_priority


def get_role_set(policy: dict[str, Any], key: str) -> set[str]:
    """指定キーから role 名集合を返す。

    Args:
        policy (dict[str, Any]): ネットワーク role ポリシーである。
        key (str): role リストを保持するキー名である。

    Returns:
        set[str]: role 名集合である。

    Examples:
        >>> sorted(get_role_set({"management_roles": ["a", "b"]}, "management_roles"))
        ['a', 'b']
    """
    roles_raw: Any = policy.get(key, [])
    if not isinstance(roles_raw, list):
        return set()

    role_names: set[str] = {
        role_name
        for role_name in cast(list[Any], roles_raw)
        if isinstance(role_name, str)
    }
    return role_names


def resolve_network_role_config(
    active_network_role_policy: dict[str, Any],
) -> tuple[dict[str, int], str, str, set[str], set[str], set[str]]:
    """network_role ポリシーから利用設定を取り出す。

    Args:
        active_network_role_policy (dict[str, Any]): network_role セクション設定である。

    Returns:
        tuple[dict[str, int], str, str, set[str], set[str], set[str]]:
            役割優先度, 内部管理ロール, 外部管理ロール,
            データプレーンロール集合, FRR広報ロール集合,
            internal_network_list 対象ロール集合である。

    Examples:
        >>> resolve_network_role_config({})[1]
        'private_control_plane_network'
    """
    role_priority: dict[str, int] = get_role_priority(active_network_role_policy)
    internal_mgmt_role_raw: Any = active_network_role_policy.get('internal_mgmt_role')
    internal_mgmt_role: str = (
        internal_mgmt_role_raw
        if isinstance(internal_mgmt_role_raw, str) and internal_mgmt_role_raw
        else 'private_control_plane_network'
    )
    external_mgmt_role_raw: Any = active_network_role_policy.get('external_mgmt_role')
    external_mgmt_role: str = (
        external_mgmt_role_raw
        if isinstance(external_mgmt_role_raw, str) and external_mgmt_role_raw
        else 'external_control_plane_network'
    )
    data_plane_roles: set[str] = get_role_set(active_network_role_policy, 'data_plane_roles')
    frr_advertise_roles: set[str] = get_role_set(active_network_role_policy, 'frr_advertise_roles')
    internal_network_list_roles: set[str] = get_role_set(
        active_network_role_policy,
        'internal_network_list_roles',
    )
    return (
        role_priority,
        internal_mgmt_role,
        external_mgmt_role,
        data_plane_roles,
        frr_advertise_roles,
        internal_network_list_roles,
    )


def is_management_role(role_name: str, policy: dict[str, Any]) -> bool:
    """role 名が管理ネットワーク role か判定する。

    Args:
        role_name (str): 判定対象 role 名である。
        policy (dict[str, Any]): ネットワーク role ポリシーである。

    Returns:
        bool: 管理 role なら True である。

    Examples:
        >>> is_management_role("mgmt", {"management_roles": ["mgmt"]})
        True
    """
    return role_name in get_role_set(policy, "management_roles")


def _validate_network_role_policy(policy: dict[str, Any]) -> None:
    """ポリシー構造を検証する。

    Args:
        policy (dict[str, Any]): 検証対象のポリシー辞書である。

    Raises:
        ValueError: 必須キーや値型が要件を満たさない場合に送出する。

    Examples:
        >>> _validate_network_role_policy({"role_priority": {}, "management_roles": [], "data_plane_roles": [], "frr_advertise_roles": [], "internal_network_list_roles": []})
    """
    role_priority_raw: Any = policy.get("role_priority", {})
    if not isinstance(role_priority_raw, dict):
        raise ValueError("network role policy: 'role_priority' must be a mapping")

    role_name: Any
    priority: Any
    for role_name, priority in cast(dict[Any, Any], role_priority_raw).items():
        if not isinstance(role_name, str) or not isinstance(priority, int):
            raise ValueError("network role policy: role_priority entries must be str->int")

    for list_key in (
        "management_roles",
        "data_plane_roles",
        "frr_advertise_roles",
        "internal_network_list_roles",
    ):
        roles_raw: Any = policy.get(list_key, [])
        if not isinstance(roles_raw, list):
            raise ValueError(f"network role policy: '{list_key}' must be a list")
        item: Any
        for item in cast(list[Any], roles_raw):
            if not isinstance(item, str):
                raise ValueError(f"network role policy: '{list_key}' items must be strings")

    for scalar_key in ("internal_mgmt_role", "external_mgmt_role"):
        scalar_raw: Any = policy.get(scalar_key)
        if scalar_raw is not None and not isinstance(scalar_raw, str):
            raise ValueError(f"network role policy: '{scalar_key}' must be a string")
