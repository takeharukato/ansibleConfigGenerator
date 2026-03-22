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
"""service_rules の単体テスト。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.genAnsibleConf.lib.service_rules import (
    get_service_disabled_cleanup_keys,
    load_service_transform_rules_from_section,
    map_service_config_to_scalars,
)


def _rules_path() -> Path:
    """convert-rule-config.yaml の絶対パスを返す。"""
    return Path(__file__).resolve().parents[2] / "src" / "genAnsibleConf" / "convert-rule-config.yaml"


def test_load_service_transform_rules_reads_services() -> None:
    """ルールファイル読込後に services マップを取得できる。"""
    rules: dict[str, Any] = load_service_transform_rules_from_section(
        _rules_path(),
        section_key="service_settings",
    )

    services: dict[str, Any] = rules["services"]
    assert "gitlab" in services
    assert "terraform" in services


def test_map_service_config_to_scalars_gitlab_applies_key_map_and_passthrough() -> None:
    """gitlab で key_map と passthrough_all_config が適用される。"""
    rules: dict[str, Any] = load_service_transform_rules_from_section(
        _rules_path(),
        section_key="service_settings",
    )
    service_entry: dict[str, Any] = {
        "config": {
            "hostname": "gitlab.example.local",
            "gitlab_backup_rotation": 3,
        }
    }

    actual: dict[str, Any] = map_service_config_to_scalars("gitlab", service_entry, rules)

    assert actual["gitlab_hostname"] == "gitlab.example.local"
    assert actual["gitlab_backup_rotation"] == 3


def test_map_service_config_to_scalars_terraform_sets_enabled_flag() -> None:
    """terraform で enabled_flag が出力される。"""
    rules: dict[str, Any] = load_service_transform_rules_from_section(
        _rules_path(),
        section_key="service_settings",
    )
    service_entry: dict[str, Any] = {"config": {}}

    actual: dict[str, Any] = map_service_config_to_scalars("terraform", service_entry, rules)

    assert actual == {"terraform_enabled": True}


def test_get_service_disabled_cleanup_keys_includes_terraform_enabled() -> None:
    """ルール由来の disabled_service_cleanup_keys を取得できる。"""
    rules: dict[str, Any] = load_service_transform_rules_from_section(
        _rules_path(),
        section_key="service_settings",
    )

    scoped: dict[str, set[str]] = get_service_disabled_cleanup_keys(rules)

    assert "terraform" in scoped
    assert "terraform_enabled" in scoped["terraform"]


def test_map_service_config_to_scalars_applies_fixed_values() -> None:
    """fixed_values で固定値を追加できる。"""
    rules: dict[str, Any] = {
        "services": {
            "svc": {
                "disabled_service_cleanup_keys": ["mode", "const_int"],
                "key_map": {"mode_src": "mode"},
                "fixed_values": {
                    "const_int": 7,
                    "const_bool": True,
                },
                "config_keys": [],
                "passthrough_all_config": False,
            }
        }
    }
    service_entry: dict[str, Any] = {
        "config": {
            "mode_src": "manual",
        }
    }

    actual: dict[str, Any] = map_service_config_to_scalars("svc", service_entry, rules)

    assert actual == {
        "mode": "manual",
        "const_int": 7,
        "const_bool": True,
    }
