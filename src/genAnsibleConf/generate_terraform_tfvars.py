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

"""network_topology.yaml から terraform.tfvars を生成する。

このスクリプトは, network_topology.yaml のノード定義から
xcp-ng Terraform モジュール向けの terraform.tfvars を生成する。
出力対象は terraform_orchestration ロールを持つノードのみとし,
ノードの vm_params サービス設定と環境共通の xcp_ng_environment 設定を統合して
Terraform の vm_groups 形式 (group -> vm 二段マップ) で出力する。

主な機能:
- terraform_orchestration ロール保持ノードの自動抽出
- vm_group の設定駆動解決 (vm_params.vm_group 優先, vm_group_map フォールバック)
- node.interfaces から Terraform network_key への自動変換 (network_key_map 使用)
- globals.networks.role から network_roles を自動生成
- vm_group_defaults によるデフォルト値フォールバックの検証
- HCL 形式での terraform.tfvars 出力
"""

import argparse
import sys
from pathlib import Path
from typing import Any, cast

from lib.cli_defaults import (
    DEFAULT_NETWORK_TOPOLOGY,
    DEFAULT_TERRAFORM_TFVARS,
)
from lib.node_topology_utils import (
    get_globals_networks,
    get_globals_services,
    node_has_role,
)
from lib.yaml_io import load_yaml_mapping

# xcp_ng_environment.config の必須キー
# xoa_password は環境変数 TF_VAR_xoa_password で指定するため対象外
_REQUIRED_ENV_KEYS: tuple[str, ...] = (
    'xoa_url',
    'xoa_username',
    'xoa_insecure',
    'xcpng_pool_name',
    'xcpng_sr_name',
    'xcpng_template_ubuntu',
    'xcpng_template_rhel',
    'network_key_map',
)

# vm オブジェクト内のスカラーキー (出力順を固定するため順序付きで定義)
_VM_SCALAR_KEYS: tuple[str, ...] = (
    'template_type',
    'firmware',
    'resource_profile',
    'vcpus',
    'memory_mb',
    'disk_gb',
)


def load_topology(path: str) -> dict[str, Any]:
    """topology YAML ファイルを読み込んで辞書として返す。

    Args:
        path (str): topology YAML ファイルのパス

    Returns:
        dict[str, Any]: 読み込んだ topology 辞書

    Raises:
        FileNotFoundError: ファイルが存在しない場合
        ValueError: ファイル内容が dict でない場合

    Examples:
        >>> import tempfile, os, yaml
        >>> with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        ...     _ = f.write('version: 2\\nglobals:\\n  networks: {}\\n  datacenters: {}\\nnodes: []\\n')
        ...     tmp = f.name
        >>> t = load_topology(tmp)
        >>> t['version']
        2
        >>> os.unlink(tmp)
    """
    return load_yaml_mapping(path)


def collect_target_nodes(topology: dict[str, Any]) -> list[dict[str, Any]]:
    """terraform_orchestration ロールを持つノードだけを抽出する。

    Args:
        topology (dict[str, Any]): topology 辞書

    Returns:
        list[dict[str, Any]]: terraform_orchestration ロール保持ノードのリスト

    Examples:
        >>> t = {'nodes': [
        ...     {'name': 'n1', 'roles': ['terraform_orchestration']},
        ...     {'name': 'n2', 'roles': ['k8s_worker']},
        ... ]}
        >>> [n['name'] for n in collect_target_nodes(t)]
        ['n1']
    """
    nodes: list[Any] = topology.get('nodes', [])
    result: list[dict[str, Any]] = []
    for item in nodes:
        if isinstance(item, dict):
            node: dict[str, Any] = cast(dict[str, Any], item)
            if node_has_role(node, 'terraform_orchestration'):
                result.append(node)
    return result


def resolve_environment_config(topology: dict[str, Any]) -> dict[str, Any]:
    """globals.services.xcp_ng_environment.config を取得して返す。

    Args:
        topology (dict[str, Any]): topology 辞書

    Returns:
        dict[str, Any]: xcp_ng_environment.config 辞書

    Raises:
        ValueError: xcp_ng_environment.config が dict でない場合

    Examples:
        >>> t = {'globals': {'services': {'xcp_ng_environment': {'config': {'xoa_url': 'ws://x'}}}}}
        >>> resolve_environment_config(t)['xoa_url']
        'ws://x'
        >>> resolve_environment_config({})
        {}
    """
    services: dict[str, Any] = get_globals_services(topology)
    env_service: dict[str, Any] = services.get('xcp_ng_environment', {})
    config: Any = env_service.get('config', {})
    if not isinstance(config, dict):
        raise ValueError("globals.services.xcp_ng_environment.config が dict ではありません")
    return cast(dict[str, Any], config)


def validate_environment_config(env_config: dict[str, Any]) -> None:
    """環境設定の必須キーと network_key_map の内容を検証する。

    Args:
        env_config (dict[str, Any]): xcp_ng_environment.config 辞書

    Raises:
        ValueError: 必須キーが欠けている場合, または network_key_map が空の場合

    Examples:
        >>> cfg = {k: 'x' for k in _REQUIRED_ENV_KEYS}
        >>> cfg['xoa_insecure'] = True
        >>> cfg['network_key_map'] = {'mgmt_external': 'ext_mgmt'}
        >>> validate_environment_config(cfg)  # 例外なし
    """
    missing: list[str] = [k for k in _REQUIRED_ENV_KEYS if k not in env_config]
    if missing:
        raise ValueError(f"xcp_ng_environment.config に必須キーがありません: {missing}")
    network_key_map: Any = env_config.get('network_key_map', {})
    if not isinstance(network_key_map, dict) or not network_key_map:
        raise ValueError("xcp_ng_environment.config.network_key_map が未定義または空です")


def classify_vm_group(
    node: dict[str, Any],
    vm_params_config: dict[str, Any],
    vm_group_map: dict[str, str],
) -> str:
    """ノードの vm_groups グループ名を解決する。

    優先順位: vm_params.config.vm_group (明示) > vm_group_map[roles[*]] (フォールバック)

    Args:
        node (dict[str, Any]): ノード定義辞書
        vm_params_config (dict[str, Any]): node.services.vm_params.config 辞書
        vm_group_map (dict[str, str]): ロール名 -> グループ名 の対応表

    Returns:
        str: 解決されたグループ名

    Raises:
        ValueError: グループ名を解決できなかった場合

    Examples:
        >>> classify_vm_group({'name': 'n', 'roles': ['k8s_control_plane']}, {}, {'k8s_control_plane': 'k8s'})
        'k8s'
        >>> classify_vm_group({'name': 'n', 'roles': []}, {'vm_group': 'vmlinux'}, {})
        'vmlinux'
    """
    # vm_params.config.vm_group が明示的に設定されていれば最優先
    explicit_group: Any = vm_params_config.get('vm_group')
    if isinstance(explicit_group, str) and explicit_group:
        return explicit_group

    # vm_group_map でロールからグループ名を解決 (roles リストの先頭から検索)
    roles_raw: Any = node.get('roles')
    node_roles: list[str] = []
    if isinstance(roles_raw, list):
        roles_list: list[Any] = cast(list[Any], roles_raw)
        node_roles = [r for r in roles_list if isinstance(r, str)]

    for role in node_roles:
        group: str | None = vm_group_map.get(role)
        if group:
            return group

    node_name: str = node.get('name', '(unknown)')
    raise ValueError(
        f"ノード '{node_name}' の vm_groups グループ名を解決できませんでした。"
        f" vm_params.config.vm_group を明示するか,"
        f" vm_group_map にロール ({node_roles}) を追加してください。"
    )


def convert_interfaces_to_networks(
    node: dict[str, Any],
    network_key_map: dict[str, str],
) -> list[dict[str, Any]]:
    """node.interfaces から Terraform の networks リストを生成する。

    network_key_map に存在しないネットワークはエラーにする。

    Args:
        node (dict[str, Any]): ノード定義辞書
        network_key_map (dict[str, str]): topology ネットワーク名 -> Terraform ネットワークキーの対応表

    Returns:
        list[dict[str, Any]]: [{'network_key': str, 'mac_address': str | None}, ...] 形式のリスト

    Raises:
        ValueError: network_key_map に存在しないネットワークを検出した場合

    Examples:
        >>> n = {'interfaces': [
        ...     {'network': 'mgmt_external', 'mac': '00:11:22:33:44:55'},
        ...     {'network': 'mgmt_internal', 'mac': '00:11:22:33:44:66'},
        ... ]}
        >>> m = {'mgmt_external': 'ext_mgmt', 'mgmt_internal': 'gpn_mgmt'}
        >>> result = convert_interfaces_to_networks(n, m)
        >>> [(r['network_key'], r['mac_address']) for r in result]
        [('ext_mgmt', '00:11:22:33:44:55'), ('gpn_mgmt', '00:11:22:33:44:66')]
    """
    result: list[dict[str, Any]] = []
    node_name: str = str(node.get('name', '(unknown)'))
    for interface in node.get('interfaces', []):
        topology_network: Any = interface.get('network')
        if not isinstance(topology_network, str):
            continue
        terraform_key: str | None = network_key_map.get(topology_network)
        if terraform_key is None:
            raise ValueError(
                f"ノード '{node_name}' のネットワーク '{topology_network}' は"
                " xcp_ng_environment.config.network_key_map に未定義です。"
            )
        mac_raw: Any = interface.get('mac')
        mac: str | None = mac_raw if isinstance(mac_raw, str) else None
        result.append({
            'network_key': terraform_key,
            'mac_address': mac,
        })
    return result


def resolve_globals_networks(topology: dict[str, Any]) -> dict[str, Any]:
    """globals.networks を取得して返す。

    Args:
        topology (dict[str, Any]): topology 辞書

    Returns:
        dict[str, Any]: globals.networks 辞書

    Raises:
        ValueError: globals.networks が dict でない場合
    """
    return get_globals_networks(topology)


def build_network_roles(
    globals_networks: dict[str, Any],
    network_key_map: dict[str, str],
) -> dict[str, list[str]]:
    """globals.networks.role から network_roles を生成する。

    `globals.networks` 側の network 名が `network_key_map` に未登録の場合,
    その network は `network_roles` 集約結果に含めない。

    Args:
        globals_networks (dict[str, Any]): globals.networks 辞書
        network_key_map (dict[str, str]): topology ネットワーク名 -> Terraform ネットワークキー対応表

    Returns:
        dict[str, list[str]]: network role -> Terraform network key のマップ

    Examples:
        >>> g = {
        ...     'mgmt_external': {'role': 'external_control_plane_network'},
        ...     'unknown_net': {'role': 'external_control_plane_network'},
        ... }
        >>> m = {'mgmt_external': 'ext_mgmt'}
        >>> build_network_roles(g, m)
        {'external_control_plane_network': ['ext_mgmt']}
    """
    role_map: dict[str, set[str]] = {}
    for topology_network_name, network_def in globals_networks.items():
        if not isinstance(network_def, dict):
            continue
        network_def_typed: dict[str, Any] = cast(dict[str, Any], network_def)
        role_raw: Any = network_def_typed.get('role')
        if not isinstance(role_raw, str) or not role_raw:
            continue
        terraform_key: str | None = network_key_map.get(str(topology_network_name))
        if terraform_key is None:
            continue
        role_map.setdefault(role_raw, set()).add(terraform_key)
    return {role: sorted(list(keys)) for role, keys in sorted(role_map.items())}


def _resolve_vm_property(
    prop_key: str,
    vm_params_config: dict[str, Any],
    group_defaults: dict[str, Any],
) -> Any:
    """vm_params.config -> vm_group_defaults の優先順位で vm プロパティ値を解決する。

    Args:
        prop_key (str): プロパティキー名 (例: 'template_type')
        vm_params_config (dict[str, Any]): node.services.vm_params.config 辞書
        group_defaults (dict[str, Any]): vm_group_defaults の対象グループ辞書

    Returns:
        Any: 解決された値, 解決できなかった場合は None

    Examples:
        >>> _resolve_vm_property('template_type', {'template_type': 'rhel'}, {})
        'rhel'
        >>> _resolve_vm_property('template_type', {}, {'default_template_type': 'ubuntu'})
        'ubuntu'
        >>> _resolve_vm_property('template_type', {}, {}) is None
        True
    """
    if prop_key in vm_params_config:
        return vm_params_config[prop_key]
    default_key: str = f"default_{prop_key}"
    if default_key in group_defaults:
        return group_defaults[default_key]
    return None


def build_vm_groups_structure(
    target_nodes: list[dict[str, Any]],
    env_config: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    """vm_groups = {group_name: {vm_name: vm_object}} の辞書を構築する。

    vm_params.config に明示されたスカラーのみ vm_object に含める。
    networks は node.interfaces から network_key_map を用いて自動変換する。

    Args:
        target_nodes (list[dict[str, Any]]): terraform_orchestration ロール保持ノードのリスト
        env_config (dict[str, Any]): xcp_ng_environment.config 辞書

    Returns:
        dict[str, dict[str, Any]]: グループ名昇順でソートされた vm_groups 辞書

    Raises:
        ValueError: グループ名解決失敗, networks 変換結果が空, 必須プロパティ未解決の場合

    Examples:
        >>> nodes = [{'name': 'vm1', 'roles': ['terraform_orchestration', 'k8s_worker'],
        ...           'interfaces': [{'network': 'mgmt_internal', 'mac': 'aa:bb:cc:dd:ee:ff'}],
        ...           'services': {'vm_params': {'config': {
        ...               'template_type': 'ubuntu', 'firmware': 'uefi', 'resource_profile': 'k8s_worker'}}}}]
        >>> cfg = {'network_key_map': {'mgmt_internal': 'gpn_mgmt'}, 'vm_group_map': {'k8s_worker': 'k8s'},
        ...        'vm_group_defaults': {}}
        >>> result = build_vm_groups_structure(nodes, cfg)
        >>> list(result.keys())
        ['k8s']
        >>> result['k8s']['vm1']['template_type']
        'ubuntu'
    """
    network_key_map: dict[str, str] = cast(dict[str, str], env_config.get('network_key_map', {}))
    vm_group_map: dict[str, str] = cast(dict[str, str], env_config.get('vm_group_map', {}))
    vm_group_defaults_raw: Any = env_config.get('vm_group_defaults', {})
    vm_group_defaults: dict[str, Any] = (
        cast(dict[str, Any], vm_group_defaults_raw)
        if isinstance(vm_group_defaults_raw, dict)
        else {}
    )

    vm_groups: dict[str, dict[str, Any]] = {}

    for node in target_nodes:
        node_name: str = node.get('name', '(unknown)')

        # vm_params 設定を取得 (未設定時は空辞書)
        node_services: dict[str, Any] = node.get('services', {})
        vm_params_entry_raw: Any = node_services.get('vm_params', {})
        vm_params_entry: dict[str, Any] = (
            cast(dict[str, Any], vm_params_entry_raw)
            if isinstance(vm_params_entry_raw, dict)
            else {}
        )
        vm_params_config_raw: Any = vm_params_entry.get('config', {})
        vm_params_config: dict[str, Any] = (
            cast(dict[str, Any], vm_params_config_raw)
            if isinstance(vm_params_config_raw, dict)
            else {}
        )

        # グループ名を解決
        group_name: str = classify_vm_group(node, vm_params_config, vm_group_map)
        group_defaults_raw: Any = vm_group_defaults.get(group_name, {})
        group_defaults: dict[str, Any] = (
            cast(dict[str, Any], group_defaults_raw)
            if isinstance(group_defaults_raw, dict)
            else {}
        )

        # 必須プロパティの解決可否を検証
        for req_key in ('template_type', 'firmware', 'resource_profile'):
            resolved: Any = _resolve_vm_property(req_key, vm_params_config, group_defaults)
            if resolved is None:
                raise ValueError(
                    f"ノード '{node_name}' の '{req_key}' が未解決です。"
                    f" vm_params.config に明示するか,"
                    f" vm_group_defaults['{group_name}'].default_{req_key} を設定してください。"
                )

        # vm オブジェクトを組み立て (vm_params.config に明示されたスカラーのみ出力)
        vm_object: dict[str, Any] = {}
        for key in _VM_SCALAR_KEYS:
            if key in vm_params_config and key != 'vm_group':
                vm_object[key] = vm_params_config[key]

        # ネットワーク変換
        networks: list[dict[str, Any]] = convert_interfaces_to_networks(node, network_key_map)
        if not networks:
            raise ValueError(
                f"ノード '{node_name}' のネットワーク変換結果が空です。"
                f" network_key_map にノードのインターフェース ({[i.get('network') for i in node.get('interfaces', [])]})"
                f" を登録してください。"
            )
        vm_object['networks'] = networks

        # グループに追加
        if group_name not in vm_groups:
            vm_groups[group_name] = {}
        vm_groups[group_name][node_name] = vm_object

    # グループ名昇順でソートして返す
    return {g: dict(sorted(vms.items())) for g, vms in sorted(vm_groups.items())}


# ──────────────────────────────────────────────────────────────
# HCL レンダリング関数群
# ──────────────────────────────────────────────────────────────


def _hcl_str(v: str) -> str:
    """文字列を HCL 文字列リテラルに変換する。

    Args:
        v (str): 変換する文字列

    Returns:
        str: ダブルクォートで囲んだ HCL 文字列

    Examples:
        >>> _hcl_str('hello')
        '"hello"'
    """
    return f'"{v}"'


def _hcl_bool(v: bool) -> str:
    """ブール値を HCL ブールリテラルに変換する。

    Args:
        v (bool): 変換するブール値

    Returns:
        str: 'true' または 'false'

    Examples:
        >>> _hcl_bool(True)
        'true'
        >>> _hcl_bool(False)
        'false'
    """
    return "true" if v else "false"


def _hcl_scalar(v: Any) -> str:
    """Python スカラー値を HCL 形式の文字列に変換する。

    Args:
        v (Any): 変換する値 (str, bool, int, float, None)

    Returns:
        str: HCL 形式の文字列

    Examples:
        >>> _hcl_scalar('ubuntu')
        '"ubuntu"'
        >>> _hcl_scalar(True)
        'true'
        >>> _hcl_scalar(4)
        '4'
        >>> _hcl_scalar(None)
        'null'
    """
    if isinstance(v, bool):
        return _hcl_bool(v)
    if isinstance(v, str):
        return _hcl_str(v)
    if v is None:
        return "null"
    return str(v)


def _render_map_block(
    var_name: str,
    items: dict[str, str],
    indent: int = 0,
) -> list[str]:
    """キー = 値 形式の単純マップブロックを HCL 行リストで返す。

    Args:
        var_name (str): 変数名
        items (dict[str, str]): キー -> 文字列値 の辞書
        indent (int): インデントレベル (2スペース単位)

    Returns:
        list[str]: HCL 行リスト

    Examples:
        >>> _render_map_block('network_names', {'gpn_mgmt': 'GPNMgmt'})
        ['network_names = {', '  gpn_mgmt = "GPNMgmt"', '}']
    """
    pad: str = "  " * indent
    lines: list[str] = [f"{pad}{var_name} = {{"]
    for key in sorted(items.keys()):
        lines.append(f"{pad}  {key} = {_hcl_str(items[key])}")
    lines.append(f"{pad}}}")
    return lines


def _render_list_map_block(
    var_name: str,
    items: dict[str, list[str]],
    indent: int = 0,
) -> list[str]:
    """キー = [値リスト] 形式のマップブロックを HCL 行リストで返す。"""
    pad: str = "  " * indent
    lines: list[str] = [f"{pad}{var_name} = {{"]
    for key in sorted(items.keys()):
        values: list[str] = [
            _hcl_str(v) for v in items[key] if v
        ]
        rendered_values: str = ", ".join(values)
        lines.append(f"{pad}  {key} = [{rendered_values}]")
    lines.append(f"{pad}}}")
    return lines


def _render_network_options(
    network_options: dict[str, Any],
    indent: int = 0,
) -> list[str]:
    """network_options ブロックを HCL 行リストで返す。

    Args:
        network_options (dict[str, Any]): キー -> オプション辞書 の対応表
        indent (int): インデントレベル

    Returns:
        list[str]: HCL 行リスト

    Examples:
        >>> _render_network_options({})
        ['network_options = {}']
    """
    pad: str = "  " * indent
    if not network_options:
        return [f"{pad}network_options = {{}}"]
    lines: list[str] = [f"{pad}network_options = {{"]
    for key in sorted(network_options.keys()):
        opts: dict[str, Any] = network_options[key]
        lines.append(f"{pad}  {key} = {{")
        for opt_key, opt_val in sorted(opts.items()):
            lines.append(f"{pad}    {opt_key} = {_hcl_scalar(opt_val)}")
        lines.append(f"{pad}  }}")
    lines.append(f"{pad}}}")
    return lines


def _render_vm_group_defaults(
    vm_group_defaults: dict[str, Any],
    indent: int = 0,
) -> list[str]:
    """vm_group_defaults ブロックを HCL 行リストで返す。

    Args:
        vm_group_defaults (dict[str, Any]): グループ名 -> デフォルト辞書 の対応表
        indent (int): インデントレベル

    Returns:
        list[str]: HCL 行リスト (空の場合は空リスト)

    Examples:
        >>> lines = _render_vm_group_defaults({'k8s': {}})
        >>> lines[0]
        'vm_group_defaults = {'
        >>> lines[1]
        '  k8s = {}'
    """
    pad: str = "  " * indent
    lines: list[str] = [f"{pad}vm_group_defaults = {{"]
    for group_name in sorted(vm_group_defaults.keys()):
        group_def: Any = vm_group_defaults[group_name]
        if not isinstance(group_def, dict) or not group_def:
            lines.append(f"{pad}  {group_name} = {{}}")
        else:
            lines.append(f"{pad}  {group_name} = {{")
            group_def_typed: dict[str, Any] = cast(dict[str, Any], group_def)
            for k, v in sorted(group_def_typed.items()):
                lines.append(f"{pad}    {k} = {_hcl_scalar(v)}")
            lines.append(f"{pad}  }}")
    lines.append(f"{pad}}}")
    return lines


def _render_networks_list(
    networks: list[dict[str, Any]],
    indent: int = 0,
) -> list[str]:
    """networks = [...] ブロックを HCL 行リストで返す。

    Args:
        networks (list[dict[str, Any]]): [{'network_key': str, 'mac_address': str|None}, ...] 形式
        indent (int): インデントレベル

    Returns:
        list[str]: HCL 行リスト

    Examples:
        >>> lines = _render_networks_list([{'network_key': 'ext_mgmt', 'mac_address': 'aa:bb:cc:dd:ee:ff'}])
        >>> lines[0]
        'networks = ['
        >>> 'network_key = "ext_mgmt"' in lines[1]
        True
    """
    pad: str = "  " * indent
    lines: list[str] = [f"{pad}networks = ["]
    for i, net in enumerate(networks):
        comma: str = "," if i < len(networks) - 1 else ""
        mac_val: str = _hcl_scalar(net.get('mac_address'))
        lines.append(
            f'{pad}  {{ network_key = {_hcl_str(net["network_key"])}, mac_address = {mac_val} }}{comma}'
        )
    lines.append(f"{pad}]")
    return lines


def _render_vm_object(
    vm_name: str,
    vm_obj: dict[str, Any],
    indent: int = 0,
) -> list[str]:
    """1 VM のブロックを HCL 行リストで返す。

    Args:
        vm_name (str): VM 名
        vm_obj (dict[str, Any]): vm オブジェクト辞書
        indent (int): インデントレベル

    Returns:
        list[str]: HCL 行リスト

    Examples:
        >>> obj = {'template_type': 'ubuntu', 'firmware': 'uefi',
        ...        'networks': [{'network_key': 'ext_mgmt', 'mac_address': None}]}
        >>> lines = _render_vm_object('router', obj)
        >>> lines[0]
        'router = {'
        >>> lines[-1]
        '}'
    """
    pad: str = "  " * indent
    lines: list[str] = [f"{pad}{vm_name} = {{"]
    for key in _VM_SCALAR_KEYS:
        if key in vm_obj:
            lines.append(f"{pad}  {key} = {_hcl_scalar(vm_obj[key])}")
    networks: list[dict[str, Any]] = vm_obj.get('networks', [])
    lines.extend(_render_networks_list(networks, indent + 1))
    lines.append(f"{pad}}}")
    return lines


def _render_vm_groups(
    vm_groups: dict[str, dict[str, Any]],
    indent: int = 0,
) -> list[str]:
    """vm_groups ブロック全体を HCL 行リストで返す。

    Args:
        vm_groups (dict[str, dict[str, Any]]): {group_name: {vm_name: vm_object}} 形式
        indent (int): インデントレベル

    Returns:
        list[str]: HCL 行リスト

    Examples:
        >>> lines = _render_vm_groups({'k8s': {}})
        >>> lines[0]
        'vm_groups = {'
        >>> lines[-1]
        '}'
    """
    pad: str = "  " * indent
    lines: list[str] = [f"{pad}vm_groups = {{"]
    for group_name in sorted(vm_groups.keys()):
        vms: dict[str, Any] = vm_groups[group_name]
        lines.append(f"{pad}  {group_name} = {{")
        for vm_name in sorted(vms.keys()):
            vm_obj: dict[str, Any] = vms[vm_name]
            lines.extend(_render_vm_object(vm_name, vm_obj, indent + 2))
        lines.append(f"{pad}  }}")
    lines.append(f"{pad}}}")
    return lines


def render_tfvars(
    env_config: dict[str, Any],
    vm_groups: dict[str, dict[str, Any]],
    network_roles: dict[str, list[str]],
) -> str:
    """Terraform tfvars 文字列を生成して返す。

    Args:
        env_config (dict[str, Any]): xcp_ng_environment.config 辞書
        vm_groups (dict[str, dict[str, Any]]): {group_name: {vm_name: vm_object}} 形式

    Returns:
        str: terraform.tfvars 形式の文字列 (末尾改行あり)

    Examples:
        >>> cfg = {k: 'x' for k in _REQUIRED_ENV_KEYS}
        >>> cfg['xoa_insecure'] = True
        >>> cfg['network_key_map'] = {'mgmt_external': 'ext_mgmt'}
        >>> content = render_tfvars(cfg, {}, {'external_control_plane_network': ['ext_mgmt']})
        >>> 'xoa_url' in content
        True
        >>> 'vm_groups = {' in content
        True
    """
    lines: list[str] = []

    lines.append("############################################")
    lines.append("# XenOrchestra 接続情報")
    lines.append("############################################")
    lines.append(f'xoa_url      = {_hcl_str(str(env_config["xoa_url"]))}')
    lines.append(f'xoa_username = {_hcl_str(str(env_config["xoa_username"]))}')
    lines.append(f'xoa_insecure = {_hcl_bool(bool(env_config["xoa_insecure"]))}')
    lines.append("# xoa_password は TF_VAR_xoa_password 環境変数で指定すること")
    lines.append("")

    lines.append("##############################################")
    lines.append("# 使用するXCP-ng プール名/ストレージリポジトリ")
    lines.append("##############################################")
    lines.append(f'xcpng_pool_name = {_hcl_str(str(env_config["xcpng_pool_name"]))}')
    lines.append(f'xcpng_sr_name   = {_hcl_str(str(env_config["xcpng_sr_name"]))}')
    lines.append("")

    lines.append("########################################################")
    lines.append("# VM生成テンプレート")
    lines.append("########################################################")
    lines.append(f'xcpng_template_ubuntu = {_hcl_str(str(env_config["xcpng_template_ubuntu"]))}')
    lines.append(f'xcpng_template_rhel   = {_hcl_str(str(env_config["xcpng_template_rhel"]))}')
    lines.append("")

    # network_names
    network_names_raw: Any = env_config.get('network_names', {})
    network_names: dict[str, str] = (
        cast(dict[str, str], network_names_raw)
        if isinstance(network_names_raw, dict) and network_names_raw
        else {}
    )
    if network_names:
        lines.append("########################################################")
        lines.append("# ネットワーク名定義")
        lines.append("########################################################")
        lines.extend(_render_map_block('network_names', network_names))
        lines.append("")

    if network_roles:
        lines.append("########################################################")
        lines.append("# ネットワーク役割定義")
        lines.append("########################################################")
        lines.extend(_render_list_map_block('network_roles', network_roles))
        lines.append("")

    # network_options
    network_options_raw: Any = env_config.get('network_options', {})
    network_options: dict[str, Any] = (
        cast(dict[str, Any], network_options_raw)
        if isinstance(network_options_raw, dict)
        else {}
    )
    lines.extend(_render_network_options(network_options))
    lines.append("")

    # デフォルトリソース割り当て
    has_defaults: bool = any(
        k in env_config for k in ('xcpng_vm_disk_gb', 'xcpng_vm_vcpus', 'xcpng_vm_mem_mb')
    )
    if has_defaults:
        lines.append("############################################")
        lines.append("# デフォルトのリソース割り当て量")
        lines.append("############################################")
        if 'xcpng_vm_disk_gb' in env_config:
            lines.append(f'xcpng_vm_disk_gb = {env_config["xcpng_vm_disk_gb"]}')
        if 'xcpng_vm_vcpus' in env_config:
            lines.append(f'xcpng_vm_vcpus   = {env_config["xcpng_vm_vcpus"]}')
        if 'xcpng_vm_mem_mb' in env_config:
            lines.append(f'xcpng_vm_mem_mb  = {env_config["xcpng_vm_mem_mb"]}')
        lines.append("")

    # vm_group_defaults
    vm_group_defaults_raw: Any = env_config.get('vm_group_defaults', {})
    vm_group_defaults: dict[str, Any] = (
        cast(dict[str, Any], vm_group_defaults_raw)
        if isinstance(vm_group_defaults_raw, dict) and vm_group_defaults_raw
        else {}
    )
    if vm_group_defaults:
        lines.append("####################################################")
        lines.append("# VMグループ既定値")
        lines.append("####################################################")
        lines.extend(_render_vm_group_defaults(vm_group_defaults))
        lines.append("")

    # vm_groups
    lines.append("####################################################")
    lines.append("# VMグループ定義")
    lines.append("####################################################")
    lines.extend(_render_vm_groups(vm_groups))
    lines.append("")

    return "\n".join(lines)


def main() -> int:
    """メイン関数。

    Returns:
        int: 終了コード (0: 成功, 1: 失敗)
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="network_topology.yaml から terraform.tfvars を生成する。",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        '-t', '--topology',
        default=DEFAULT_NETWORK_TOPOLOGY,
        help="network_topology.yaml のパス",
    )
    parser.add_argument(
        '-o', '--output',
        default=DEFAULT_TERRAFORM_TFVARS,
        help="出力する terraform.tfvars のパス",
    )
    parser.add_argument(
        '-n', '--dry-run',
        action='store_true',
        help="ファイルに書き込まず標準出力に表示する",
    )
    parser.add_argument(
        '-s', '--strict',
        action='store_true',
        help="警告をエラーとして扱う",
    )
    args: argparse.Namespace = parser.parse_args()

    try:
        topology: dict[str, Any] = load_topology(args.topology)
        env_config: dict[str, Any] = resolve_environment_config(topology)
        globals_networks: dict[str, Any] = resolve_globals_networks(topology)
        validate_environment_config(env_config)
        network_key_map: dict[str, str] = cast(dict[str, str], env_config.get('network_key_map', {}))
        network_roles: dict[str, list[str]] = build_network_roles(globals_networks, network_key_map)

        target_nodes: list[dict[str, Any]] = collect_target_nodes(topology)
        if not target_nodes:
            print(
                "警告: terraform_orchestration ロールを持つノードが見つかりませんでした。",
                file=sys.stderr,
            )
            if args.strict:
                return 1

        vm_groups: dict[str, dict[str, Any]] = build_vm_groups_structure(target_nodes, env_config)
        content: str = render_tfvars(env_config, vm_groups, network_roles)

        if args.dry_run:
            print(content)
        else:
            output_path: Path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(content, encoding='utf-8')
            print(f"生成完了: {args.output}", file=sys.stderr)

    except (FileNotFoundError, ValueError, KeyError) as exc:
        print(f"エラー: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
