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
"""host_vars_structured 生成で使う実行時コンテキスト構築処理を提供する。"""

from __future__ import annotations

from typing import Any, cast

from .cluster_platform import ClusterPlatform
from .node_topology_utils import get_node_map
from .service_rules import get_service_disabled_cleanup_keys
from .supply_map import build_supply_map


def prepare_service_runtime_context(
    globals_def: dict[str, Any],
    networks: dict[str, dict[str, Any]],
    internal_network_list_roles: set[str],
    active_service_settings_rules: dict[str, Any],
    nodes: list[dict[str, Any]],
) -> tuple[list[dict[str, str]], dict[str, set[str]], dict[str, list[str]], dict[str, Any]]:
    """サービス関連処理で利用する派生データを準備する。

    Args:
        globals_def (dict[str, Any]): 入力トポロジーの globals セクションである。
        networks (dict[str, dict[str, Any]]): globals.networks 定義である。
        internal_network_list_roles (set[str]): internal_network_list 対象ロール集合である。
        active_service_settings_rules (dict[str, Any]): service_settings ルールである。
        nodes (list[dict[str, Any]]): 正規化済みノード一覧である。

    Returns:
        tuple[list[dict[str, str]], dict[str, set[str]], dict[str, list[str]], dict[str, Any]]:
            internal_network_list, サービススカラー集合, 供給先マップ, globals.services である。

    Examples:
        >>> prepare_service_runtime_context({'roles': {}, 'services': {}}, {}, set(), {}, [])[2]
        {}
    """
    from .service_processing import derive_internal_network_list

    derived_internal_network_list: list[dict[str, str]] = derive_internal_network_list(
        networks,
        internal_network_list_roles,
    )

    service_disabled_cleanup_keys: dict[str, set[str]] = get_service_disabled_cleanup_keys(
        active_service_settings_rules
    )

    globals_roles: dict[str, list[str]] = cast(
        dict[str, list[str]],
        globals_def.get('roles', {}),
    )
    supply_map: dict[str, list[str]] = build_supply_map(nodes, globals_roles)
    globals_services: dict[str, Any] = globals_def.get('services', {})

    return derived_internal_network_list, service_disabled_cleanup_keys, supply_map, globals_services


def prepare_cluster_runtime_context(
    topology: dict[str, Any],
    cluster_platform: ClusterPlatform | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    """クラスタ処理で利用する正規化ノードとクラスタ所属情報を準備する。

    Args:
        topology (dict[str, Any]): network_topology v2 入力辞書である。
        cluster_platform (ClusterPlatform | None): クラスタ処理実装である。
            未指定時は Kubernetes 実装を用いる。

    Returns:
        tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
            入力ノード, 正規化ノード, ノード名マップ, クラスタ所属情報である。

    Examples:
        >>> prepare_cluster_runtime_context({'nodes': []})[0]
        []
        >>> cp = {
        ...     'name': 'cp1',
        ...     'roles': ['k8s_control_plane'],
        ...     'cluster': 'c1',
        ...     'datacenter': 'dc1',
        ...     'hostname_fqdn': 'cp1.local',
        ...     'scalars': {'k8s_cilium_cm_cluster_id': '1'},
        ... }
        >>> wk = {
        ...     'name': 'wk1',
        ...     'roles': ['k8s_worker'],
        ...     'control_plane': 'cp1',
        ...     'hostname_fqdn': 'wk1.local',
        ...     'scalars': {},
        ... }
        >>> _, nodes, node_map, membership = prepare_cluster_runtime_context({'nodes': [cp, wk]})
        >>> node_map['wk1']['cluster']
        'c1'
        >>> membership['c1']['workers']
        ['wk1']
    """
    active_cluster_platform: ClusterPlatform
    if cluster_platform is None:
        from .k8s_cluster_platform import K8sClusterPlatform

        active_cluster_platform = K8sClusterPlatform()
    else:
        active_cluster_platform = cluster_platform

    input_nodes: list[dict[str, Any]] = topology['nodes']
    raw_node_map: dict[str, dict[str, Any]] = get_node_map(input_nodes)
    nodes: list[dict[str, Any]] = active_cluster_platform.normalize_cluster_nodes(
        input_nodes,
        raw_node_map,
    )
    node_map: dict[str, dict[str, Any]] = get_node_map(nodes)
    cluster_membership: dict[str, dict[str, Any]] = active_cluster_platform.infer_cluster_membership(
        nodes,
        node_map,
    )
    return input_nodes, nodes, node_map, cluster_membership


def prepare_k8s_runtime_context(
    topology: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    """互換性のために Kubernetes 既定実装でクラスタ runtime context を準備する。

    Args:
        topology (dict[str, Any]): network_topology v2 入力辞書である。

    Returns:
        tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
            入力ノード, 正規化ノード, ノード名マップ, クラスタ所属情報である。
    """
    return prepare_cluster_runtime_context(topology)
