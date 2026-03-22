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
"""サービス変換ルールの読込, 検証, 適用を提供するモジュールである。"""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

from .yaml_io import load_yaml_mapping


def load_service_transform_rules(path: str | Path) -> dict[str, Any]:
    """サービス変換ルール YAML を読み込む。

    Args:
        path (str | Path): ルールファイルのパスである。

    Returns:
        dict[str, Any]: 検証済みルール辞書である。

    Raises:
        ValueError: ルール構造が不正な場合に送出する。

    Examples:
        >>> isinstance(load_service_transform_rules_from_section("src/prototype/convert-rule-config.yaml"), dict)
        True
    """
    return load_service_transform_rules_from_section(path)


def load_service_transform_rules_from_section(
    path: str | Path,
    section_key: str = "service_transform",
) -> dict[str, Any]:
    """統合設定ファイルから指定セクションのサービス変換ルールを読み込む。

    Args:
        path (str | Path): 統合設定ファイルのパスである。
        section_key (str): 読み込むセクション名である。

    Returns:
        dict[str, Any]: 検証済みルール辞書である。

    Raises:
        ValueError: セクション値がマッピングでない場合, または検証に失敗した場合に送出する。

    Examples:
        >>> rules = load_service_transform_rules_from_section("src/prototype/convert-rule-config.yaml")
        >>> isinstance(rules, dict)
        True
    """
    root_rules: dict[str, Any] = load_yaml_mapping(path)
    section_raw: Any = root_rules.get(section_key, root_rules)
    if not isinstance(section_raw, dict):
        raise ValueError(f"service transform rules: '{section_key}' must be a mapping")
    rules: dict[str, Any] = cast(dict[str, Any], section_raw)
    validate_service_transform_rules(rules)
    return rules

def validate_service_transform_rules(rules: dict[str, Any]) -> None:
    """ルール辞書の構造を検証する。

    Args:
        rules (dict[str, Any]): 検証対象のルール辞書である。

    Raises:
        ValueError: サービス定義, key_map, fixed_values, config_keys などの型要件に違反した場合に送出する。

    Examples:
        >>> validate_service_transform_rules({"services": {}})
    """
    skip_services_raw: Any = rules.get("skip_config_scalar_services", [])
    if not isinstance(skip_services_raw, list):
        raise ValueError("service transform rules: 'skip_config_scalar_services' must be list")
    skip_service_name: Any
    for skip_service_name in cast(list[Any], skip_services_raw):
        if not isinstance(skip_service_name, str):
            raise ValueError(
                "service transform rules: 'skip_config_scalar_services' items must be strings"
            )

    services_raw: Any = rules.get("services", {})
    if not isinstance(services_raw, dict):
        raise ValueError("service transform rules: 'services' must be a mapping")

    services_map: dict[str, Any] = cast(dict[str, Any], services_raw)
    service_name: str
    service_rule_raw: Any
    for service_name, service_rule_raw in services_map.items():
        if not isinstance(service_rule_raw, dict):
            raise ValueError(f"service transform rules: '{service_name}' rule must be mapping")

        service_rule: dict[str, Any] = cast(dict[str, Any], service_rule_raw)

        disabled_service_cleanup_keys_raw: Any = service_rule.get("disabled_service_cleanup_keys", [])
        if not isinstance(disabled_service_cleanup_keys_raw, list):
            raise ValueError(f"service transform rules: '{service_name}.disabled_service_cleanup_keys' must be list")

        scoped_item: Any
        for scoped_item in cast(list[Any], disabled_service_cleanup_keys_raw):
            if not isinstance(scoped_item, str):
                raise ValueError(
                    f"service transform rules: '{service_name}.disabled_service_cleanup_keys' item must be string"
                )

        key_map_raw: Any = service_rule.get("key_map", {})
        if not isinstance(key_map_raw, dict):
            raise ValueError(f"service transform rules: '{service_name}.key_map' must be mapping")
        key_map: dict[Any, Any] = cast(dict[Any, Any], key_map_raw)
        src_key: Any
        dst_key: Any
        for src_key, dst_key in key_map.items():
            if not isinstance(src_key, str) or not isinstance(dst_key, str):
                raise ValueError(
                    f"service transform rules: '{service_name}.key_map' key/value must be string"
                )

        fixed_values_raw: Any = service_rule.get("fixed_values", {})
        if not isinstance(fixed_values_raw, dict):
            raise ValueError(f"service transform rules: '{service_name}.fixed_values' must be mapping")
        fixed_values: dict[Any, Any] = cast(dict[Any, Any], fixed_values_raw)
        fixed_key: Any
        for fixed_key in fixed_values.keys():
            if not isinstance(fixed_key, str):
                raise ValueError(
                    f"service transform rules: '{service_name}.fixed_values' key must be string"
                )

        config_keys_raw: Any = service_rule.get("config_keys", [])
        if not isinstance(config_keys_raw, list):
            raise ValueError(f"service transform rules: '{service_name}.config_keys' must be list")
        config_key: Any
        for config_key in cast(list[Any], config_keys_raw):
            if not isinstance(config_key, str):
                raise ValueError(
                    f"service transform rules: '{service_name}.config_keys' item must be string"
                )

        passthrough_raw: Any = service_rule.get("passthrough_all_config", False)
        if not isinstance(passthrough_raw, bool):
            raise ValueError(
                f"service transform rules: '{service_name}.passthrough_all_config' must be bool"
            )

        enabled_flag_raw: Any = service_rule.get("enabled_flag")
        if enabled_flag_raw is not None and not isinstance(enabled_flag_raw, str):
            raise ValueError(f"service transform rules: '{service_name}.enabled_flag' must be string")


def get_service_disabled_cleanup_keys(rules: dict[str, Any]) -> dict[str, set[str]]:
    """ルールからサービス別のスカラーキー集合を返す。

    Args:
        rules (dict[str, Any]): サービス変換ルールである。

    Returns:
        dict[str, set[str]]: サービス名ごとのスカラーキー集合である。

    Examples:
        >>> get_service_disabled_cleanup_keys({"services": {"svc": {"disabled_service_cleanup_keys": ["a"]}}})["svc"]
        {'a'}
    """
    services_map: dict[str, Any] = cast(dict[str, Any], rules.get("services", {}))
    out: dict[str, set[str]] = {}

    service_name: str
    service_rule_raw: Any
    for service_name, service_rule_raw in services_map.items():
        service_rule: dict[str, Any] = cast(dict[str, Any], service_rule_raw)
        disabled_service_cleanup_keys_raw: list[Any] = cast(list[Any], service_rule.get("disabled_service_cleanup_keys", []))
        out[service_name] = {item for item in disabled_service_cleanup_keys_raw if isinstance(item, str)}

    return out


def map_service_config_to_scalars(
    service_name: str,
    service_entry: dict[str, Any],
    rules: dict[str, Any],
) -> dict[str, Any]:
    """サービス設定をルールに従ってスカラーへ変換する。

    Args:
        service_name (str): 変換対象サービス名である。
        service_entry (dict[str, Any]): サービス設定エントリである。
        rules (dict[str, Any]): 変換ルール辞書である。

    Returns:
        dict[str, Any]: 変換結果のスカラー辞書である。

    Examples:
        >>> rules = {"services": {"svc": {"enabled_flag": "svc_enabled", "key_map": {"a": "b"}, "fixed_values": {"const_key": 10}, "config_keys": [], "passthrough_all_config": False, "disabled_service_cleanup_keys": []}}}
        >>> map_service_config_to_scalars("svc", {"config": {"a": 1}}, rules)
        {'svc_enabled': True, 'b': 1, 'const_key': 10}
    """
    services_map: dict[str, Any] = cast(dict[str, Any], rules.get("services", {}))
    service_rule_raw: Any = services_map.get(service_name)
    if not isinstance(service_rule_raw, dict):
        return {}

    service_rule: dict[str, Any] = cast(dict[str, Any], service_rule_raw)
    out: dict[str, Any] = {}

    config_raw: Any = service_entry.get("config", {})
    config: dict[str, Any] = cast(dict[str, Any], config_raw) if isinstance(config_raw, dict) else {}

    enabled_flag_raw: Any = service_rule.get("enabled_flag")
    if isinstance(enabled_flag_raw, str) and enabled_flag_raw:
        out[enabled_flag_raw] = True

    key_map_raw: Any = service_rule.get("key_map", {})
    key_map: dict[str, str] = {
        src: dst
        for src, dst in cast(dict[Any, Any], key_map_raw).items()
        if isinstance(src, str) and isinstance(dst, str)
    }

    src_key: str
    dst_key: str
    for src_key, dst_key in key_map.items():
        if src_key in config:
            out[dst_key] = config[src_key]

    passthrough_raw: Any = service_rule.get("passthrough_all_config", False)
    passthrough_all: bool = bool(passthrough_raw)
    if passthrough_all:
        key: str
        value: Any
        for key, value in config.items():
            if key not in key_map:
                out[key] = value
        return out

    config_keys_raw: Any = service_rule.get("config_keys", [])
    config_keys: list[str] = [
        item
        for item in cast(list[Any], config_keys_raw)
        if isinstance(item, str)
    ]
    config_key: str
    for config_key in config_keys:
        if config_key in config:
            out[config_key] = config[config_key]

    fixed_values_raw: Any = service_rule.get("fixed_values", {})
    fixed_values: dict[str, Any] = {
        key: value
        for key, value in cast(dict[Any, Any], fixed_values_raw).items()
        if isinstance(key, str)
    }
    if fixed_values:
        out.update(fixed_values)

    return out
