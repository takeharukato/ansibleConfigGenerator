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
"""globals 直下スカラーと補助パラメータ処理を提供するモジュールである。"""

from __future__ import annotations

import json
from typing import Any, cast


def _dedupe_preserve_order(values: list[Any]) -> list[Any]:
    """リストの重複を順序維持で除去する。"""
    seen: set[str] = set()
    out: list[Any] = []
    for value in values:
        marker: str = json.dumps(value, sort_keys=True, ensure_ascii=False)
        if marker in seen:
            continue
        seen.add(marker)
        out.append(value)
    return out


def collect_dns_defaults(globals_def: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
    """globals.services.dns-server から reverse DNS と dns_domain の既定値を抽出する。

    Args:
        globals_def (dict[str, Any]): 入力トポロジーの globals セクションである。

    Returns:
        tuple[dict[str, Any], str | None]:
            reverse DNS 関連既定値辞書と dns_domain 既定値である。

    Examples:
        >>> collect_dns_defaults({})
        ({}, None)
    """
    dns_reverse_defaults: dict[str, Any] = {}
    globals_services_raw: Any = globals_def.get('services', {})
    globals_services_map: dict[str, Any] = (
        cast(dict[str, Any], globals_services_raw)
        if isinstance(globals_services_raw, dict)
        else {}
    )
    dns_server_entry_raw: Any = globals_services_map.get('dns-server', {})
    dns_server_entry: dict[str, Any] = (
        cast(dict[str, Any], dns_server_entry_raw)
        if isinstance(dns_server_entry_raw, dict)
        else {}
    )
    dns_server_config_raw: Any = dns_server_entry.get('config', {})
    dns_server_config: dict[str, Any] = (
        cast(dict[str, Any], dns_server_config_raw)
        if isinstance(dns_server_config_raw, dict)
        else {}
    )
    for key in (
        'dns_server_ipv4_address',
        'dns_server_ipv6_address',
        'dns_ipv4_reverse',
        'dns_ipv6_reverse',
    ):
        if key in dns_server_config:
            dns_reverse_defaults[key] = dns_server_config[key]
    dns_domain_default_raw: Any = dns_server_config.get('dns_domain')
    dns_domain_default: str | None = None
    if isinstance(dns_domain_default_raw, str):
        dns_domain_default = dns_domain_default_raw.strip() or None
    return dns_reverse_defaults, dns_domain_default


def prepare_netif_reserved_pairs(globals_def: dict[str, Any]) -> list[tuple[str, str]]:
    """NIC/netif 処理で利用する予約 NIC ペアを準備する。

    Args:
        globals_def (dict[str, Any]): 入力トポロジーの globals セクションである。

    Returns:
        list[tuple[str, str]]: 予約NICペア一覧である。

    Examples:
        >>> prepare_netif_reserved_pairs({})
        []
    """
    reserved_nic_pairs_input: list[list[str]] = globals_def.get('reserved_nic_pairs', [])
    return [(pair[0], pair[1]) for pair in reserved_nic_pairs_input]


def build_global_scalars(
    globals_def: dict[str, Any],
    dynamic_internal_network_list: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """globals から全ホスト共通スカラー既定値を構築する。

    Args:
        globals_def (dict[str, Any]): globals 定義である。
        dynamic_internal_network_list (list[dict[str, str]] | None):
            ネットワーク定義から動的導出した internal_network_list である。

    Returns:
        dict[str, Any]: グローバルスカラー辞書である。

    Examples:
        >>> build_global_scalars({"scalars": {"a": 1}})
        {'a': 1}
    """
    out: dict[str, Any] = {}

    global_scalars_raw: Any = globals_def.get('scalars', {})
    if isinstance(global_scalars_raw, dict):
        out.update(cast(dict[str, Any], global_scalars_raw))

    dynamic_list: list[dict[str, str]] = dynamic_internal_network_list or []
    static_list_raw: Any = out.get('internal_network_list', [])
    static_list: list[dict[str, str]] = []
    if isinstance(static_list_raw, list):
        static_list_items: list[Any] = cast(list[Any], static_list_raw)
        static_list = [
            cast(dict[str, str], entry)
            for entry in static_list_items
            if isinstance(entry, dict)
        ]

    if static_list or dynamic_list:
        merged_internal_network_list: list[dict[str, str]] = cast(
            list[dict[str, str]],
            _dedupe_preserve_order(static_list + dynamic_list),
        )
        out['internal_network_list'] = merged_internal_network_list

    return out
