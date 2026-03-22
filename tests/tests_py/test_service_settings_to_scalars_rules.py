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
"""service_settings_to_scalars ルール適用の単体テスト。"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable

from src.genAnsibleConf.lib.service_processing import service_settings_to_scalars
from src.genAnsibleConf.lib.service_rules import load_service_transform_rules_from_section

PROTOTYPE_DIR: Path = Path(__file__).resolve().parents[2] / "src" / "genAnsibleConf"
if str(PROTOTYPE_DIR) not in sys.path:
    sys.path.insert(0, str(PROTOTYPE_DIR))

ServiceSettingsToScalarsType = Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]]
service_settings_to_scalars_typed: ServiceSettingsToScalarsType = service_settings_to_scalars


def _rules_path() -> Path:
    """convert-rule-config.yaml の絶対パスを返す。"""
    return (
        Path(__file__).resolve().parents[2]
        / "src"
        / "genAnsibleConf"
        / "convert-rule-config.yaml"
    )


def test_load_service_settings_rules_contains_cilium_and_terraform() -> None:
    """変換ルールに主要サービス定義が含まれる。"""
    rules: dict[str, Any] = load_service_transform_rules_from_section(
        _rules_path(),
        section_key="service_settings",
    )

    services: dict[str, Any] = rules["services"]
    assert "cilium" in services
    assert "terraform" in services


def test_service_settings_to_scalars_uses_yaml_rules() -> None:
    """YAMLルールに従い enabled_flag と key_map を変換できる。"""
    rules: dict[str, Any] = load_service_transform_rules_from_section(
        _rules_path(),
        section_key="service_settings",
    )
    merged_services: dict[str, Any] = {
        "cilium": {
            "config": {
                "version": "1.16.0",
                "shared_ca_enabled": True,
            }
        },
        "hubble_cli": {},
        "terraform": {"config": {}},
    }

    actual: dict[str, Any] = service_settings_to_scalars_typed(merged_services, rules)

    assert actual["k8s_cilium_version"] == "1.16.0"
    assert actual["k8s_cilium_shared_ca_enabled"] is True
    assert actual["k8s_hubble_cli_enabled"] is True
    assert actual["terraform_enabled"] is True
