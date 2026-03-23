#!/usr/bin/env python3
# -*- mode: python; coding: utf-8; line-endings: unix -*-
# SPDX-License-Identifier: BSD-2-Clause
#
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

"""network_topology.v2.yaml から host_vars_structured.yaml を生成するオーケストレータ。

このスクリプトは, データセンタ中心のネットワークトポロジー定義から
ansible-linux-setup用のhost_vars_structured.yamlを生成する。
詳細な変換ロジックは lib/ 配下の責務別モジュールに委譲しており,
本スクリプトはオーケストレーションとYAML出力CLIのみを担う。

委譲先サブモジュール:
- lib.network_core      : プレフィックス長計算・K8sクラスタ所属情報の導出
- lib.user_merge        : users関連マージ・DNSドメイン/GWフォールバックスカラー導出
- lib.netif_builder     : NIC変数導出・予約NIC名検証・netif_list生成
- lib.k8s_normalize     : K8sノード正規化・既定BGP/Worker FRR設定生成
- lib.service_processing: サービス変換・auto config注入・internal_network_list導出
- lib.routing_frr       : eBGP/iBGPネイバー生成・FRR広報ネットワーク生成

本スクリプトの責務:
- 各サブモジュールの呼び出し順序制御と結果の組み立て
- ルール設定ファイル読み込み (service_transform, service_settings, network_role)
- host_vars_structured形式の最終ホストエントリ構築とYAML出力CLI提供
"""

import argparse
import sys
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from genAnsibleConf.lib.cli_defaults import (
    DEFAULT_CONVERT_RULE_CONFIG,
    DEFAULT_HOST_VARS_STRUCTURED,
    DEFAULT_NETWORK_TOPOLOGY,
    resolve_schema_file,
)
from genAnsibleConf.lib.hostvars_node_pipeline import (
    apply_node_network_interfaces,
    apply_node_routing_entries,
    apply_node_service_scalars,
    initialize_node_entry_and_scalars,
)
from genAnsibleConf.lib.hostvars_runtime_context import (
    prepare_cluster_runtime_context,
    prepare_service_runtime_context,
)
from genAnsibleConf.lib.network_role_policy import (
    load_network_role_policy_from_section,
    resolve_network_role_config,
)
from genAnsibleConf.lib.global_params import (
    build_global_scalars,
    collect_dns_defaults,
    prepare_netif_reserved_pairs,
)
from genAnsibleConf.lib.routing_frr import prepare_frr_runtime_flags
from genAnsibleConf.lib.service_rules import load_service_transform_rules_from_section
from genAnsibleConf.lib.yaml_io import load_yaml_mapping, write_yaml_file


def generate_host_vars_structured(
    topology: dict[str, Any],
    schema_dir: str | None = None,
) -> dict[str, Any]:
    """network_topology v2からhost_vars_structuredを生成する。

    Args:
        topology (dict[str, Any]): network_topology v2形式の入力

    Returns:
        dict[str, Any]: host_vars_structured形式の出力
    """
    convert_rule_config_path: Path = resolve_schema_file(
        DEFAULT_CONVERT_RULE_CONFIG,
        schema_dir,
    )
    active_service_settings_rules: dict[str, Any] = load_service_transform_rules_from_section(
        convert_rule_config_path,
        section_key='service_settings',
    )
    active_network_role_policy: dict[str, Any] = load_network_role_policy_from_section(
        convert_rule_config_path,
        section_key='network_role',
    )
    (
        role_priority,
        internal_mgmt_role,
        external_mgmt_role,
        data_plane_roles,
        frr_advertise_roles,
        internal_network_list_roles,
    ) = resolve_network_role_config(active_network_role_policy)

    globals_def: dict[str, Any] = topology['globals']
    networks: dict[str, dict[str, Any]] = globals_def['networks']
    datacenters, auto_meshed_ebgp_transport_enabled = prepare_frr_runtime_flags(globals_def)
    generate_internal_network_list: bool = bool(
        globals_def.get('generate_internal_network_list', True)
    )

    dns_reverse_defaults, dns_domain_default = collect_dns_defaults(globals_def)

    reserved_nic_pairs: list[tuple[str, str]] = prepare_netif_reserved_pairs(globals_def)

    _input_nodes, nodes, node_map, cluster_membership = prepare_cluster_runtime_context(topology)

    (
        derived_internal_network_list,
        service_disabled_cleanup_keys,
        supply_map,
        globals_services,
    ) = prepare_service_runtime_context(
        globals_def,
        networks,
        internal_network_list_roles,
        active_service_settings_rules,
        nodes,
    )
    global_scalars: dict[str, Any] = build_global_scalars(
        globals_def,
        dynamic_internal_network_list=derived_internal_network_list,
    )

    output_hosts: list[dict[str, Any]] = []

    for node in nodes:
        host_entry, scalars, internal_mgmt_connected = initialize_node_entry_and_scalars(
            node,
            networks,
            internal_mgmt_role,
            global_scalars,
            role_priority,
            dns_domain_default,
        )

        apply_node_network_interfaces(
            host_entry,
            scalars,
            node,
            networks,
            node_map,
            reserved_nic_pairs,
            internal_mgmt_role,
            external_mgmt_role,
            data_plane_roles,
        )

        apply_node_routing_entries(
            host_entry,
            node,
            datacenters,
            cluster_membership,
            node_map,
            networks,
            nodes,
            frr_advertise_roles,
            auto_meshed_ebgp_transport_enabled,
            supply_map,
        )

        apply_node_service_scalars(
            scalars,
            node,
            globals_services,
            networks,
            supply_map,
            internal_mgmt_role,
            external_mgmt_role,
            active_service_settings_rules,
            dns_reverse_defaults,
            generate_internal_network_list,
            internal_mgmt_connected,
            derived_internal_network_list,
            service_disabled_cleanup_keys,
            global_scalars,
        )

        if scalars:
            host_entry['scalars'] = scalars

        # パススルー項目
        for key in ('vcinstances_clusterversions', 'vcinstances_virtualclusters'):
            if key in node:
                host_entry[key] = node[key]

        output_hosts.append(host_entry)

    return {'hosts': output_hosts}

def parse_arguments() -> argparse.Namespace:
    """コマンドライン引数を解析する。

    Returns:
        argparse.Namespace: 解析された引数の名前空間
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description='Generate host_vars_structured.yaml from network_topology v2',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        '-i', '--input',
        type=Path,
        default=DEFAULT_NETWORK_TOPOLOGY,
        help='Input network_topology v2 YAML file'
    )

    parser.add_argument(
        '-o', '--output',
        type=Path,
        default=DEFAULT_HOST_VARS_STRUCTURED,
        help='Output host_vars_structured YAML file'
    )
    parser.add_argument(
        '--schema-dir',
        default=None,
        help='Directory to search schema/config YAML files with highest priority',
    )

    return parser.parse_args()

def main() -> int:
    """メインエントリーポイント。

    Returns:
        int: 終了コード（0=成功, 非0=失敗）
    """

    #
    # コマンドライン引数の解析
    #
    args: argparse.Namespace = parse_arguments()

    #
    # 入力ファイル読み込み
    #
    topology: dict[str, Any] = load_yaml_mapping(args.input)

    #
    # 辞書形式に変換して出力データ生成
    #
    output: dict[str, Any] = generate_host_vars_structured(
        topology,
        args.schema_dir,
    )

    #
    # 辞書をYAML形式に変換して, 出力ファイルに書き込む
    #
    write_yaml_file(
        args.output,
        output,
        sort_keys=False,
        allow_unicode=True,
    )

    print(f"Generated: {args.output}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
